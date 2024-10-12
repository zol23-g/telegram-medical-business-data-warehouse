from sqlalchemy import Column, Integer, String, Float, DateTime
from .database import Base

# SQLAlchemy model for the object_detections table
class ObjectDetection(Base):
    __tablename__ = "object_detections"

    id = Column(Integer, primary_key=True, index=True)
    image_name = Column(String)
    class_name = Column(String)
    confidence = Column(Float)
    x_min = Column(Float)
    y_min = Column(Float)
    x_max = Column(Float)
    y_max = Column(Float)
    detection_time = Column(DateTime)
