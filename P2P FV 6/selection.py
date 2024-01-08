import sqlite3

def fetch_all_data():
    try:
        # Connect to the SQLite database
        connection = sqlite3.connect('user_database.db')
        cursor = connection.cursor()

        # Query to select all data from the 'users' table
        query = "SELECT * FROM users"
        cursor.execute(query)

        # Fetch and print all rows from the table
        rows = cursor.fetchall()
        for row in rows:
            print(row)

    except sqlite3.Error as e:
        print(f"Database error: {e}")
    finally:
        if connection:
            connection.close()

if __name__ == "__main__":
    fetch_all_data()
