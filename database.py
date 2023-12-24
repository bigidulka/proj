# database.py
import sqlite3

# Database connection functions

def create_connection():
    return sqlite3.connect('test_management.db')

def setup_database():
    # Create tables in the database
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
        
        conn.execute('''
            CREATE TABLE IF NOT EXISTS groups (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE
            );
        ''')

        # Create Tests Table
        conn.execute('''
            CREATE TABLE IF NOT EXISTS tests (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                description TEXT,
                total_marks INTEGER,
                attempts INTEGER NOT NULL,
                creator_id INTEGER,  -- Foreign key referencing the users table
                FOREIGN KEY(creator_id) REFERENCES users(id)
            );
        ''')

        # Create UserGroups Table (if needed for many-to-many relationship)
        conn.execute('''
            CREATE TABLE IF NOT EXISTS user_groups (
                user_id INTEGER NOT NULL,
                group_id INTEGER NOT NULL,
                PRIMARY KEY(user_id, group_id),
                FOREIGN KEY(user_id) REFERENCES users(id),
                FOREIGN KEY(group_id) REFERENCES groups(id)
            );
        ''')
        
        conn.execute('''
            CREATE TABLE IF NOT EXISTS student_tests (
                student_id INTEGER NOT NULL,
                test_id INTEGER NOT NULL,
                assigner_id INTEGER NOT NULL,
                FOREIGN KEY(student_id) REFERENCES users(id),
                FOREIGN KEY(test_id) REFERENCES tests(id),
                FOREIGN KEY(assigner_id) REFERENCES users(id),
                PRIMARY KEY(student_id, test_id)
            );
        ''')
        
        conn.execute('''
            CREATE TABLE IF NOT EXISTS questions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                test_id INTEGER NOT NULL,
                text TEXT NOT NULL,
                type TEXT NOT NULL,
                FOREIGN KEY(test_id) REFERENCES tests(id)
            );
        ''')

        conn.execute('''
            CREATE TABLE IF NOT EXISTS answers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                question_id INTEGER NOT NULL,
                text TEXT NOT NULL,
                is_correct BOOLEAN NOT NULL,
                FOREIGN KEY(question_id) REFERENCES questions(id)
            );
        ''')
        
        # Insert initial admin, teacher, and student users
        conn.execute("INSERT OR IGNORE INTO users (name, username, password, role) VALUES ('Admin User', 'admin', 'admin', 'ADMIN')")
        conn.execute("INSERT OR IGNORE INTO users (name, username, password, role) VALUES ('Teacher User', 'teacher', 'teacher', 'TEACHER')")
        conn.execute("INSERT OR IGNORE INTO users (name, username, password, role) VALUES ('Student User', 'student', 'student', 'STUDENT')")


# User-related functions

def authenticate_user(username, password):
    # Authenticate a user
    conn = create_connection()
    with conn:
        cursor = conn.cursor()
        cursor.execute("SELECT role FROM users WHERE username=? AND password=?", (username, password))
        return cursor.fetchone()
    
def get_all_users():
    # Get a list of all users
    conn = create_connection()
    with conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, username, password, role FROM users")
        return cursor.fetchall()

# Generic database query execution function

def execute_query(query, args=None):
    # Execute arbitrary SQL queries
    conn = create_connection()
    with conn:
        cursor = conn.cursor()
        if args:
            cursor.execute(query, args)
        else:
            cursor.execute(query)
        conn.commit()
        return cursor.fetchall()

# Functions for managing users

def add_user(name, username, password, role):
    # Add a new user
    query = "INSERT INTO users (name, username, password, role) VALUES (?, ?, ?, ?)"
    args = (name, username, password, role)
    execute_query(query, args)

def delete_user(username):
    # Delete a user by username
    query = "DELETE FROM users WHERE username = ?"
    args = (username,)
    execute_query(query, args)

def update_name(username, name):
    # Update the name of a user
    query = "UPDATE users SET name = ? WHERE username = ?"
    args = (name, username)
    execute_query(query, args)

def update_password(username, new_password):
    # Update the password of a user
    query = "UPDATE users SET password = ? WHERE username = ?"
    args = (new_password, username)
    execute_query(query, args)

def update_role(username, new_role):
    # Update the role of a user
    query = "UPDATE users SET role = ? WHERE username = ?"
    args = (new_role, username)
    execute_query(query, args)
    
