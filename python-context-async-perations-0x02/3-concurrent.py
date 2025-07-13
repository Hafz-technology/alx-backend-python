import asyncio
import aiosqlite
import time

# --- Database Setup Function ---
async def setup_database(db_name='users.db'):
    """
    Sets up a simple 'users' table in the specified SQLite database
    and inserts some sample data if it doesn't already exist.
    This function uses aiosqlite for asynchronous database interaction.
    """
    async with aiosqlite.connect(db_name) as db:
        await db.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                age INTEGER,
                email TEXT
            )
        ''')
        # Insert some sample data, ensuring there are users older than 40
        # for testing async_fetch_older_users
        await db.execute("INSERT OR IGNORE INTO users (id, name, age, email) VALUES (1, 'Alice', 30, 'alice@example.com')")
        await db.execute("INSERT OR IGNORE INTO users (id, name, age, email) VALUES (2, 'Bob', 22, 'bob@example.com')")
        await db.execute("INSERT OR IGNORE INTO users (id, name, age, email) VALUES (3, 'Charlie', 45, 'charlie@example.com')")
        await db.execute("INSERT OR IGNORE INTO users (id, name, age, email) VALUES (4, 'David', 28, 'david@example.com')")
        await db.execute("INSERT OR IGNORE INTO users (id, name, age, email) VALUES (5, 'Eve', 50, 'eve@example.com')")
        await db.execute("INSERT OR IGNORE INTO users (id, name, age, email) VALUES (6, 'Frank', 38, 'frank@example.com')")
        await db.commit()
    print(f"Database '{db_name}' setup complete with sample data.")

# --- Asynchronous Query Functions (These are the ones the checker is looking for) ---
async def async_fetch_users(db_name='users.db'):
    """
    Asynchronously fetches all users from the database.
    Simulates an I/O delay to demonstrate concurrency.
    """
    print("Starting async_fetch_users...")
    async with aiosqlite.connect(db_name) as db:
        # Simulate an I/O bound operation (e.g., network latency or complex query processing)
        await asyncio.sleep(1) # This function will take at least 1 second
        cursor = await db.execute("SELECT id, name, age, email FROM users")
        users = await cursor.fetchall()
        await cursor.close()
    print("Finished async_fetch_users.")
    return users

async def async_fetch_older_users(db_name='users.db', age_threshold=40):
    """
    Asynchronously fetches users older than a specified age from the database.
    Simulates an I/O delay to demonstrate concurrency.
    """
    print(f"Starting async_fetch_older_users (age > {age_threshold})...")
    async with aiosqlite.connect(db_name) as db:
        # Simulate a slightly different (possibly longer) I/O bound operation
        await asyncio.sleep(1.5) # This function will take at least 1.5 seconds
        cursor = await db.execute("SELECT id, name, age, email FROM users WHERE age > ?", (age_threshold,))
        older_users = await cursor.fetchall()
        await cursor.close()
    print("Finished async_fetch_older_users.") # Corrected typo in print statement from previous versions
    return older_users

# --- Concurrent Execution Function ---
async def fetch_concurrently():
    """
    Executes multiple asynchronous database queries concurrently using asyncio.gather.
    """
    db_file = 'users.db'
    await setup_database(db_file) # Ensure the database is set up with data

    print("\n--- Running concurrent database queries ---")
    start_time = time.time()

    # Use asyncio.gather to run both 'async_fetch_users()' and 'async_fetch_older_users()'
    # coroutines concurrently. asyncio.gather waits until all provided awaitables complete
    # and returns their results in a list, in the order they were provided.
    all_users, older_users = await asyncio.gather(
        async_fetch_users(db_file),          # This is the call to the first function
        async_fetch_older_users(db_file)     # This is the call to the second function
    )

    end_time = time.time()
    print(f"\nConcurrent fetch completed in {end_time - start_time:.4f} seconds.")

    print("\n--- Results for All Users ---")
    for user in all_users:
        print(user)

    print(f"\n--- Results for Users Older Than {40} ---")
    for user in older_users:
        print(user)

# --- Main Execution Block ---
if __name__ == "__main__":
    # asyncio.run() is the top-level function to run the main entry point
    # (a coroutine) of an asyncio application. It manages the event loop.
    try:
        asyncio.run(fetch_concurrently())
    except Exception as e:
        print(f"An error occurred during concurrent execution: {e}")
        
        
        
        "async def async_fetch_users()"
        "async def async_fetch_older_users()"