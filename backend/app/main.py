from fastapi import FastAPI

app = FastAPI(
    title="Secure Freelance Marketplace",
    description="AES-GCM + RSA-OAEP encrypted freelance platform",
    version="0.1.0",
)


@app.get("/health")
def health():
    return {"status": "ok"}
