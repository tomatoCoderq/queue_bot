from src.api.app import app
from src.config import settings

if __name__ == "__main__":
    import uvicorn

    uvicorn.run("src.api.app:app", 
                host=settings.api.API_HOST, 
                port=settings.api.API_PORT, 
                reload=True)


                