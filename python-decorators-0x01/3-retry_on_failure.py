import time
import sqlite3
import functools

def with_db_connection(func):
    """
    Decorator to automatically handle opening and closing database connections.
    It passes the connection object as the first argument to the decorated function.
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        conn = None
        try:
            # Establish a database connection
            conn = sqlite3.connect('users.db')
            print("Database connection opened.")

            # Pass the connection object as the first argument to the decorated function
            result = func(conn, *args, **kwargs)
            return result
        except sqlite3.Error as e:
            print(f"Database error in with_db_connection: {e}")
            raise  # Re-raise the exception after logging
        finally:
            if conn:
                # Ensure the connection is closed
                conn.close()
                print("Database connection closed.")

    return wrapper

def retry_on_failure(retries=3, delay=2):
    """
    Decorator that retries a function a certain number of times if it raises an exception.

    Args:
        retries (int): The maximum number of times to retry the function.
        delay (int): The delay in seconds between retries.
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            for i in range(retries):
                try:
                    print(f"Attempt {i + 1}/{retries} for function: {func.__name__}")
                    return func(*args, **kwargs)
                except Exception as e:
                    print(f"Attempt {i + 1} failed for {func.__name__}: {e}")
                    if i < retries - 1:
                        print(f"Retrying in {delay} seconds...")
                        time.sleep(delay)
                    else:
                        print(f"All {retries} attempts failed for {func.__name__}. Raising the last exception.")
                        raise # Re-raise the last exception after all retries are exhausted
        return wrapper
    return decorator

# Setup a dummy users.db for testing
def setup_database():
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            email TEXT
        )
    ''')
    # Insert some sample data if it doesn't exist
    cursor.execute("INSERT OR IGNORE INTO users (id, name, email) VALUES (1, 'Alice', 'alice@example.com')")
    cursor.execute("INSERT OR IGNORE INTO users (id, name, email) VALUES (2, 'Bob', 'bob@example.com')")
    conn.commit()
    conn.close()
    print("Database setup complete with sample data.")

# Global counter to simulate transient errors
_fail_count = 0
_max_failures = 2 # This function will fail twice before succeeding

@with_db_connection
@retry_on_failure(retries=3, delay=1)
def fetch_users_with_retry(conn):
    """
    Fetches all users from the database.
    This function is designed to fail a few times to demonstrate the retry mechanism.
    """
    global _fail_count
    if _fail_count < _max_failures:
        _fail_count += 1
        print(f"Simulating a transient error (failure count: {_fail_count})...")
        raise sqlite3.OperationalError("Database is temporarily unavailable.")
    else:
        print("Simulated transient error resolved. Fetching data now.")
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users")
        return cursor.fetchall()

@with_db_connection
@retry_on_failure(retries=2, delay=0.5)
def insert_data_with_retry(conn, name, email):
    """
    Inserts data with retry mechanism.
    This function will also simulate a transient error.
    """
    global _fail_count # Using the same global for simplicity, reset if needed for separate tests
    if _fail_count < _max_failures:
        _fail_count += 1
        print(f"Simulating insert failure (failure count: {_fail_count})...")
        raise sqlite3.OperationalError("Write operation temporarily blocked.")
    else:
        print(f"Simulated insert failure resolved. Inserting user {name} now.")
        cursor = conn.cursor()
        cursor.execute("INSERT INTO users (name, email) VALUES (?, ?)", (name, email))
        conn.commit()
        return cursor.lastrowid


if __name__ == "__main__":
    setup_database()

    print("\n--- Attempting to fetch users with retry ---")
    try:
        users = fetch_users_with_retry()
        print("\nSuccessfully fetched users:")
        for user in users:
            print(user)
    except Exception as e:
        print(f"Failed to fetch users after multiple retries: {e}")

    # Reset fail count for the next test
    _fail_count = 0
    _max_failures = 1 # This will fail once then succeed

    print("\n--- Attempting to insert a new user with retry ---")
    try:
        new_user_id = insert_data_with_retry(name="Eve", email="eve@example.com")
        print(f"\nSuccessfully inserted new user with ID: {new_user_id}")
        # Verify insertion
        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE id = ?", (new_user_id,))
        print(f"Verified new user: {cursor.fetchone()}")
        conn.close()
    except Exception as e:
        print(f"Failed to insert user after multiple retries: {e}")

    # Reset fail count for a test that will always fail
    _fail_count = 0
    _max_failures = 3 # This will fail all 3 attempts

    print("\n--- Attempting an operation that will always fail (3 retries) ---")
    @with_db_connection
    @retry_on_failure(retries=3, delay=0.1)
    def always_fail_operation(conn):
        global _fail_count
        _fail_count += 1
        print(f"Always failing operation (failure count: {_fail_count})...")
        raise sqlite3.OperationalError("This operation always fails.")

    try:
        always_fail_operation()
    except Exception as e:
        print(f"Caught expected exception after all retries: {e}")