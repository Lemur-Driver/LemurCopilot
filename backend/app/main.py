from fastapi import FastAPI

app = FastAPI()


@app.get("/")
def root():
    return {"message": "Adaptive Driving Tutor API"}


@app.get("/health")
def health():
    return {"status": "ok"}