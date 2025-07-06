import mysql.connector

# --- Database Configuration (Copied from previous scripts for self-containment) ---
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': ''  # IMPORTANT: Replace with your MySQL root password
}
DATABASE_NAME = 'ALX_prodev'
TABLE_NAME = 'user_data'

def stream_users_in_batches(batch_size):
    """
    A generator function that fetches rows from the 'user_data' table
    in the ALX_prodev database in specified batch sizes.

    Args:
        batch_size (int): The number of rows to fetch in each batch.

    Yields:
        list: A list of dictionaries, where each dictionary represents a user row.
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

        # Use buffered=True for fetching large results, but for true streaming
        # with yield, fetching in chunks with fetchmany is more appropriate.
        # dictionary=True ensures rows are returned as dictionaries.
        cursor = connection.cursor(dictionary=True)
        query = f"SELECT user_id, name, email, age FROM {TABLE_NAME}"
        cursor.execute(query)

        while True:
            # Fetch a batch of rows
            batch = cursor.fetchmany(batch_size)
            if not batch:
                # No more rows to fetch, break the loop
                break
            yield batch # Yield the entire batch (list of user dictionaries)

    except mysql.connector.Error as err:
        print(f"Database error in stream_users_in_batches: {err}")
    except Exception as e:
        print(f"An unexpected error occurred in stream_users_in_batches: {e}")
    finally:
        # Ensure the cursor and connection are closed
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()

def batch_processing(batch_size):
    """
    A generator function that processes user data in batches.
    It fetches batches using stream_users_in_batches and filters
    users older than 25.

    Args:
        batch_size (int): The size of batches to fetch from the database.

    Yields:
        dict: A dictionary representing a user who is older than 25.
    """
    # Loop 1: Iterates over batches yielded by stream_users_in_batches
    for batch in stream_users_in_batches(batch_size):
        # Loop 2: Iterates over individual users within each batch
        for user in batch:
            # Loop 3 (implicit/conditional check, not a full loop):
            # The 'if' condition acts as a filter.
            if user['age'] > 25:
                yield user

# Example of how to use the batch_processing generator (similar to 2-main.py)
if __name__ == "__main__":
    import sys

    # Set a batch size for demonstration
    demo_batch_size = 50

    print(f"Processing users in batches of {demo_batch_size}, filtering for age > 25:")
    try:
        # Iterate over the processed users (which are yielded one by one)
        for processed_user in batch_processing(demo_batch_size):
            print(processed_user)
    except BrokenPipeError:
        # This can happen if output is piped to `head` and it closes early
        sys.stderr.close()
    except Exception as e:
        print(f"An error occurred during batch processing: {e}", file=sys.stderr)

