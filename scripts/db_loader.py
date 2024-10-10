import os
import pandas as pd
import psycopg2
import logging
from psycopg2 import sql
from sqlalchemy import create_engine
from contextlib import closing

# Logging setup
logging.basicConfig(filename='logs/database_operations.log', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

# PostgreSQL configuration
db_config = {
    'user': 'postgres',
    'password': 'password',
    'host': 'localhost',
    'port': 5432,
    'database': 'medical_data_warehouse'
}

# Table creation query
create_table_query = """
CREATE TABLE IF NOT EXISTS medical_data (
    message_id TEXT PRIMARY KEY,
    sender_id TEXT,
    message_text TEXT,
    channel TEXT,
    date TIMESTAMP
);
"""

def connect_to_db(db_config):
    """Establishes a connection to the PostgreSQL database."""
    try:
        connection = psycopg2.connect(
            user=db_config['user'],
            password=db_config['password'],
            host=db_config['host'],
            port=db_config['port'],
            database=db_config['database']
        )
        logging.info("Successfully connected to the database.")
        return connection
    except Exception as e:
        logging.error(f"Error while connecting to PostgreSQL: {e}")
        raise

def create_table(connection):
    """Creates the 'medical_data' table if it doesn't exist."""
    try:
        with connection.cursor() as cursor:
            cursor.execute(create_table_query)
            connection.commit()
            logging.info("Table 'medical_data' created successfully (if not existed).")
    except Exception as e:
        connection.rollback()
        logging.error(f"Error creating the table: {e}")
        raise

def insert_data_to_table(df, connection):
    """Inserts cleaned data from the DataFrame into the 'medical_data' table."""
    try:
        # Using SQLAlchemy to bulk insert data from DataFrame
        engine = create_engine(f'postgresql+psycopg2://{db_config["user"]}:{db_config["password"]}@{db_config["host"]}:{db_config["port"]}/{db_config["database"]}')
        
        # Insert data
        df.to_sql('medical_data', engine, if_exists='append', index=False)
        logging.info(f"Successfully inserted {len(df)} records into 'medical_data' table.")
    except Exception as e:
        logging.error(f"Error inserting data into the table: {e}")
        raise

def close_connection(connection):
    """Closes the database connection."""
    if connection:
        connection.close()
        logging.info("PostgreSQL connection closed successfully.")

def main():
    try:
        # Load cleaned data from CSV
        df = pd.read_csv('data/cleaned/cleaned_data.csv')

        # Connect to the PostgreSQL database
        connection = connect_to_db(db_config)

        # Create the table if it doesn't exist
        create_table(connection)

        # Insert the data into the table
        insert_data_to_table(df, connection)

    except Exception as e:
        logging.error(f"An error occurred during the database operation: {e}")
    finally:
        # Close the connection
        close_connection(connection)

if __name__ == '__main__':
    main()
