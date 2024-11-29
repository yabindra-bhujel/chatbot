from fastapi import FastAPI

app = FastAPI()


# set tap for swagger
@app.get("/health_check", tags=["Health Check"])
def health_check():
    return {"status": "ok"}


