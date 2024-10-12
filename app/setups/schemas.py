from pydantic import BaseModel
from datetime import datetime

# Schema for reading detection data
class ObjectDetectionBase(BaseModel):
    image_name: str
    class_name: str
    confidence: float
    x_min: float
    y_min: float
    x_max: float
    y_max: float
    detection_time: datetime

# Schema for creating detection data
class ObjectDetectionCreate(ObjectDetectionBase):
    pass

# Schema for reading detection data, including the ID
class ObjectDetection(ObjectDetectionBase):
    id: int

    class Config:
        orm_mode = True  # Enable ORM mode to interact with SQLAlchemy models
