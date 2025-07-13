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
            print(f"Database error in with_db_connection: {e}")
            raise  # Re-raise the exception after logging
        finally:
            if conn:
                # Ensure the connection is closed
                conn.close()
                print("Database connection closed.")

    return wrapper

def transactional(func):
    """
    Decorator to manage database transactions (commit/rollback).
    Assumes the decorated function receives a 'conn' object as its first argument.
    """
    @functools.wraps(func)
    def wrapper(conn, *args, **kwargs):
        if not isinstance(conn, sqlite3.Connection):
            raise TypeError("The 'transactional' decorator expects 'conn' (a sqlite3.Connection object) as the first argument.")
        try:
            print(f"Starting transaction for function: {func.__name__}")
            result = func(conn, *args, **kwargs)
            conn.commit()
            print(f"Transaction committed for function: {func.__name__}")
            return result
        except Exception as e:
            conn.rollback()
            print(f"Transaction rolled back for function: {func.__name__} due to error: {e}")
            raise # Re-raise the exception to propagate it
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
@transactional
def update_user_email(conn, user_id, new_email):
    """
    Updates a user's email. This function is wrapped by both with_db_connection
    and transactional decorators.
    """
    cursor = conn.cursor()
    print(f"Attempting to update user {user_id} email to {new_email}")
    cursor.execute("UPDATE users SET email = ? WHERE id = ?", (new_email, user_id))
    if cursor.rowcount == 0:
        print(f"No user found with id {user_id}. Update failed.")
        # Optionally raise an error if no rows were updated to trigger a rollback
        # raise ValueError(f"User with ID {user_id} not found.")
    else:
        print(f"User {user_id} email updated to {new_email}.")


@with_db_connection
@transactional
def add_user_and_fail(conn, name, email):
    """
    Adds a user and then intentionally raises an error to demonstrate rollback.
    """
    cursor = conn.cursor()
    print(f"Attempting to add user '{name}' and then cause an error...")
    cursor.execute("INSERT INTO users (name, email) VALUES (?, ?)", (name, email))
    print(f"User '{name}' inserted (will be rolled back).")
    # Simulate an error
    raise ValueError("Simulated error after inserting user.")


@with_db_connection
def get_user_by_id(conn, user_id):
    """
    Fetches a user by their ID. Used to verify changes.
    """
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    return cursor.fetchone()


if __name__ == "__main__":
    setup_database()

    print("\n--- Test Case 1: Successful Update ---")
    initial_user_1 = get_user_by_id(user_id=1)
    print(f"Initial user 1: {initial_user_1}")
    try:
        update_user_email(user_id=1, new_email='Crawford_Cartwright@hotmail.com')
        updated_user_1 = get_user_by_id(user_id=1)
        print(f"Updated user 1: {updated_user_1}")
    except Exception as e:
        print(f"An unexpected error occurred during successful update test: {e}")

    print("\n--- Test Case 2: Failed Operation (Rollback) ---")
    initial_user_count = 0
    with sqlite3.connect('users.db') as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM users")
        initial_user_count = cursor.fetchone()[0]
    print(f"Initial user count: {initial_user_count}")

    try:
        add_user_and_fail(name="Dave", email="dave@example.com")
    except ValueError as e:
        print(f"Caught expected error: {e}")
    except Exception as e:
        print(f"Caught unexpected error: {e}")

    final_user_count = 0
    with sqlite3.connect('users.db') as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM users")
        final_user_count = cursor.fetchone()[0]
    print(f"Final user count after failed operation: {final_user_count}")

    # Verify that Dave was not added
    dave = get_user_by_id(user_id=None, name="Dave") # Assuming get_user_by_id can search by name if needed, or we fetch all users
    # For simplicity, let's just check the count, as 'get_user_by_id' only takes ID.
    # If the count is the same as initial, rollback worked.
    if initial_user_count == final_user_count:
        print("Rollback successful: User 'Dave' was not added to the database.")
    else:
        print("Rollback failed: User 'Dave' was added to the database.")

    print("\n--- Verifying final state of user 1 ---")
    final_user_1 = get_user_by_id(user_id=1)
    print(f"Final user 1: {final_user_1}")