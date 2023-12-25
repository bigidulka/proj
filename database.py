# database.py

import sqlite3


def create_connection():
    return sqlite3.connect("test_management.db")


def setup_database():
    conn = create_connection()
    with conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                username TEXT NOT NULL UNIQUE,
                password TEXT NOT NULL,
                role TEXT NOT NULL
            );
        """
        )

        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS groups (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE
            );
        """
        )

        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS tests (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                description TEXT,
                total_marks INTEGER,
                attempts INTEGER NOT NULL,
                creator_id INTEGER,  -- Foreign key referencing the users table
                FOREIGN KEY(creator_id) REFERENCES users(id)
            );
        """
        )

        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS user_groups (
                user_id INTEGER NOT NULL,
                group_id INTEGER NOT NULL,
                PRIMARY KEY(user_id, group_id),
                FOREIGN KEY(user_id) REFERENCES users(id),
                FOREIGN KEY(group_id) REFERENCES groups(id)
            );
        """
        )

        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS student_tests (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id INTEGER NOT NULL,
                test_id INTEGER NOT NULL,
                assigner_id INTEGER NOT NULL,
                remaining_attempts INTEGER,
                FOREIGN KEY(student_id) REFERENCES users(id),
                FOREIGN KEY(test_id) REFERENCES tests(id),
                FOREIGN KEY(assigner_id) REFERENCES users(id),
                UNIQUE(student_id, test_id)
            );
            """
        )

        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS questions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                test_id INTEGER NOT NULL,
                text TEXT NOT NULL,
                type TEXT NOT NULL,
                FOREIGN KEY(test_id) REFERENCES tests(id)
            );
        """
        )

        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS answers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                question_id INTEGER NOT NULL,
                text TEXT NOT NULL,
                is_correct BOOLEAN NOT NULL,
                FOREIGN KEY(question_id) REFERENCES questions(id)
            );
        """
        )

        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS student_answers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                test_results_id INTEGER NOT NULL,
                question_id INTEGER NOT NULL,
                selected_answer INTEGER NOT NULL,
                FOREIGN KEY(test_results_id) REFERENCES test_results(id),
                FOREIGN KEY(question_id) REFERENCES questions(id)
            );
        """
        )

        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS test_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id INTEGER NOT NULL,
                test_id INTEGER NOT NULL,
                FOREIGN KEY(student_id) REFERENCES users(id),
                FOREIGN KEY(test_id) REFERENCES tests(id)
            );
        """
        )

        conn.execute(
            "INSERT OR IGNORE INTO users (name, username, password, role) VALUES ('Admin User', 'admin', 'admin', 'ADMIN')"
        )
        conn.execute(
            "INSERT OR IGNORE INTO users (name, username, password, role) VALUES ('Teacher User', 'teacher', 'teacher', 'TEACHER')"
        )
        conn.execute(
            "INSERT OR IGNORE INTO users (name, username, password, role) VALUES ('Student User', 'student', 'student', 'STUDENT')"
        )


def authenticate_user(username, password):
    conn = create_connection()
    with conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT role FROM users WHERE username=? AND password=?",
            (username, password),
        )
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
        conn.commit()
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


def update_role(username, new_role):
    query = "UPDATE users SET role = ? WHERE username = ?"
    args = (new_role, username)
    execute_query(query, args)


def add_group(name):
    query = "INSERT INTO groups (name) VALUES (?)"
    args = (name,)
    execute_query(query, args)


def delete_group(name):
    query = "DELETE FROM groups WHERE name = ?"
    args = (name,)
    execute_query(query, args)


def get_all_groups():
    query = "SELECT id, name FROM groups"
    conn = create_connection()
    with conn:
        cursor = conn.cursor()
        cursor.execute(query)
        groups = [{"id": row[0], "name": row[1]} for row in cursor.fetchall()]
    return groups


def get_tests_for_student(student_id):
    query = """
    SELECT test_id FROM student_tests WHERE student_id = ?
    """
    args = (student_id,)
    return [row[0] for row in execute_query(query, args)]


def assign_test_to_student(test_id, student_id, assigner_id):
    conn = create_connection()
    with conn:
        cursor = conn.cursor()

        cursor.execute("SELECT attempts FROM tests WHERE id = ?", (test_id,))
        result = cursor.fetchone()
        attempts = result[0]

        query = """
        INSERT INTO student_tests (student_id, test_id, assigner_id, remaining_attempts)
        VALUES (?, ?, ?, ?)
        ON CONFLICT(student_id, test_id) DO UPDATE SET remaining_attempts = ?
        """
        args = (student_id, test_id, assigner_id, attempts, attempts)
        cursor.execute(query, args)
        conn.commit()


def authenticate_user(username, password):
    conn = create_connection()
    with conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, role FROM users WHERE username=? AND password=?",
            (username, password),
        )
        return cursor.fetchone()


def get_all_students():
    conn = create_connection()
    with conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT u.id, u.name, u.username, u.role, g.name as group_name, GROUP_CONCAT(t.name) as tests
            FROM users u
            LEFT JOIN user_groups ug ON u.id = ug.user_id
            LEFT JOIN groups g ON ug.group_id = g.id
            LEFT JOIN student_tests st ON u.id = st.student_id
            LEFT JOIN tests t ON st.test_id = t.id
            WHERE u.role = 'STUDENT'
            GROUP BY u.id
        """
        )
        students = [
            {
                "id": row[0],
                "name": row[1],
                "username": row[2],
                "role": row[3],
                "group": row[4],
                "tests": row[5],
            }
            for row in cursor.fetchall()
        ]
        return students