def check_existing_user(username):
    # Check if a user with the given username already exists
    query = "SELECT username FROM users WHERE username = ?"
    args = (username,)
    existing_user = execute_query(query, args)
    return existing_user is not None


# Functions for managing groups

def add_group(name):
    # Add a new group
    query = "INSERT INTO groups (name) VALUES (?)"
    args = (name,)
    execute_query(query, args)

def delete_group(name):
    # Delete a group by name
    query = "DELETE FROM groups WHERE name = ?"
    args = (name,)
    execute_query(query, args)

def get_all_groups():
    # Get a list of all groups
    query = "SELECT id, name FROM groups"
    conn = create_connection()
    with conn:
        cursor = conn.cursor()
        cursor.execute(query)
        groups = [{"id": row[0], "name": row[1]} for row in cursor.fetchall()]
    return groups

# Functions for managing tests

def add_test(name, description, total_marks, creator_id):
    query = "INSERT INTO tests (name, description, total_marks, creator_id) VALUES (?, ?, ?, ?)"
    args = (name, description, total_marks, creator_id)
    execute_query(query, args)

def save_test_to_database(test_name, attempts, questions, creator_id):
    conn = create_connection()
    with conn:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO tests (name, attempts, creator_id) VALUES (?, ?, ?)", (test_name, attempts, creator_id))
        test_id = cursor.lastrowid

        for question in questions:
            cursor.execute("INSERT INTO questions (test_id, text, type) VALUES (?, ?, ?)", 
                           (test_id, question['text'], question['type']))
            question_id = cursor.lastrowid

            for answer in question['answers']:
                cursor.execute("INSERT INTO answers (question_id, text, is_correct) VALUES (?, ?, ?)", 
                               (question_id, answer['text'], answer['is_correct']))

        conn.commit()


    

def get_tests_for_student(student_id):
    query = """
    SELECT test_id FROM student_tests WHERE student_id = ?
    """
    args = (student_id,)
    return [row[0] for row in execute_query(query, args)]


def assign_test_to_student(test_id, student_id, assigner_id):
    query = """
    INSERT INTO student_tests (student_id, test_id, assigner_id) VALUES (?, ?, ?)
    ON CONFLICT(student_id, test_id) DO NOTHING
    """
    args = (student_id, test_id, assigner_id)
    execute_query(query, args)
    
def authenticate_user(username, password):
    conn = create_connection()
    with conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, role FROM users WHERE username=? AND password=?", (username, password))
        return cursor.fetchone()  # This now returns (id, role)


# Functions for managing students

