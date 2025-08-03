import time
from fastapi import APIRouter
from typing import List, Dict
from pydantic import BaseModel

class ModelMetric(BaseModel):
    model_name: str
    latency: float
    timestamp: float
    task: str

router = APIRouter(
    prefix="/metrics",
    tags=["metrics"]
)

# In-memory storage for model metrics (in production, this would be a database)
model_metrics: List[ModelMetric] = []

@router.post("/record")
def record_metric(model_name: str, latency: float, task: str):
    """Record a model's performance metric"""
    metric = ModelMetric(
        model_name=model_name,
        latency=latency,
        timestamp=time.time(),
        task=task
    )
    model_metrics.append(metric)
    return {"message": "Metric recorded successfully"}

@router.get("/leaderboard")
def get_leaderboard(limit: int = 3):
    """Get the fastest models leaderboard"""
    # Sort by latency and get top N
    sorted_metrics = sorted(model_metrics, key=lambda x: x.latency)
    leaderboard = []
    
    # Group by model name and get the fastest time for each
    model_fastest = {}
    for metric in sorted_metrics:
        if metric.model_name not in model_fastest or metric.latency < model_fastest[metric.model_name].latency:
            model_fastest[metric.model_name] = metric
    
    # Sort by latency again and limit results
    fastest_models = sorted(model_fastest.values(), key=lambda x: x.latency)[:limit]
    
    for metric in fastest_models:
        leaderboard.append({
            "model_name": metric.model_name,
            "latency": metric.latency,
            "task": metric.task
        })
    
    return leaderboard

@router.get("/model_stats")
def get_model_stats():
    """Get statistics for all models"""
    stats = {}
    for metric in model_metrics:
        if metric.model_name not in stats:
            stats[metric.model_name] = {
                "count": 0,
                "total_latency": 0,
                "min_latency": float('inf'),
                "max_latency": 0
            }
        
        stats[metric.model_name]["count"] += 1
        stats[metric.model_name]["total_latency"] += metric.latency
        stats[metric.model_name]["min_latency"] = min(stats[metric.model_name]["min_latency"], metric.latency)
        stats[metric.model_name]["max_latency"] = max(stats[metric.model_name]["max_latency"], metric.latency)
    
    # Calculate averages
    for model_name in stats:
        stats[model_name]["avg_latency"] = stats[model_name]["total_latency"] / stats[model_name]["count"]
    
    return stats