def get_all_users_as_dicts():
    conn = create_connection()
    with conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, username, password, role FROM users")
        users = [
            {
                "id": row[0],
                "name": row[1],
                "username": row[2],
                "password": row[3],
                "role": row[4],
            }
            for row in cursor.fetchall()
        ]
    return users


def get_all_tests_as_dict():
    query = "SELECT id, name FROM tests"
    return execute_query(query)

# -----------------------


def set_student_group(student_id, group_id):
    conn = create_connection()
    with conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT OR REPLACE INTO user_groups (user_id, group_id) VALUES (?, ?)
        """,
            (student_id, group_id),
        )
        conn.commit()


def set_student_group(student_id, group_id):
    conn = create_connection()
    with conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM user_groups WHERE user_id = ?", (student_id,))
        existing_group = cursor.fetchone()

        if existing_group is None:
            cursor.execute(
                "INSERT INTO user_groups (user_id, group_id) VALUES (?, ?)",
                (student_id, group_id),
            )
        else:
            cursor.execute(
                "UPDATE user_groups SET group_id = ? WHERE user_id = ?",
                (group_id, student_id),
            )

        conn.commit()


def remove_test_assignment_from_group(test_id, group_id):
    conn = create_connection()
    with conn:
        cursor = conn.cursor()

        cursor.execute(
            """
            DELETE FROM student_tests
            WHERE test_id = ? AND student_id IN (
                SELECT user_id FROM user_groups WHERE group_id = ?
            )
        """,
            (test_id, group_id),
        )
        conn.commit()


def assign_test_to_group_students(test_id, group_id, assigner_id):
    conn = create_connection()
    with conn:
        cursor = conn.cursor()

        cursor.execute("SELECT attempts FROM tests WHERE id = ?", (test_id,))
        result = cursor.fetchone()
        attempts = result[0]

        query = """
        INSERT INTO student_tests (student_id, test_id, assigner_id, remaining_attempts)
        SELECT user_id, ?, ?, ?
        FROM user_groups WHERE group_id = ?
        ON CONFLICT(student_id, test_id) DO UPDATE SET remaining_attempts = ?
        """
        args = (test_id, assigner_id, attempts, group_id, attempts)
        cursor.execute(query, args)
        conn.commit()


def get_teachers_tests():
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
        teachers_tests = [
            {"teacher_name": row[0], "tests": row[1]} for row in cursor.fetchall()
        ]
    return teachers_tests


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
        tests = [
            dict(zip([column[0] for column in cursor.description], row))
            for row in cursor.fetchall()
        ]
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
        tests = [
            dict(zip([column[0] for column in cursor.description], row))
            for row in cursor.fetchall()
        ]
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
        return (
            {"name": user_info[0], "username": user_info[1],
                "password": user_info[2]}
            if user_info
            else None
        )


def update_user_info(user_id, name, username, password):
    query = "UPDATE users SET name = ?, username = ?, password = ? WHERE id = ?"
    args = (name, username, password, user_id)
    execute_query(query, args)


def get_assigned_tests_for_student(student_id):
    query = """
    SELECT 
        t.id, t.name, t.description, t.total_marks, t.attempts, 
        creator.name as creator_name, assigner.name as assigner_name,
        st.remaining_attempts
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
        tests = [
            dict(zip([column[0] for column in cursor.description], row))
            for row in cursor.fetchall()
        ]
    return tests


def remove_test_from_student(test_id, student_id):
    conn = create_connection()
    with conn:
        cursor = conn.cursor()
        query = "DELETE FROM student_tests WHERE student_id = ? AND test_id = ?"
        args = (student_id, test_id)
        cursor.execute(query, args)
        conn.commit()