def get_all_students():
    conn = create_connection()
    with conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT u.id, u.name, u.username, u.role, g.name as group_name, GROUP_CONCAT(t.name) as tests
            FROM users u
            LEFT JOIN user_groups ug ON u.id = ug.user_id
            LEFT JOIN groups g ON ug.group_id = g.id
            LEFT JOIN student_tests st ON u.id = st.student_id
            LEFT JOIN tests t ON st.test_id = t.id
            WHERE u.role = 'STUDENT'
            GROUP BY u.id
        """)
        students = [{"id": row[0], "name": row[1], "username": row[2], "role": row[3], "group": row[4], "tests": row[5]} for row in cursor.fetchall()]
        return students

# Functions for managing user data retrieval

def get_all_users_as_dicts():
    # Get a list of all users as dictionaries
    conn = create_connection()
    with conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, username, password, role FROM users")
        users = [{"id": row[0], "name": row[1], "username": row[2], "password": row[3], "role": row[4]} for row in cursor.fetchall()]
    return users

# Functions for managing tests assigned to teachers

def delete_test(test_name):
    # Delete a test by name
    query = "DELETE FROM tests WHERE name = ?"
    args = (test_name,)
    execute_query(query, args)

def get_test_with_questions_and_answers(test_id):
    query = """
    SELECT t.id as test_id, t.name as test_name, t.description, t.total_marks, t.attempts,
           q.id as question_id, q.text as question_text, q.type as question_type,
           a.id as answer_id, a.text as answer_text, a.is_correct
    FROM tests t
    LEFT JOIN questions q ON t.id = q.test_id
    LEFT JOIN answers a ON q.id = a.question_id
    WHERE t.id = ?
    ORDER BY q.id, a.id
    """
    args = (test_id,)
    conn = create_connection()
    with conn:
        cursor = conn.cursor()
        cursor.execute(query, args)
        rows = cursor.fetchall()

    # Transform the rows into a structured format (e.g., a dictionary)
    test_info = {}
    for row in rows:
        if row[0] not in test_info:
            test_info[row[0]] = {
                'test_id': row[0],
                'test_name': row[1],
                'description': row[2],
                'total_marks': row[3],
                'attempts': row[4],
                'questions': {}
            }

        if row[5] not in test_info[row[0]]['questions']:
            test_info[row[0]]['questions'][row[5]] = {
                'question_id': row[5],
                'question_text': row[6],
                'question_type': row[7],
                'answers': []
            }

        test_info[row[0]]['questions'][row[5]]['answers'].append({
            'answer_id': row[8],
            'answer_text': row[9],
            'is_correct': row[10]
        })

    return test_info

def get_test_details(test_name):
    query = """
    SELECT t.id, t.name, t.attempts, t.creator_id,
           q.id, q.text, q.type,
           a.id, a.text, a.is_correct
    FROM tests t
    LEFT JOIN questions q ON t.id = q.test_id
    LEFT JOIN answers a ON q.id = a.question_id
    WHERE t.name = ?
    ORDER BY q.id, a.id
    """
    args = (test_name,)
    conn = create_connection()
    with conn:
        cursor = conn.cursor()
        cursor.execute(query, args)
        rows = cursor.fetchall()
        if not rows:
            return None

        test_info = {'questions': []}
        question = None

        for row in rows:
            if test_info.get('id') is None:
                test_info.update({'id': row[0], 'name': row[1], 'attempts': row[2], 'creator_id': row[3]})

            if question is None or question['id'] != row[4]:
                question = {'id': row[4], 'text': row[5], 'type': row[6], 'answers': []}
                test_info['questions'].append(question)

            if row[7] is not None:
                answer = {'id': row[7], 'text': row[8], 'is_correct': row[9]}
                question['answers'].append(answer)

        return test_info
    
def update_test_in_database(test_name, attempts, questions, creator_id):
    conn = create_connection()
    with conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE tests SET attempts = ?, creator_id = ? WHERE name = ?", (attempts, creator_id, test_name))
        test_id = cursor.execute("SELECT id FROM tests WHERE name = ?", (test_name,)).fetchone()[0]

        for question in questions:
            if 'id' in question:
                cursor.execute("UPDATE questions SET text = ?, type = ? WHERE id = ?", (question['text'], question['type'], question['id']))
                question_id = question['id']
            else:
                cursor.execute("INSERT INTO questions (test_id, text, type) VALUES (?, ?, ?)", (test_id, question['text'], question['type']))
                question_id = cursor.lastrowid

            cursor.execute("DELETE FROM answers WHERE question_id = ?", (question_id,))
            for answer in question['answers']:
                cursor.execute("INSERT INTO answers (question_id, text, is_correct) VALUES (?, ?, ?)", (question_id, answer['text'], answer['is_correct']))

        conn.commit()

def get_student_group(student_id):
    # Get the current group of a student
    query = "SELECT group_id FROM user_groups WHERE user_id = ?"
    args = (student_id,)
    return execute_query(query, args)

def set_student_group(student_id, group_id):
    conn = create_connection()
    with conn:
        cursor = conn.cursor()
        if group_id is None:
            cursor.execute("DELETE FROM user_groups WHERE user_id = ?", (student_id,))
        else:
            cursor.execute("""
                INSERT INTO user_groups (user_id, group_id) VALUES (?, ?)
                ON CONFLICT(user_id, group_id) DO UPDATE SET group_id = excluded.group_id
            """, (student_id, group_id))
        conn.commit()

    
def get_all_tests_as_dict():
    # Get a list of all tests as dictionaries
    query = "SELECT id, name FROM tests"
    return execute_query(query)



    
def reset_student_group(student_id):
    conn = create_connection()
    with conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM user_groups WHERE user_id = ?", (student_id,))
        conn.commit()
        
def remove_test_from_student(test_id, student_id):
    conn = create_connection()
    with conn:
        cursor = conn.cursor()
        query = "DELETE FROM student_tests WHERE student_id = ? AND test_id = ?"
        args = (student_id, test_id)
        cursor.execute(query, args)
        conn.commit()
        
def get_group_id_by_name(group_name):
    conn = create_connection()
    with conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM groups WHERE name = ?", (group_name,))
        result = cursor.fetchone()
        return result[0] if result else None
    
def assign_test_to_all_students_in_group(test_id, group_id):
    conn = create_connection()
    with conn:
        cursor = conn.cursor()
        # Insert a test assignment for each student in the group
        cursor.execute("""
            INSERT INTO student_tests (student_id, test_id)
            SELECT user_id, ? FROM user_groups WHERE group_id = ?
        """, (test_id, group_id))
        conn.commit()

def remove_test_assignment_from_group(test_id, group_id):
    print(test_id, group_id)
    conn = create_connection()
    with conn:
        cursor = conn.cursor()
        # Delete the test assignment for each student in the group
        cursor.execute("""
            DELETE FROM student_tests
            WHERE test_id = ? AND student_id IN (
                SELECT user_id FROM user_groups WHERE group_id = ?
            )
        """, (test_id, group_id))
        conn.commit()

def assign_test_to_group_students(test_id, group_id, assigner_id):
    query = """
    INSERT OR IGNORE INTO student_tests (student_id, test_id, assigner_id)
    SELECT user_id, ?, ? FROM user_groups WHERE group_id = ?
    """
    args = (test_id, assigner_id, group_id)
    execute_query(query, args)

    
def get_teachers_tests():
    # Modified query to fetch all tests created by teachers
    query = """
        SELECT u.name AS teacher_name, GROUP_CONCAT(t.name) AS tests
        FROM users u
        LEFT JOIN tests t ON u.id = t.creator_id
        WHERE u.role = 'TEACHER'
        GROUP BY u.name
    """
    conn = create_connection()
    with conn:
        cursor = conn.cursor()
        cursor.execute(query)
        teachers_tests = [{"teacher_name": row[0], "tests": row[1]} for row in cursor.fetchall()]
    return teachers_tests

def get_tests_by_teacher(teacher_name):
    query = """
    SELECT t.id, t.name
    FROM tests t
    JOIN users u ON t.creator_id = u.id
    WHERE u.name = ?
    """
    args = (teacher_name,)
    conn = create_connection()
    with conn:
        cursor = conn.cursor()
        cursor.execute(query, args)
        return [{"id": row[0], "name": row[1]} for row in cursor.fetchall()]
    
def get_tests_by_teacher_id(teacher_id):
    query = """
    SELECT t.id, t.name, t.description, t.total_marks, t.attempts, u.name as created_by
    FROM tests t
    LEFT JOIN users u ON t.creator_id = u.id
    WHERE t.creator_id = ?
    """
    args = (teacher_id,)
    conn = create_connection()
    with conn:
        cursor = conn.cursor()
        cursor.execute(query, args)
        tests = [dict(zip([column[0] for column in cursor.description], row)) for row in cursor.fetchall()]
    return tests

def get_all_tests():
    query = """
    SELECT t.id, t.name, t.description, t.total_marks, t.attempts, u.name as created_by
    FROM tests t
    LEFT JOIN users u ON t.creator_id = u.id
    """
    conn = create_connection()
    with conn:
        cursor = conn.cursor()
        cursor.execute(query)
        tests = [dict(zip([column[0] for column in cursor.description], row)) for row in cursor.fetchall()]
    return tests


def updateTestDescription(test_id, new_description):
    query = "UPDATE tests SET description = ? WHERE id = ?"
    args = (new_description, test_id)
    execute_query(query, args)
    
def get_user_info(user_id):
    query = "SELECT name, username, password FROM users WHERE id = ?"
    args = (user_id,)
    conn = create_connection()
    with conn:
        cursor = conn.cursor()
        cursor.execute(query, args)
        user_info = cursor.fetchone()
        return {"name": user_info[0], "username": user_info[1], "password": user_info[2]} if user_info else None


def update_user_info(user_id, name, username, password):
    query = "UPDATE users SET name = ?, username = ?, password = ? WHERE id = ?"
    args = (name, username, password, user_id)
    execute_query(query, args)
    
def get_assigned_tests_for_student(student_id):
    query = """
    SELECT 
        t.id, t.name, t.description, t.total_marks, t.attempts, 
        creator.name as creator_name, assigner.name as assigner_name
    FROM student_tests st
    JOIN tests t ON st.test_id = t.id
    LEFT JOIN users creator ON t.creator_id = creator.id
    LEFT JOIN users assigner ON st.assigner_id = assigner.id
    WHERE st.student_id = ?
    """
    args = (student_id,)
    conn = create_connection()
    tests = []
    with conn:
        cursor = conn.cursor()
        cursor.execute(query, args)
        tests = [dict(zip([column[0] for column in cursor.description], row)) for row in cursor.fetchall()]
    return tests
