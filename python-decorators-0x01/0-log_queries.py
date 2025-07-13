import sqlite3
import functools

#### decorator to log SQL queries
def log_queries(func):
    """
    A decorator that logs the SQL query passed to the decorated function
    before its execution.
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # Determine where the query argument is.
        # Assuming the query is either the first positional argument
        # or a keyword argument named 'query'.
        query = None
        if args:
            # If the first argument is a string, assume it's the query
            if isinstance(args[0], str):
                query = args[0]
        if 'query' in kwargs:
            query = kwargs['query']

        if query:
            print(f"Executing SQL Query: {query}")
        else:
            print("Executing function without a detectable SQL query argument.")

        # Call the original function with its arguments
        return func(*args, **kwargs)
    return wrapper

@log_queries
def fetch_all_users(query):
    """
    Fetches all users from the 'users.db' database using the given query.
    """
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute(query)
    results = cursor.fetchall()
    conn.close()
    return results

# Example Usage:
# First, let's create a dummy database and table for demonstration
def setup_database():
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL
        )
    ''')
    # Insert some dummy data if the table is empty
    cursor.execute("INSERT OR IGNORE INTO users (id, name, email) VALUES (1, 'Alice', 'alice@example.com')")
    cursor.execute("INSERT OR IGNORE INTO users (id, name, email) VALUES (2, 'Bob', 'bob@example.com')")
    conn.commit()
    conn.close()

# Set up the database before fetching
setup_database()

#### fetch users while logging the query
print("\n--- Fetching all users ---")
users = fetch_all_users(query="SELECT * FROM users")
print("Fetched users:", users)

print("\n--- Fetching a specific user ---")
user_bob = fetch_all_users("SELECT * FROM users WHERE name = 'Bob'")
print("Fetched Bob:", user_bob)

print("\n--- Testing with a non-query function (for decorator robustness) ---")
@log_queries
def simple_function(message):
    print(f"Inside simple_function: {message}")
    return "Done"

simple_function("Hello World")