def save_test_to_database(test_name, attempts, questions, creator_id):
    conn = create_connection()
    with conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO tests (name, attempts, creator_id) VALUES (?, ?, ?)",
            (test_name, attempts, creator_id),
        )
        test_id = cursor.lastrowid

        for question in questions:
            cursor.execute(
                "INSERT INTO questions (test_id, text, type) VALUES (?, ?, ?)",
                (test_id, question["text"], question["type"]),
            )
            question_id = cursor.lastrowid

            for answer in question["answers"]:
                cursor.execute(
                    "INSERT INTO answers (question_id, text, is_correct) VALUES (?, ?, ?)",
                    (question_id, answer["text"], answer["is_correct"]),
                )

        conn.commit()


def delete_test(test_id):
    query = "DELETE FROM tests WHERE id = ?"
    args = (test_id,)
    execute_query(query, args)


def get_group_id_by_name(group_name):
    conn = create_connection()
    with conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM groups WHERE name = ?", (group_name,))
        result = cursor.fetchone()
        return result[0] if result else None


def get_tests_by_teacher(teacher_id):
    query = """
    SELECT t.id, t.name
    FROM tests t
    JOIN users u ON t.creator_id = u.id
    WHERE u.id = ?
    """
    args = (teacher_id,)
    conn = create_connection()
    with conn:
        cursor = conn.cursor()
        cursor.execute(query, args)
        return [{"id": row[0], "name": row[1]} for row in cursor.fetchall()]


def get_test_details(test_id):
    query = """
    SELECT t.id, t.name, t.attempts, t.creator_id,
           q.id, q.text, q.type,
           a.id, a.text, a.is_correct
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
        if not rows:
            return None

        test_info = {
            "id": None,
            "name": None,
            "attempts": None,
            "creator_id": None,
            "questions": [],
        }
        question = None

        for row in rows:
            if test_info["id"] is None:
                test_info["id"] = row[0]
                test_info["name"] = row[1]
                test_info["attempts"] = row[2]
                test_info["creator_id"] = row[3]

            if question is None or question["id"] != row[4]:
                question = {"id": row[4], "text": row[5],
                            "type": row[6], "answers": []}
                test_info["questions"].append(question)

            if row[7] is not None:
                answer = {"id": row[7], "text": row[8], "is_correct": row[9]}
                question["answers"].append(answer)

        return test_info


def record_test_results(student_id, test_id, answers):
    conn = create_connection()
    with conn:
        cursor = conn.cursor()

        cursor.execute(
            "SELECT id, remaining_attempts FROM student_tests WHERE student_id = ? AND test_id = ?",
            (student_id, test_id)
        )
        result = cursor.fetchone()
        if result:
            student_test_id, remaining_attempts = result
            if remaining_attempts > 0:
                cursor.execute(
                    "INSERT INTO test_results (student_id, test_id) VALUES (?, ?)",
                    (student_id, test_id)
                )
                test_results_id = cursor.lastrowid

                for question in answers:
                    question_id = question["question_id"]
                    selected_answers = question["selected_answers"]
                    for answer_id in selected_answers:
                        cursor.execute(
                            "INSERT INTO student_answers (test_results_id, question_id, selected_answer) VALUES (?, ?, ?)",
                            (test_results_id, question_id, answer_id),
                        )

                cursor.execute(
                    "UPDATE student_tests SET remaining_attempts = remaining_attempts - 1 WHERE id = ?",
                    (student_test_id,),
                )

                conn.commit()


def get_remaining_attempts(student_id, test_id):
    query = """
    SELECT remaining_attempts FROM student_tests
    WHERE student_id = ? AND test_id = ?
    """
    args = (student_id, test_id)

    conn = create_connection()
    with conn:
        cursor = conn.cursor()
        cursor.execute(query, args)
        result = cursor.fetchone()
        return result[0] if result else None


def get_tests_by_student(student_id):
    query = """
    SELECT DISTINCT t.id, t.name
    FROM tests t
    JOIN test_results tr ON t.id = tr.test_id
    WHERE tr.student_id = ?
    """
    conn = create_connection()
    with conn:
        cursor = conn.cursor()
        cursor.execute(query, (student_id,))
        return [{"id": row[0], "name": row[1]} for row in cursor.fetchall()]


def get_student_test_attempt_results(student_id, test_id):
    query = """
    SELECT tr.id, a.is_correct, sa.selected_answer
    FROM student_answers sa
    JOIN answers a ON sa.question_id = a.question_id AND sa.selected_answer = a.id
    JOIN test_results tr ON sa.test_results_id = tr.id
    WHERE tr.student_id = ? AND tr.test_id = ?
    """
    args = (student_id, test_id)
    conn = create_connection()
    with conn:
        cursor = conn.cursor()
        cursor.execute(query, args)
        return cursor.fetchall()
