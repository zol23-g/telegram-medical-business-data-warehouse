# Telegram Medical Business Data Warehouse and Object Detection API with FastAPI

## Project Overview

This project focuses on creating a complete data pipeline that scrapes images from Telegram channels, performs object detection using YOLOv5, and exposes the results via a FastAPI-based REST API. The results are stored in a PostgreSQL database, and the API provides endpoints to interact with the data.

## Features

- **Data Scraping**: Scrape images from Telegram using Telethon.
- **Data Cleaning**: Process and clean scraped images and text data.
- **Object Detection**: Use YOLOv5 for detecting objects in images.
- **Data Storage**: Store detection results in PostgreSQL.
- **API**: Expose detection data through a FastAPI-based API with CRUD operations.
- **Documentation**: Auto-generated API docs with Swagger UI and ReDoc.
- **Logging**: Integrated logging throughout the pipeline for monitoring.


## Setup and Instructions

### 1. Clone the Repository
```bash
git clone https://github.com/zol23-g/telegram-medical-business-data-warehouse.git
cd telegram-medical-business-data-warehouse
```

### 2. Create Virtual Environment and Install Dependencies
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Database Configuration
Update PostgreSQL details in `app/database.py`:
```python
DATABASE_URL = "postgresql://postgres:password@localhost:5432/medical_data_warehouse"
```
Ensure PostgreSQL is running and the database exists.

### 4. Data Scraping (Telegram)
- **Objective**: Scrape images from a Telegram channel using Telethon.
- **How**: Execute the `telegram_scraper.py` to fetch images from the Telegram channel into the `data/raw/` directory.

### 5. Data Cleaning and Transformation
- **Objective**: Clean scraped data (e.g., removing duplicates and handling missing values) and transform it using DBT.
- **DBT Setup**:
  ```bash
  dbt init medical_data_warehouse
  dbt run
  ```

### 6. Object Detection Using YOLO
- **Objective**: Detect objects in scraped images using YOLOv5.
- **Steps**:
  - Clone YOLOv5 repository and install dependencies:
    ```bash
    git clone https://github.com/ultralytics/yolov5.git
    cd yolov5
    pip install -r requirements.txt
    ```
  - Run YOLOv5 on images:
    ```bash
    python detect.py --source ../data/raw/images --weights yolov5s.pt --save-txt --save-conf
    ```
  - Store detection results in PostgreSQL.

### 7. Expose Data with FastAPI
- **Objective**: Create a FastAPI REST API to expose object detection data.
- **Run FastAPI**:
  ```bash
  uvicorn app.main:app --reload
  ```
- Access interactive API docs:
  - **Swagger UI**: `http://127.0.0.1:8000/docs`
  - **ReDoc**: `http://127.0.0.1:8000/redoc`

## API Endpoints

| Method | Endpoint             | Description                      |
|--------|----------------------|----------------------------------|
| GET    | `/detections/`        | Get all object detection results |
| GET    | `/detections/{id}`    | Get a specific detection by ID   |
| POST   | `/detections/`        | Create a new detection record    |
| DELETE | `/detections/{id}`    | Delete a detection record        |

## Logging and Monitoring

Logs are stored in the `logs/` folder. The logs track:
- Data scraping, object detection, and API operations.
- Errors and status updates.
