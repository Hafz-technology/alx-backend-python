import sqlite3

class DatabaseConnection:
    """
    A custom class-based context manager for managing SQLite database connections.

    This context manager ensures that a database connection is properly opened
    when entering the 'with' block and automatically closed when exiting,
    even if errors occur.
    """
    def __init__(self, db_name):
        """
        Initializes the DatabaseConnection context manager.

        Args:
            db_name (str): The name of the SQLite database file.
        """
        self.db_name = db_name
        self.conn = None
        self.cursor = None

    def __enter__(self):
        """
        Enters the runtime context related to this object.
        Establishes a database connection and returns it.
        """
        try:
            self.conn = sqlite3.connect(self.db_name)
            self.cursor = self.conn.cursor()
            print(f"Database connection to '{self.db_name}' opened.")
            return self.conn
        except sqlite3.Error as e:
            print(f"Error opening database connection: {e}")
            # Re-raise the exception to indicate connection failure
            raise

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Exits the runtime context related to this object.
        Closes the database connection and handles any exceptions that occurred
        within the 'with' block.

        Args:
            exc_type: The type of the exception that caused the context to be exited.
                      None if no exception occurred.
            exc_val: The exception instance.
            exc_tb: A traceback object encapsulating the call stack at the point
                    where the exception originally occurred.
        """
        if self.conn:
            if exc_type:
                # An exception occurred, rollback changes
                self.conn.rollback()
                print(f"Transaction rolled back due to an exception: {exc_val}")
            else:
                # No exception, commit changes
                self.conn.commit()
                print("Transaction committed.")
            self.conn.close()
            print(f"Database connection to '{self.db_name}' closed.")
        
        # If exc_type is not None, returning False (or not returning anything)
        # will propagate the exception. Returning True would suppress it.
        # We want to propagate it for this task, so no explicit return True.
        return False

# Setup a dummy users.db for testing
def setup_database(db_name='users.db'):
    """
    Sets up a simple 'users' table in the specified SQLite database
    and inserts some sample data if it doesn't already exist.
    """
    try:
        with sqlite3.connect(db_name) as conn:
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
            cursor.execute("INSERT OR IGNORE INTO users (id, name, email) VALUES (3, 'Charlie', 'charlie@example.com')")
            conn.commit()
        print(f"Database '{db_name}' setup complete with sample data.")
    except sqlite3.Error as e:
        print(f"Error during database setup: {e}")

if __name__ == "__main__":
    DB_FILE = 'users.db'
    setup_database(DB_FILE)

    print("\n--- Using DatabaseConnection for a successful query ---")
    try:
        with DatabaseConnection(DB_FILE) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users")
            results = cursor.fetchall()
            print("\nResults from 'SELECT * FROM users':")
            for row in results:
                print(row)
    except Exception as e:
        print(f"An error occurred during successful query: {e}")

    print("\n--- Using DatabaseConnection for an operation that causes an error ---")
    try:
        with DatabaseConnection(DB_FILE) as conn:
            cursor = conn.cursor()
            print("Attempting to insert invalid data (should trigger rollback)...")
            # This will cause an error because 'id' is PRIMARY KEY and 1 already exists
            cursor.execute("INSERT INTO users (id, name, email) VALUES (1, 'Duplicate', 'duplicate@example.com')")
            # Or, simulate another type of error
            # raise ValueError("Simulated error inside with block")
    except sqlite3.IntegrityError as e:
        print(f"Caught expected error: {e}")
    except Exception as e:
        print(f"Caught unexpected error: {e}")

    print("\n--- Verifying database state after potential rollback ---")
    try:
        with DatabaseConnection(DB_FILE) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE name = 'Duplicate'")
            duplicate_user = cursor.fetchone()
            if duplicate_user:
                print(f"Error: 'Duplicate' user found: {duplicate_user}")
            else:
                print("Success: 'Duplicate' user was not added (rollback worked).")
            
            cursor.execute("SELECT * FROM users")
            all_users = cursor.fetchall()
            print("\nCurrent users in DB:")
            for user in all_users:
                print(user)

    except Exception as e:
        print(f"An error occurred during verification: {e}")