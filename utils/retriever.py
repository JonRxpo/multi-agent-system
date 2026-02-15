import os
from typing import List, Dict
import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
from pathlib import Path


class DocumentRetriever:
    
    def __init__(self, data_dir: str = "data", collection_name: str = "documents"):
        self.data_dir = Path(data_dir)
        self.collection_name = collection_name
        
        print("Loading embedding model...")
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        
        self.client = chromadb.Client(Settings(
            persist_directory="./chroma_db",
            anonymized_telemetry=False
        ))
        
        self.collection = self.client.get_or_create_collection(
            name=self.collection_name,
            metadata={"description": "Document collection for agentic assistant"}
        )
        
    def load_documents(self) -> None:
        print(f"Loading documents from {self.data_dir}...")
        
        if self.collection.count() > 0:
            print(f"Collection already has {self.collection.count()} documents. Skipping ingestion.")
            return
        
        documents = []
        metadatas = []
        ids = []
        
        for file_path in self.data_dir.glob("**/*"):
            if file_path.is_file() and file_path.suffix in ['.txt', '.md']:
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    chunks = self._chunk_document(content, file_path.name)
                    
                    for idx, chunk in enumerate(chunks):
                        documents.append(chunk['text'])
                        metadatas.append({
                            'source': chunk['source'],
                            'chunk_id': idx,
                            'total_chunks': len(chunks)
                        })
                        ids.append(f"{file_path.stem}_{idx}")
                    
                    print(f"  ✓ Loaded {file_path.name} ({len(chunks)} chunks)")
                
                except Exception as e:
                    print(f"  ✗ Error loading {file_path.name}: {e}")
        
        if documents:
            print(f"Adding {len(documents)} document chunks to vector store...")
            
            embeddings = self.embedding_model.encode(documents).tolist()
            
            self.collection.add(
                documents=documents,
                embeddings=embeddings,
                metadatas=metadatas,
                ids=ids
            )
            
            print(f"✓ Successfully indexed {len(documents)} chunks from {len(set(m['source'] for m in metadatas))} documents")
        else:
            print("⚠ No documents found to index")
    
    def _chunk_document(self, content: str, source: str, chunk_size: int = 1000) -> List[Dict]:
        paragraphs = [p.strip() for p in content.split('\n\n') if p.strip()]
        
        chunks = []
        current_chunk = ""
        
        for para in paragraphs:
            if len(current_chunk) + len(para) > chunk_size and current_chunk:
                chunks.append({
                    'text': current_chunk.strip(),
                    'source': source
                })
                current_chunk = para
            else:
                current_chunk += "\n\n" + para if current_chunk else para
        
        if current_chunk:
            chunks.append({
                'text': current_chunk.strip(),
                'source': source
            })
        
        return chunks if chunks else [{'text': content, 'source': source}]
    
    def search(self, query: str, top_k: int = 5) -> List[Dict]:
        query_embedding = self.embedding_model.encode(query).tolist()
        
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k
        )
        
        documents = []
        if results['documents']:
            for idx in range(len(results['documents'][0])):
                documents.append({
                    'text': results['documents'][0][idx],
                    'source': results['metadatas'][0][idx]['source'],
                    'chunk_id': results['metadatas'][0][idx]['chunk_id'],
                    'distance': results['distances'][0][idx] if 'distances' in results else None
                })
        
        return documents
    
    def get_stats(self) -> Dict:
        count = self.collection.count()
        
        if count > 0:
            all_metadata = self.collection.get()['metadatas']
            sources = set(m['source'] for m in all_metadata)
        else:
            sources = set()
        
        return {
            'total_chunks': count,
            'total_documents': len(sources),
            'sources': list(sources)
        }


_retriever = None

def get_retriever() -> DocumentRetriever:
    global _retriever
    if _retriever is None:
        _retriever = DocumentRetriever()
        _retriever.load_documents()
    return _retriever