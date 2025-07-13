import sqlite3
import functools
from datetime import datetime



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
            print(f"Database error: {e}")
            raise  # Re-raise the exception after logging
        finally:
            if conn:
                # Ensure the connection is closed
                conn.close()
                print("Database connection closed.")

    return wrapper

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

@with_db_connection
def get_user_by_id(conn, user_id):
    """
    Fetches a user by their ID from the database.
    The connection 'conn' is provided by the decorator.
    """
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    return cursor.fetchone()

@with_db_connection
def add_new_user(conn, name, email):
    """
    Adds a new user to the database.
    The connection 'conn' is provided by the decorator.
    """
    cursor = conn.cursor()
    cursor.execute("INSERT INTO users (name, email) VALUES (?, ?)", (name, email))
    conn.commit() # Commit the transaction here since this function modifies the DB
    print(f"User '{name}' added.")
    return cursor.lastrowid

if __name__ == "__main__":
    setup_database()

    # Fetch user by ID with automatic connection handling
    print("\n--- Fetching user with ID 1 ---")
    user = get_user_by_id(user_id=1)
    print(f"Fetched user: {user}")

    print("\n--- Fetching user with ID 99 (non-existent) ---")
    user_non_existent = get_user_by_id(user_id=99)
    print(f"Fetched user: {user_non_existent}")

    print("\n--- Adding a new user ---")
    new_user_id = add_new_user(name="Charlie", email="charlie@example.com")
    print(f"New user added with ID: {new_user_id}")

    print("\n--- Fetching the newly added user ---")
    fetched_new_user = get_user_by_id(user_id=new_user_id)
    print(f"Fetched new user: {fetched_new_user}")