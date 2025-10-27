import uvicorn

if __name__ == "__main__":
    uvicorn.run(
        "api:app",  # This must point to api.py
        host="0.0.0.0", 
        port=8000,
        reload=True
    )