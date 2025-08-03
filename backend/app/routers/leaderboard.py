import json
import os
from datetime import datetime
from fastapi import APIRouter, HTTPException
from typing import List, Dict, Optional

router = APIRouter(
    prefix="/leaderboard",
    tags=["leaderboard"]
)

# Get the absolute path to logs.json relative to the backend directory
LOGS_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "logs.json")
print(LOGS_FILE)

@router.get("")
def get_leaderboard(task: Optional[str] = None):
    """
    Get leaderboard of models by average latency.
    
    Args:
        task: Optional query parameter to filter by task type
        
    Returns:
        List of models with their average latency and number of runs
    """
    try:
        # Check if logs file exists
        if not os.path.exists(LOGS_FILE):
            raise HTTPException(status_code=500, detail="Logs file not found")
            
        # Read logs
        with open(LOGS_FILE, 'r') as f:
            logs = json.load(f)
            
        # Filter by task if specified
        if task:
            logs = [log for log in logs if log["task"] == task]
            
        # Group by model and calculate statistics
        model_stats = {}
        for log in logs:
            model = log["model"]
            latency = log["latency"]
            
            if model not in model_stats:
                model_stats[model] = {
                    "model": model,
                    "total_latency": 0,
                    "runs": 0
                }
                
            model_stats[model]["total_latency"] += latency
            model_stats[model]["runs"] += 1
            
        # Calculate average latency and prepare response
        leaderboard = []
        for model, stats in model_stats.items():
            avg_latency = stats["total_latency"] / stats["runs"]
            leaderboard.append({
                "model": model,
                "average_latency": round(avg_latency, 2),
                "runs": stats["runs"]
            })
            
        # Sort by average latency (fastest first)
        leaderboard.sort(key=lambda x: x["average_latency"])
        
        return leaderboard
        
    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail="Invalid JSON in logs file")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
