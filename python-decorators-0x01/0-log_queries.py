import sqlite3
import functools

def log_queries(func):
    """
    Decorator to log SQL queries executed by a function.
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # Assuming the SQL query is passed as the first positional argument
        if args and isinstance(args[0], str):
            query = args[0]
            print(f"Executing SQL Query: {query}")
        else:
            print("Executing a database operation (query not directly found in args).")

        return func(*args, **kwargs)
    return wrapper

@log_queries
def fetch_all_users(query):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute(query)
    results = cursor.fetchall()
    conn.close()
    return results

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
    cursor.execute("INSERT OR IGNORE INTO users (id, name, email) VALUES (1, 'Alice', 'alice@example.com')")
    cursor.execute("INSERT OR IGNORE INTO users (id, name, email) VALUES (2, 'Bob', 'bob@example.com')")
    conn.commit()
    conn.close()

if __name__ == "__main__":
    setup_database()

    # fetch users while logging the query
    users = fetch_all_users(query="SELECT * FROM users")
    print("\nFetched Users:")
    for user in users:
        print(user)

    print("\n--- Testing with another query ---")
    users_named = fetch_all_users(query="SELECT name FROM users WHERE id = 1")
    print("\nFetched User Name:")
    for name in users_named:
        print(name)