from sqlalchemy.orm import Session
from . import models, schemas

# Get all detection records
def get_detections(db: Session, skip: int = 0, limit: int = 10):
    return db.query(models.ObjectDetection).offset(skip).limit(limit).all()

# Get a single detection by ID
def get_detection_by_id(db: Session, detection_id: int):
    return db.query(models.ObjectDetection).filter(models.ObjectDetection.id == detection_id).first()

# Create a new detection record
def create_detection(db: Session, detection: schemas.ObjectDetectionCreate):
    db_detection = models.ObjectDetection(**detection.dict())
    db.add(db_detection)
    db.commit()
    db.refresh(db_detection)
    return db_detection

# Delete a detection record
def delete_detection(db: Session, detection_id: int):
    db_detection = db.query(models.ObjectDetection).filter(models.ObjectDetection.id == detection_id).first()
    db.delete(db_detection)
    db.commit()
    return db_detection
