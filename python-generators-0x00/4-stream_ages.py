import mysql.connector
import sys

# --- Database Configuration (Copied from previous scripts for self-containment) ---
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': ''  # IMPORTANT: Replace with your MySQL root password
}
DATABASE_NAME = 'ALX_prodev'
TABLE_NAME = 'user_data'

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
        # print(f"Successfully connected to database '{DATABASE_NAME}'.") # Optional: for debugging
        return conn
    except mysql.connector.Error as err:
        print(f"Error connecting to database '{DATABASE_NAME}': {err}", file=sys.stderr)
        return None

def paginate_users(page_size, offset):
    """
    Fetches a single page of user data from the user_data table.

    Args:
        page_size (int): The maximum number of rows to fetch for the current page.
        offset (int): The starting offset for fetching rows.

    Returns:
        list: A list of dictionaries, where each dictionary represents a user row.
    """
    connection = None
    cursor = None
    rows = []
    try:
        connection = connect_to_prodev()
        if not connection or not connection.is_connected():
            return [] # Return empty list if connection fails

        cursor = connection.cursor(dictionary=True)
        # Use LIMIT and OFFSET to fetch a specific page
        # Updated to use SELECT * as per the objective's example
        query = f"SELECT * FROM {TABLE_NAME} LIMIT {page_size} OFFSET {offset}"
        cursor.execute(query)
        rows = cursor.fetchall() # Fetch all rows for the current page
    except mysql.connector.Error as err:
        print(f"Database error in paginate_users: {err}", file=sys.stderr)
    except Exception as e:
        print(f"An unexpected error occurred in paginate_users: {e}", file=sys.stderr)
    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()
    return rows

def lazy_paginate(page_size):
    """
    A generator function that lazily loads pages of user data from the database.
    It fetches the next page only when needed.

    Args:
        page_size (int): The number of users to include in each page.

    Yields:
        list: A list of dictionaries, where each dictionary represents a user row
              for the current page.
    """
    offset = 0
    # This is the single loop as per the requirement
    while True:
        page = paginate_users(page_size, offset)
        if not page:
            # No more data to fetch, exit the generator
            break
        yield page
        offset += page_size # Increment offset for the next page

# New Function: Generator to stream user ages one by one
def stream_user_ages():
    """
    A generator function that streams only the 'age' of users one by one
    from the 'user_data' table. This is memory-efficient for large datasets.

    Yields:
        int/float: The age of a user.
    """
    connection = None
    cursor = None
    try:
        connection = connect_to_prodev()
        if not connection or not connection.is_connected():
            print(f"Error: Could not connect to database '{DATABASE_NAME}' to stream ages.", file=sys.stderr)
            return

        cursor = connection.cursor(dictionary=True) # Fetch as dictionary to access 'age' by name
        query = f"SELECT age FROM {TABLE_NAME}"
        cursor.execute(query)

        # Loop 1: Iterates over the results fetched by the cursor
        for row in cursor:
            yield row['age'] # Yield the age value

    except mysql.connector.Error as err:
        print(f"Database error in stream_user_ages: {err}", file=sys.stderr)
    except Exception as e:
        print(f"An unexpected error occurred in stream_user_ages: {e}", file=sys.stderr)
    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()

# New Function: Calculate average age using the generator
def calculate_average_age():
    """
    Calculates the average age of users without loading the entire dataset
    into memory, by using the stream_user_ages generator.
    """
    total_age = 0
    user_count = 0

    # Loop 2: Iterates over ages yielded by stream_user_ages
    for age in stream_user_ages():
        total_age += age
        user_count += 1

    if user_count > 0:
        average_age = total_age / user_count
        print(f"Average age of users: {average_age}")
    else:
        print("No users found to calculate average age.")


# Example of how to use the lazy_paginate generator (similar to 3-main.py)
if __name__ == "__main__":
    # Test the seed.py connection setup first if you haven't
    # import seed # You would normally import seed and run its main to ensure DB is set up
    # seed.main() # Assuming seed.py has a main function to run setup

    # --- Demo for lazy_paginate ---
    demo_page_size = 100 # Example page size
    print(f"--- Lazily paginating users with a page size of {demo_page_size} ---")
    try:
        # Iterate over pages yielded by lazy_paginate
        for page_num, page in enumerate(lazy_paginate(demo_page_size)):
            print(f"\n--- Page {page_num + 1} (Offset: {page_num * demo_page_size}) ---")
            if not page:
                print("No more users.")
                break
            # Iterate over users within the current page
            for user in page:
                print(user)
    except BrokenPipeError:
        # This can happen if output is piped to `head` and it closes early
        sys.stderr.close()
    except Exception as e:
        print(f"An error occurred during lazy pagination: {e}", file=sys.stderr)

    print("\n" + "="*50 + "\n") # Separator for clarity

    # --- Demo for memory-efficient average age calculation ---
    print("--- Calculating average age memory-efficiently ---")
    calculate_average_age()
