from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from .setups import crud, models, schemas  # Use absolute imports
from .setups.database import engine, get_db

# Create the FastAPI app
app = FastAPI()

# Create all the tables in the database (this is equivalent to running migrations)
models.Base.metadata.create_all(bind=engine)

# API endpoint to get all detection records
@app.get("/detections/", response_model=list[schemas.ObjectDetection])
def read_detections(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    detections = crud.get_detections(db, skip=skip, limit=limit)
    return detections

# API endpoint to get a single detection by ID
@app.get("/detections/{detection_id}", response_model=schemas.ObjectDetection)
def read_detection(detection_id: int, db: Session = Depends(get_db)):
    detection = crud.get_detection_by_id(db, detection_id=detection_id)
    if detection is None:
        raise HTTPException(status_code=404, detail="Detection not found")
    return detection

# API endpoint to create a new detection record
@app.post("/detections/", response_model=schemas.ObjectDetection)
def create_detection(detection: schemas.ObjectDetectionCreate, db: Session = Depends(get_db)):
    return crud.create_detection(db=db, detection=detection)

# API endpoint to delete a detection record
@app.delete("/detections/{detection_id}", response_model=schemas.ObjectDetection)
def delete_detection(detection_id: int, db: Session = Depends(get_db)):
    detection = crud.delete_detection(db=db, detection_id=detection_id)
    if detection is None:
        raise HTTPException(status_code=404, detail="Detection not found")
    return detection
