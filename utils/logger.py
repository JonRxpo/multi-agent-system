import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any

class WorkflowLogger:
    def __init__(self, log_dir: str = "logs"):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)
    
    def log_workflow(self, state: Dict[str, Any], duration: float, status: str):
        timestamp = datetime.now().isoformat()
        log_entry = {
            'timestamp': timestamp,
            'duration': duration,
            'status': status,
            'task': state.get('task', ''),
            'agent_trace': state.get('agent_trace', []),
            'citations_count': len(state.get('citations', [])),
            'output_length': len(state.get('final_output', '')),
            'verification': state.get('verification_result', {})
        }
        
        log_file = self.log_dir / f"workflow_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(log_file, 'w') as f:
            json.dump(log_entry, f, indent=2)
        
        return log_file

_logger = None

def get_logger() -> WorkflowLogger:
    global _logger
    if _logger is None:
        _logger = WorkflowLogger()
    return _logger