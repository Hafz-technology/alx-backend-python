import time
import sqlite3
import functools

# Global cache for query results
query_cache = {}

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

def cache_query(func):
    """
    Decorator that caches query results based on the SQL query string.
    Assumes the SQL query string is the second positional argument (after 'conn').
    """
    @functools.wraps(func)
    def wrapper(conn, query, *args, **kwargs):
        # The cache key will be the query string
        cache_key = query

        if cache_key in query_cache:
            print(f"Cache hit for query: '{query}'")
            return query_cache[cache_key]
        else:
            print(f"Cache miss for query: '{query}'. Executing database query...")
            # Execute the original function with all its arguments
            # The 'conn' is the first argument, 'query' is the second
            result = func(conn, query, *args, **kwargs)
            query_cache[cache_key] = result
            print(f"Query result cached for: '{query}'")
            return result
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
    cursor.execute("INSERT OR IGNORE INTO users (id, name, email) VALUES (3, 'Charlie', 'charlie@example.com')")
    conn.commit()
    conn.close()
    print("Database setup complete with sample data.")

@with_db_connection
@cache_query
def fetch_users_with_cache(conn, query):
    """
    Fetches users from the database.
    This function's results will be cached by the @cache_query decorator.
    """
    cursor = conn.cursor()
    cursor.execute(query)
    # Simulate some processing time to make caching more apparent
    time.sleep(0.5)
    return cursor.fetchall()

@with_db_connection
@cache_query
def fetch_user_by_id_with_cache(conn, query, user_id):
    """
    Fetches a single user by ID. Demonstrates caching with parameters.
    Note: The 'query' string itself is the cache key, so parameterized queries
    would need a more sophisticated caching key if parameters vary but query structure is same.
    For this task, we assume the exact query string is the key.
    """
    cursor = conn.cursor()
    cursor.execute(query, (user_id,))
    time.sleep(0.3)
    return cursor.fetchone()

if __name__ == "__main__":
    setup_database()

    print("\n--- First call to fetch_users_with_cache (should hit DB) ---")
    start_time = time.time()
    users = fetch_users_with_cache(query="SELECT * FROM users")
    end_time = time.time()
    print(f"Fetched users: {users}")
    print(f"Time taken: {end_time - start_time:.4f} seconds")
    print(f"Current cache: {query_cache.keys()}")

    print("\n--- Second call to fetch_users_with_cache (should use cache) ---")
    start_time = time.time()
    users_again = fetch_users_with_cache(query="SELECT * FROM users")
    end_time = time.time()
    print(f"Fetched users again: {users_again}")
    print(f"Time taken: {end_time - start_time:.4f} seconds (should be faster due to cache)")
    print(f"Current cache: {query_cache.keys()}")

    print("\n--- Third call with a different query (should hit DB) ---")
    start_time = time.time()
    names = fetch_users_with_cache(query="SELECT name FROM users WHERE id > 1")
    end_time = time.time()
    print(f"Fetched names: {names}")
    print(f"Time taken: {end_time - start_time:.4f} seconds")
    print(f"Current cache: {query_cache.keys()}")

    print("\n--- Fourth call with the first query (should use cache) ---")
    start_time = time.time()
    users_third_time = fetch_users_with_cache(query="SELECT * FROM users")
    end_time = time.time()
    print(f"Fetched users third time: {users_third_time}")
    print(f"Time taken: {end_time - start_time:.4f} seconds (should be faster due to cache)")
    print(f"Current cache: {query_cache.keys()}")

    print("\n--- Testing fetch_user_by_id_with_cache ---")
    print("--- First call for user 1 (should hit DB) ---")
    start_time = time.time()
    user_1 = fetch_user_by_id_with_cache(query="SELECT * FROM users WHERE id = ?", user_id=1)
    end_time = time.time()
    print(f"Fetched user 1: {user_1}")
    print(f"Time taken: {end_time - start_time:.4f} seconds")
    # Note: For parameterized queries, the cache key here is "SELECT * FROM users WHERE id = ?"
    # If we wanted to cache based on (query_string, user_id), the cache_key logic would need to be adjusted.
    # For this task, the instruction implies caching based on the query string itself.
    print(f"Current cache: {query_cache.keys()}")


    print("\n--- Second call for user 1 (should use cache for the query string) ---")
    start_time = time.time()
    user_1_again = fetch_user_by_id_with_cache(query="SELECT * FROM users WHERE id = ?", user_id=1)
    end_time = time.time()
    print(f"Fetched user 1 again: {user_1_again}")
    print(f"Time taken: {end_time - start_time:.4f} seconds (should be faster for the query string)")
    print(f"Current cache: {query_cache.keys()}")

    print("\n--- Clear the cache for demonstration ---")
    query_cache.clear()
    print(f"Cache cleared. Current cache: {query_cache.keys()}")

    print("\n--- Call after cache clear (should hit DB again) ---")
    start_time = time.time()
    users_after_clear = fetch_users_with_cache(query="SELECT * FROM users")
    end_time = time.time()
    print(f"Fetched users after clear: {users_after_clear}")
    print(f"Time taken: {end_time - start_time:.4f} seconds")
    print(f"Current cache: {query_cache.keys()}")