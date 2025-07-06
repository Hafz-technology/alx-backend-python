import mysql.connector
import csv
import uuid
import os

# --- Database Configuration ---
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': ''   # IMPORTANT: Replace with your MySQL root password
}
DATABASE_NAME = 'ALX_prodev'
TABLE_NAME = 'user_data'
CSV_FILE = 'user_data.csv'

def connect_db():
    """
    Connects to the MySQL database server.
    Returns a connection object if successful, None otherwise.
    """
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        print("Successfully connected to MySQL server.")
        return conn
    except mysql.connector.Error as err:
        print(f"Error connecting to MySQL server: {err}")
        return None

def create_database(connection):
    """
    Creates the ALX_prodev database if it does not exist.
    """
    try:
        cursor = connection.cursor()
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DATABASE_NAME}")
        print(f"Database '{DATABASE_NAME}' checked/created successfully.")
        cursor.close()
    except mysql.connector.Error as err:
        print(f"Error creating database '{DATABASE_NAME}': {err}")

def connect_to_prodev():
    """
    Connects to the ALX_prodev database in MySQL.
    Returns a connection object to ALX_prodev if successful, None otherwise.
    """
    try:
        # Add database name to config for direct connection
        db_config_with_db = DB_CONFIG.copy()
        db_config_with_db['database'] = DATABASE_NAME
        conn = mysql.connector.connect(**db_config_with_db)
        print(f"Successfully connected to database '{DATABASE_NAME}'.")
        return conn
    except mysql.connector.Error as err:
        print(f"Error connecting to database '{DATABASE_NAME}': {err}")
        return None

def create_table(connection):
    """
    Creates a table user_data if it does not exist with the required fields.
    user_id (PRIMARY KEY, UUID, Indexed)
    name (VARCHAR, NOT NULL)
    email (VARCHAR, NOT NULL, UNIQUE) - Added UNIQUE for idempotency
    age (DECIMAL, NOT NULL)
    """
    try:
        cursor = connection.cursor()
        create_table_query = f"""
        CREATE TABLE IF NOT EXISTS {TABLE_NAME} (
            user_id VARCHAR(36) PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            email VARCHAR(255) NOT NULL UNIQUE, -- Added UNIQUE constraint
            age DECIMAL(3,0) NOT NULL
        )
        """
        cursor.execute(create_table_query)
        print(f"Table '{TABLE_NAME}' checked/created successfully.")
        cursor.close()
    except mysql.connector.Error as err:
        print(f"Error creating table '{TABLE_NAME}': {err}")

def insert_data(connection, data_rows):
    """
    Inserts data into the user_data table.
    Uses INSERT IGNORE to prevent re-inserting rows with duplicate emails
    (due to the UNIQUE constraint on email).
    """
    if not data_rows:
        print("No data rows provided for insertion.")
        return

    try:
        cursor = connection.cursor()
        insert_query = f"""
        INSERT IGNORE INTO {TABLE_NAME} (user_id, name, email, age)
        VALUES (%s, %s, %s, %s)
        """
        records_inserted = 0
        for row in data_rows:
            # Generate a new UUID for each user
            user_id = str(uuid.uuid4())
            try:
                # Ensure age is convertible to DECIMAL
                age = int(row['age']) # Convert to int first to handle potential floats in CSV
            except ValueError:
                print(f"Skipping row due to invalid age: {row}")
                continue

            values = (user_id, row['name'], row['email'], age)
            try:
                cursor.execute(insert_query, values)
                # Check if a row was actually inserted (not ignored)
                if cursor.rowcount > 0:
                    records_inserted += 1
            except mysql.connector.IntegrityError as err:
                # This catches other integrity errors if any, though INSERT IGNORE handles UNIQUE
                print(f"Integrity Error inserting data: {err} for row: {row}")
            except mysql.connector.Error as err:
                print(f"Error inserting data: {err} for row: {row}")

        connection.commit()
        print(f"Attempted to insert {len(data_rows)} rows. Successfully inserted/updated {records_inserted} new records.")
        cursor.close()
    except mysql.connector.Error as err:
        print(f"Error during data insertion: {err}")
        if connection:
            connection.rollback() # Rollback in case of an error during a batch
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

def read_csv_data(file_path):
    """Reads data from a CSV file and returns a list of dictionaries."""
    data = []
    if not os.path.exists(file_path):
        print(f"Error: CSV file not found at '{file_path}'")
        return data
    try:
        with open(file_path, mode='r', newline='', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                data.append(row)
        print(f"Successfully read {len(data)} rows from '{file_path}'.")
    except Exception as e:
        print(f"Error reading CSV file: {e}")
    return data

if __name__ == "__main__":
    # Create a dummy CSV file for demonstration if it doesn't exist
    if not os.path.exists(CSV_FILE):
        print(f"'{CSV_FILE}' not found. Creating a dummy CSV for demonstration.")
        with open(CSV_FILE, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['name', 'email', 'age'])
            writer.writerow(['John Doe', 'john.doe@example.com', '30'])
            writer.writerow(['Jane Smith', 'jane.smith@example.com', '25'])
            writer.writerow(['Peter Jones', 'peter.jones@example.com', '40'])
            writer.writerow(['Alice Brown', 'alice.brown@example.com', '35'])
            writer.writerow(['Bob White', 'bob.white@example.com', '28'])
            writer.writerow(['Charlie Green', 'charlie.green@example.com', '45'])
        print(f"Dummy '{CSV_FILE}' created.")

    # --- Main execution flow ---
    conn_server = None
    conn_db = None
    try:
        # 1. Connect to MySQL server
        conn_server = connect_db()
        if not conn_server:
            exit("Exiting: Could not connect to MySQL server.")

        # 2. Create the database
        create_database(conn_server)
        conn_server.close() # Close server connection, will reconnect to specific DB

        # 3. Connect to the ALX_prodev database
        conn_db = connect_to_prodev()
        if not conn_db:
            exit("Exiting: Could not connect to ALX_prodev database.")

        # 4. Create the user_data table
        create_table(conn_db)

        # 5. Read data from CSV
        user_data_from_csv = read_csv_data(CSV_FILE)
        if not user_data_from_csv:
            print("No data to insert from CSV. Exiting.")
        else:
            # 6. Insert data into the table
            insert_data(conn_db, user_data_from_csv)

    finally:
        # Ensure connections are closed
        if conn_server and conn_server.is_connected():
            conn_server.close()
            print("MySQL server connection closed.")
        if conn_db and conn_db.is_connected():
            conn_db.close()
            print("ALX_prodev database connection closed.")
