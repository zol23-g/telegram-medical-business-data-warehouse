import os
import logging
import torch
import cv2
from datetime import datetime
import pandas as pd
from sqlalchemy import create_engine
from ultralytics import YOLO  # Import YOLO from the Ultralytics package

# Setup logging
logging.basicConfig(filename='logs/yolo_detection.log', level=logging.INFO, format='%(asctime)s - %(message)s')

# Load the YOLOv11 model
model = YOLO('yolov8n.pt')  # Load the pretrained YOLOv8n model (YOLOv11 version)

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
def detect_objects(image_folder, output_folder):
    detections = []
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    for image_file in os.listdir(image_folder):
        if image_file.endswith('.jpg') or image_file.endswith('.png'):
            image_path = os.path.join(image_folder, image_file)
            logging.info(f"Processing image: {image_path}")

            # Load the image
            img = cv2.imread(image_path)

            # Perform object detection with YOLOv11
            results = model(img)

            # Extract relevant detection data
            for result in results:
                for box in result.boxes:
                    xmin, ymin, xmax, ymax = box.xyxy[0]  # Bounding box coordinates
                    confidence = box.conf[0]  # Confidence score
                    class_id = int(box.cls[0])  # Class ID
                    class_name = model.names[class_id]  # Class name

                    # Draw bounding box on the image
                    color = (0, 255, 0)  # Green bounding box
                    cv2.rectangle(img, (int(xmin), int(ymin)), (int(xmax), int(ymax)), color, 2)
                    cv2.putText(img, f'{class_name} {confidence:.2f}', (int(xmin), int(ymin)-10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, color, 2)

                    # Log the detection
                    logging.info(f"Detected {class_name} with confidence {confidence:.2f} in {image_file}")

                    # Prepare detection data for storage
                    detections.append({
                        'image_name': image_file,
                        'class_name': class_name,
                        'confidence': confidence.item(),
                        'x_min': xmin.item(),
                        'y_min': ymin.item(),
                        'x_max': xmax.item(),
                        'y_max': ymax.item(),
                        'detection_time': datetime.now()
                    })

            # Save the image with bounding boxes to the output folder
            output_image_path = os.path.join(output_folder, image_file)
            cv2.imwrite(output_image_path, img)
            logging.info(f"Saved detected image to {output_image_path}")

    # Store detection results to the database
    if detections:
        store_detections_to_db(detections)

# Main function to trigger the object detection
def main():
    image_folder = 'data/raw/images/'  # Folder containing raw images
    output_folder = 'data/detected_images/'  # Folder to save images with detections
    detect_objects(image_folder, output_folder)
    logging.info("Object detection completed.")

if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        logging.error(f"An error occurred during object detection: {e}")
