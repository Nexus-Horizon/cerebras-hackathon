from fastapi import APIRouter

router = APIRouter(
    prefix="/example",
    tags=["example"]
)

@router.get("/")
def get_example():
    return {
        "example": "This is an example endpoint",
        "endpoints": {
            "analyze": "POST /analyze - Image analysis endpoint"
        }
    }
