import os
import logging
import torch
import cv2
from datetime import datetime
import pandas as pd
from sqlalchemy import create_engine

# Setup logging
logging.basicConfig(filename='logs/yolo_detection.log', level=logging.INFO, format='%(asctime)s - %(message)s')

# Load the YOLOv5 model
model = torch.hub.load('ultralytics/yolov5', 'yolov5s')  # Pre-trained YOLOv5 model

# PostgreSQL configuration
db_config = {
    'user': 'postgres',
    'password': 'password',
    'host': 'localhost',
    'port': 5432,
    'database': 'medical_data_warehouse'
}

# Function to store detection data to the database
def store_detections_to_db(data):
    try:
        engine = create_engine(f'postgresql+psycopg2://{db_config["user"]}:{db_config["password"]}@{db_config["host"]}:{db_config["port"]}/{db_config["database"]}')
        df = pd.DataFrame(data)
        df.to_sql('object_detections', engine, if_exists='append', index=False)
        logging.info(f"Stored {len(df)} detection records to the database.")
    except Exception as e:
        logging.error(f"Error storing detection data to the database: {e}")

# Function to process images and detect objects
def detect_objects(image_folder):
    detections = []
    for image_file in os.listdir(image_folder):
        if image_file.endswith('.jpg') or image_file.endswith('.png'):
            image_path = os.path.join(image_folder, image_file)
            logging.info(f"Processing image: {image_path}")

            # Load the image
            img = cv2.imread(image_path)

            # Perform object detection
            results = model(img)

            # Extract relevant detection data
            for detection in results.xyxy[0]:  # xyxy format for bounding boxes
                xmin, ymin, xmax, ymax, confidence, class_id = detection[:6]
                class_name = model.names[int(class_id)]

                # Log the detection
                logging.info(f"Detected {class_name} with confidence {confidence:.2f} in {image_file}")

                # Prepare detection data for storage
                detections.append({
                    'image_name': image_file,
                    'class_name': class_name,
                    'confidence': confidence.item(),
                    'x_min': xmin.item(),  # Renamed xmin to x_min
                    'y_min': ymin.item(),  # Renamed ymin to y_min
                    'x_max': xmax.item(),  # Renamed xmax to x_max
                    'y_max': ymax.item(),  # Renamed ymax to y_max
                    'detection_time': datetime.now()
                })

    # Store detection results to the database
    if detections:
        store_detections_to_db(detections)

# Main function to trigger the object detection
def main():
    image_folder = 'data/raw/images/'  # Folder containing images
    detect_objects(image_folder)
    logging.info("Object detection completed.")

if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        logging.error(f"An error occurred during object detection: {e}")
