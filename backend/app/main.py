from fastapi import FastAPI

app = FastAPI(title="Vienna Metro Live API")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
