# database.py
import sqlite3

def create_connection():
    return sqlite3.connect('test_management.db')

def setup_database():
    conn = create_connection()
    with conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                username TEXT NOT NULL UNIQUE,
                password TEXT NOT NULL,
                role TEXT NOT NULL
            );
        ''')
        conn.execute("INSERT OR IGNORE INTO users (name, username, password, role) VALUES ('Admin User', 'admin', 'admin', 'ADMIN')")
        conn.execute("INSERT OR IGNORE INTO users (name, username, password, role) VALUES ('Teacher User', 'teacher', 'teacher', 'TEACHER')")
        conn.execute("INSERT OR IGNORE INTO users (name, username, password, role) VALUES ('Student User', 'student', 'student', 'STUDENT')")

def authenticate_user(username, password):
    conn = create_connection()
    with conn:
        cursor = conn.cursor()
        cursor.execute("SELECT role FROM users WHERE username=? AND password=?", (username, password))
        return cursor.fetchone()
    
def get_all_users():
    conn = create_connection()
    with conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, username, password, role FROM users")
        return cursor.fetchall()

def execute_query(query, args=None):
    conn = create_connection()
    with conn:
        cursor = conn.cursor()
        if args:
            cursor.execute(query, args)
        else:
            cursor.execute(query)
        return cursor.fetchall()

def add_user(name, username, password, role):
    query = "INSERT INTO users (name, username, password, role) VALUES (?, ?, ?, ?)"
    args = (name, username, password, role)
    execute_query(query, args)

def delete_user(username):
    query = "DELETE FROM users WHERE username = ?"
    args = (username,)
    execute_query(query, args)

def update_name(username, name):
    query = "UPDATE users SET name = ? WHERE username = ?"
    args = (name, username)
    execute_query(query, args)

def update_password(username, new_password):
    query = "UPDATE users SET password = ? WHERE username = ?"
    args = (new_password, username)
    execute_query(query, args)

def update_role(username, new_role):
    query = "UPDATE users SET role = ? WHERE username = ?"
    args = (new_role, username)
    execute_query(query, args)