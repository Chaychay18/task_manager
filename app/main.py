import uuid
import os
import subprocess
from fastapi import FastAPI, File, UploadFile, Form, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from app.database import SessionLocal, engine
from app import models, schemas

from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
# Create tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.get("/")
def serve_ui():
    return FileResponse("static/index.html")

@app.post("/tasks", response_model=schemas.TaskResponse)
async def create_task(
    name: str = Form(...),
    description: str = Form(...),
    script: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    # Save uploaded .py file
    file_id = str(uuid.uuid4())
    file_path = os.path.join(UPLOAD_DIR, f"{file_id}_{script.filename}")
    
    with open(file_path, "wb") as f:
        content = await script.read()
        f.write(content)

    # Execute and capture output
    try:
        result = subprocess.check_output(["python", file_path], stderr=subprocess.STDOUT, text=True)
    except subprocess.CalledProcessError as e:
        result = e.output

    # Store in DB
    task = models.Task(
        id=file_id,
        name=name,
        description=description,
        result=result
    )
    db.add(task)
    db.commit()
    db.refresh(task)

    return task

@app.get("/tasks/{task_id}", response_model=schemas.TaskResponse)
def get_task(task_id: str, db: Session = Depends(get_db)):
    task = db.query(models.Task).filter(models.Task.id == task_id).first()
    if task is None:
        return JSONResponse(status_code=404, content={"message": "Task not found"})
    return task


app.mount("/static", StaticFiles(directory="static"), name="static")