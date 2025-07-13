import sqlite3

class ExecuteQuery:
    """
    A reusable class-based context manager for executing database queries.

    This context manager handles opening and closing a SQLite database connection,
    executes a given SQL query with optional parameters, and makes the results
    available upon exiting the 'with' block. It also handles transaction
    management (commit/rollback).
    """
    def __init__(self, db_name, query, params=None):
        """
        Initializes the ExecuteQuery context manager.

        Args:
            db_name (str): The name of the SQLite database file.
            query (str): The SQL query string to execute.
            params (tuple, list, or None): Optional parameters for the query.
                                          Defaults to None.
        """
        self.db_name = db_name
        self.query = query
        self.params = params if params is not None else ()
        self.conn = None
        self.cursor = None
        self.results = None # To store results for access after __exit__

    def __enter__(self):
        """
        Enters the runtime context. Establishes a database connection,
        executes the query, and returns the cursor.
        """
        try:
            self.conn = sqlite3.connect(self.db_name)
            self.cursor = self.conn.cursor()
            print(f"Database connection to '{self.db_name}' opened.")
            print(f"Executing query: '{self.query}' with params: {self.params}")
            self.cursor.execute(self.query, self.params)
            # Fetch results immediately if it's a SELECT query
            if self.query.strip().upper().startswith("SELECT"):
                self.results = self.cursor.fetchall()
            return self.cursor # Return the cursor so user can fetch results if needed
        except sqlite3.Error as e:
            print(f"Error during query execution: {e}")
            # Re-raise the exception to be caught by __exit__ and propagated
            raise

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Exits the runtime context. Handles transaction commit/rollback
        and closes the database connection.
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
        return False # Propagate exceptions

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
                    age INTEGER,
                    email TEXT
                )
            ''')
            # Insert some sample data if it doesn't exist
            cursor.execute("INSERT OR IGNORE INTO users (id, name, age, email) VALUES (1, 'Alice', 30, 'alice@example.com')")
            cursor.execute("INSERT OR IGNORE INTO users (id, name, age, email) VALUES (2, 'Bob', 22, 'bob@example.com')")
            cursor.execute("INSERT OR IGNORE INTO users (id, name, age, email) VALUES (3, 'Charlie', 35, 'charlie@example.com')")
            cursor.execute("INSERT OR IGNORE INTO users (id, name, age, email) VALUES (4, 'David', 28, 'david@example.com')")
            conn.commit()
        print(f"Database '{db_name}' setup complete with sample data.")
    except sqlite3.Error as e:
        print(f"Error during database setup: {e}")

if __name__ == "__main__":
    DB_FILE = 'users.db'
    setup_database(DB_FILE)

    print("\n--- Executing SELECT query with parameter ---")
    query_str = "SELECT * FROM users WHERE age > ?"
    param_value = 25
    try:
        with ExecuteQuery(DB_FILE, query_str, (param_value,)) as cursor:
          
            pass # No explicit action needed here, query is executed in __enter__
        
        
        
        # Re-run the example to capture the instance
        print("\n--- Re-executing SELECT query to capture results ---")
        eq_instance = ExecuteQuery(DB_FILE, query_str, (param_value,))
        with eq_instance as cursor:
            pass # Query executed, results stored in eq_instance.results

        print(f"\nResults for '{query_str}' with age > {param_value}:")
        if eq_instance.results:
            for row in eq_instance.results:
                print(row)
        else:
            print("No results found or query was not a SELECT statement.")

    except Exception as e:
        print(f"An error occurred during query execution: {e}")

    print("\n--- Executing an INSERT query ---")
    insert_query = "INSERT INTO users (name, age, email) VALUES (?, ?, ?)"
    insert_params = ("Eva", 29, "eva@example.com")
    try:
        with ExecuteQuery(DB_FILE, insert_query, insert_params) as cursor:
            print(f"Inserted new user: {insert_params}")
            # For INSERT, results attribute will be None, but rowcount can be checked
            print(f"Rows affected: {cursor.rowcount}")
    except Exception as e:
        print(f"An error occurred during INSERT query: {e}")

    print("\n--- Verifying the inserted user ---")
    verify_query = "SELECT * FROM users WHERE name = ?"
    verify_params = ("Eva",)
    try:
        eq_verify = ExecuteQuery(DB_FILE, verify_query, verify_params)
        with eq_verify as cursor:
            pass
        print(f"\nVerification results for '{verify_query}' with name 'Eva':")
        if eq_verify.results:
            for row in eq_verify.results:
                print(row)
        else:
            print("User 'Eva' not found.")
    except Exception as e:
        print(f"An error occurred during verification query: {e}")

    print("\n--- Executing a query that causes an error (e.g., syntax error) ---")
    bad_query = "SELECT * FROM non_existent_table"
    try:
        with ExecuteQuery(DB_FILE, bad_query) as cursor:
            pass
    except sqlite3.OperationalError as e:
        print(f"Caught expected error for bad query: {e}")
    except Exception as e:
        print(f"Caught unexpected error for bad query: {e}")