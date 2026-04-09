import sqlite3
from pathlib import Path
from tkinter import messagebox

DB_PATH = Path(__file__).parent / "app.db"

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def init_db():
    with get_connection() as conn:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS student (
                id          TEXT PRIMARY KEY,
                name        TEXT NOT NULL,
                year_level  TEXT,
                program     TEXT,
                college     TEXT,
                dob         TEXT,
                sex         TEXT,
                contact     TEXT,
                email       TEXT,
                address     TEXT
            );               

            CREATE TABLE IF NOT EXISTS program (
                code         TEXT PRIMARY KEY,
                name         TEXT NOT NULL,
                college_code TEXT NOT NULL REFERENCES college(code)
                                   ON UPDATE CASCADE ON DELETE RESTRICT,
                UNIQUE(name, college_code)
            );

             CREATE TABLE IF NOT EXISTS college (
                code TEXT PRIMARY KEY,
                name TEXT NOT NULL UNIQUE
            );

            

            

            CREATE INDEX IF NOT EXISTS idx_student_program ON student(program);
            CREATE INDEX IF NOT EXISTS idx_student_college ON student(college);
            CREATE INDEX IF NOT EXISTS idx_program_college ON program(college_code);                   
                           """)
        
def load_colleges(college_table):
    with get_connection() as conn:
        rows = conn.execute("""
            SELECT c.code, c.name,
                   COUNT(DISTINCT p.code) AS prog_count,
                   COUNT(DISTINCT s.id)   AS stu_count
            FROM college c
            LEFT JOIN program p ON p.college_code = c.code
            LEFT JOIN student s ON s.college = c.name
            GROUP BY c.code
            ORDER BY c.name
        """).fetchall()
    for row in rows:
        college_table.insert("", "end",
                             values=(row["code"], row["name"],
                                     row["prog_count"], row["stu_count"]))


def load_programs(program_table):
    with get_connection() as conn:
        rows = conn.execute("""
            SELECT p.code, p.name, p.college_code,
                   COUNT(s.id) AS stu_count
            FROM program p
            LEFT JOIN student s ON s.program = p.name
            GROUP BY p.code
            ORDER BY p.name
        """).fetchall()
    for row in rows:
        program_table.insert("", "end",
                             values=(row["code"], row["name"],
                                     row["college_code"], row["stu_count"]))


def load_students(student_table, update_all_program_counts, update_all_college_counts):
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT id,name,year_level,program,college,dob,sex,contact,email,address"
            " FROM student ORDER BY name"
        ).fetchall()
    for row in rows:
        student_table.insert("", "end", values=list(row) + ["View"])

    update_all_program_counts()
    update_all_college_counts()