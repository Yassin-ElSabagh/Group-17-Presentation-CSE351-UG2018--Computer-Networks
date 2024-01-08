# create_db.py
import sqlite3
import bcrypt

def create_database():
    # Connect to the SQLite database or create it if it doesn't exist
    connection = sqlite3.connect('user_database.db')
    cursor = connection.cursor()

    # Create the 'users' table if it doesn't exist
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            username TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL
        )
    ''')

    # Commit changes and close the database connection
    connection.commit()
    connection.close()

if __name__ == "__main__":
    # Call the create_database function when the script is executed
    create_database()
    print("Database created with the users table.")
