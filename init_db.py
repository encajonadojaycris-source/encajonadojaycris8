import os
import sqlite3

DATABASE = os.path.join(os.path.dirname(__file__), "students.db")

conn = sqlite3.connect(DATABASE)
conn.execute("""
    CREATE TABLE IF NOT EXISTS students (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id TEXT NOT NULL,
        name TEXT NOT NULL,
        program TEXT NOT NULL,
        year INTEGER NOT NULL,
        section TEXT NOT NULL
    )
""")

# Add practice records only when the table is empty.
count = conn.execute("SELECT COUNT(*) FROM students").fetchone()[0]
if count == 0:
    sample_students = [
        ("2024-00001", "Juan Dela Cruz", "BSIT", 2, "2A"),
        ("2024-00002", "Maria Santos", "BSIT", 2, "2A"),
        ("2024-00003", "Pedro Reyes", "BSCS", 1, "1B"),
    ]
    conn.executemany("""
        INSERT INTO students (student_id, name, program, year, section)
        VALUES (?, ?, ?, ?, ?)
    """, sample_students)

conn.commit()
conn.close()
print("Database created successfully.")
