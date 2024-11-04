import sqlite3

def migrate_database(db_path='invite_stats.db'):
    # Connect to the existing database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Step 1: Add the new 'link_created' column
    try:
        cursor.execute("ALTER TABLE invite_stats ADD COLUMN link_created TEXT")
        print("Added 'link_created' column successfully.")
    except sqlite3.OperationalError as e:
        print(f"Column 'link_created' may already exist or another error occurred: {e}")
    
    # Step 2: Create a new table without 'phone_number' column
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS invite_stats_new (
            invite_link TEXT,
            user_id INTEGER,
            username TEXT,
            name TEXT,
            channel TEXT,
            time TEXT,
            link_created TEXT
        )
    ''')
    print("Created new table 'invite_stats_new' without 'phone_number' column.")

    # Step 3: Copy data from the old table to the new table, excluding 'phone_number'
    cursor.execute('''
        INSERT INTO invite_stats_new (invite_link, user_id, username, name, channel, time, link_created)
        SELECT invite_link, user_id, username, name, channel, time, NULL as link_created
        FROM invite_stats
    ''')
    print("Data copied to 'invite_stats_new'.")

    # Step 4: Drop the old table
    cursor.execute("DROP TABLE invite_stats")
    print("Dropped old table 'invite_stats'.")

    # Step 5: Rename the new table to the original table name
    cursor.execute("ALTER TABLE invite_stats_new RENAME TO invite_stats")
    print("Renamed 'invite_stats_new' to 'invite_stats'.")

    # Commit changes and close connection
    conn.commit()
    conn.close()
    print("Database migration completed successfully.")

# Run the migration
if __name__ == "__main__":
    migrate_database()
