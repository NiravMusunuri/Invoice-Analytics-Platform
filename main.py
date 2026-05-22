from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def home(name: str = "Guest"):
    return {"message": f"Hello, {name}!"}


