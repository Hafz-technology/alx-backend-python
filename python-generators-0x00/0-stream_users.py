import mysql.connector

# --- Database Configuration (Copied from seed.py for self-containment) ---
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': ''  # IMPORTANT: Replace with your MySQL root password
}
DATABASE_NAME = 'ALX_prodev'
TABLE_NAME = 'user_data'

def stream_users():
    """
    A generator function that streams rows from the 'user_data' table
    in the ALX_prodev database one by one.
    """
    connection = None
    cursor = None
    try:
        # Establish connection to the ALX_prodev database
        db_config_with_db = DB_CONFIG.copy()
        db_config_with_db['database'] = DATABASE_NAME
        connection = mysql.connector.connect(**db_config_with_db)

        if not connection.is_connected():
            print(f"Error: Could not connect to database '{DATABASE_NAME}'.")
            return # Exit generator if connection fails

        cursor = connection.cursor(dictionary=True) # Use dictionary=True to get rows as dicts
        query = f"SELECT user_id, name, email, age FROM {TABLE_NAME}"
        cursor.execute(query)

        # Iterate over the results and yield each row
        # This loop is the only loop in the function as per the requirement
        for row in cursor:
            yield row

    except mysql.connector.Error as err:
        print(f"Database error: {err}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    finally:
        # Ensure the cursor and connection are closed
        if cursor:
            cursor.close()
            # print("Database cursor closed.") # Optional: for debugging
        if connection and connection.is_connected():
            connection.close()
            # print("Database connection closed.") # Optional: for debugging

# Example of how to use the generator (similar to 1-main.py provided in prompt)
if __name__ == "__main__":
    from itertools import islice

    print("Streaming first 6 users:")
    for user in islice(stream_users(), 6):
        print(user)

    print("\nStreaming next 3 users (demonstrates continued streaming if more data exists):")
    # To demonstrate continued streaming, you'd need to re-call the generator
    # as the generator exhausts its results after the first iteration.
    # For a real-world scenario where you want to resume, you'd manage state
    # or use an OFFSET/LIMIT approach if not using a true server-side cursor.
    # For this generator, each call starts fresh.
    for user in islice(stream_users(), 3):
        print(user)
