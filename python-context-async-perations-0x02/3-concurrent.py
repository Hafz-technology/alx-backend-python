import asyncio
import time
import aiosqlite


# Setup a dummy users.db for testing
async def setup_database(db_name='users.db'):
    """
    Sets up a simple 'users' table in the specified SQLite database
    and inserts some sample data if it doesn't already exist.
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
        # Insert some sample data if it doesn't exist
        # Include users older than 40 for testing async_fetch_older_users
        await db.execute("INSERT OR IGNORE INTO users (id, name, age, email) VALUES (1, 'Alice', 30, 'alice@example.com')")
        await db.execute("INSERT OR IGNORE INTO users (id, name, age, email) VALUES (2, 'Bob', 22, 'bob@example.com')")
        await db.execute("INSERT OR IGNORE INTO users (id, name, age, email) VALUES (3, 'Charlie', 45, 'charlie@example.com')")
        await db.execute("INSERT OR IGNORE INTO users (id, name, age, email) VALUES (4, 'David', 28, 'david@example.com')")
        await db.execute("INSERT OR IGNORE INTO users (id, name, age, email) VALUES (5, 'Eve', 50, 'eve@example.com')")
        await db.commit()
    print(f"Database '{db_name}' setup complete with sample data.")

async def async_fetch_users(db_name='users.db'):
    """
    Asynchronously fetches all users from the database.
    Simulates a network delay.
    """
    print("Starting async_fetch_users...")
    async with aiosqlite.connect(db_name) as db:
        await asyncio.sleep(1) # Simulate I/O bound operation
        cursor = await db.execute("SELECT id, name, age, email FROM users")
        users = await cursor.fetchall()
        await cursor.close()
    print("Finished async_fetch_users.")
    return users

async def async_fetch_older_users(db_name='users.db', age_threshold=40):
    """
    Asynchronously fetches users older than a specified age from the database.
    Simulates a network delay.
    """
    print(f"Starting async_fetch_older_users (age > {age_threshold})...")
    async with aiosqlite.connect(db_name) as db:
        await asyncio.sleep(1.5) # Simulate a slightly longer I/O bound operation
        cursor = await db.execute("SELECT id, name, age, email FROM users WHERE age > ?", (age_threshold,))
        older_users = await cursor.fetchall()
        await cursor.close()
    print("Finished async_fetch_older_users.")
    return older_users

async def fetch_concurrently():
    """
    Executes multiple asynchronous database queries concurrently using asyncio.gather.
    """
    db_file = 'users.db'
    await setup_database(db_file) # Ensure database is set up before queries

    print("\n--- Running concurrent database queries ---")
    start_time = time.time()

    # Use asyncio.gather to run both functions concurrently
    all_users, older_users = await asyncio.gather(
        async_fetch_users(db_file),
        async_fetch_older_users(db_file)
    )

    end_time = time.time()
    print(f"\nConcurrent fetch completed in {end_time - start_time:.4f} seconds.")

    print("\nAll Users:")
    for user in all_users:
        print(user)

    print(f"\nUsers Older Than 40:")
    for user in older_users:
        print(user)

if __name__ == "__main__":
    # Run the main asynchronous function
    asyncio.run(fetch_concurrently())