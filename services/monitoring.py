from datetime import datetime
from services.storage import save_state
import uuid

def log_activity(agent: str, action: str, details: dict):
    """Log agent activity"""
    activity = {
        "timestamp": datetime.utcnow().isoformat(),
        "agent": agent,
        "action": action,
        "details": details
    }
    
    # In a real implementation, this would go to a monitoring system
    print(f"Activity: {activity}")

def get_activities(task_id: str = None):
    """Get activities for a specific task or all"""
    # Simplified implementation - would query monitoring system
    return []