import json
import os
from pathlib import Path

DATA_DIR = Path("data")

def save_state(task_id: str, key: str, value: dict):
    """Save task state to disk"""
    task_dir = DATA_DIR / task_id
    task_dir.mkdir(parents=True, exist_ok=True)
    
    with open(task_dir / f"{key}.json", "w") as f:
        json.dump(value, f)

def get_state(task_id: str, key: str = None):
    """Get task state from disk"""
    task_dir = DATA_DIR / task_id
    
    if key:
        file_path = task_dir / f"{key}.json"
        if not file_path.exists():
            return None
        with open(file_path) as f:
            return json.load(f)
    else:
        state = {}
        for file in task_dir.glob("*.json"):
            with open(file) as f:
                state[file.stem] = json.load(f)
        return state if state else None