from fastapi import FastAPI

app = FastAPI(title="API d'administration de conteneurs")

@app.get("/health")
def health_check():
    return {"status": "healthy"}