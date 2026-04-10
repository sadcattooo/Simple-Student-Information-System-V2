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
            CREATE TABLE IF NOT EXISTS college (
                code TEXT PRIMARY KEY,
                name TEXT NOT NULL UNIQUE
            );

            CREATE TABLE IF NOT EXISTS program (
                code         TEXT PRIMARY KEY,
                name         TEXT NOT NULL,
                college_code TEXT NOT NULL REFERENCES college(code)
                                   ON UPDATE CASCADE ON DELETE RESTRICT,
                UNIQUE(name, college_code)
            );

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

            CREATE INDEX IF NOT EXISTS idx_student_program ON student(program);
            CREATE INDEX IF NOT EXISTS idx_student_college ON student(college);
            CREATE INDEX IF NOT EXISTS idx_program_college ON program(college_code);
        """)


# ── Load ──────────────────────────────────────────────────────

def load_colleges(college_table):
    with get_connection() as conn:
        rows = conn.execute("""
            SELECT
                c.code AS ccode,
                c.name AS cname,
                COUNT(DISTINCT p.code) AS prog_count,
                COUNT(DISTINCT s.id)   AS stu_count
            FROM college AS c
            LEFT JOIN program AS p ON p.college_code = c.code
            LEFT JOIN student AS s ON s.college = c.name
            GROUP BY c.code, c.name
            ORDER BY c.name
        """).fetchall()
    for row in rows:
        college_table.insert("", "end",
                             values=(row["ccode"], row["cname"],
                                     row["prog_count"], row["stu_count"]))


def load_programs(program_table):
    with get_connection() as conn:
        rows = conn.execute("""
            SELECT
                p.code         AS pcode,
                p.name         AS pname,
                p.college_code AS pcollege,
                COUNT(s.id)    AS stu_count
            FROM program AS p
            LEFT JOIN student AS s ON s.program = p.name
            GROUP BY p.code, p.name, p.college_code
            ORDER BY p.name
        """).fetchall()
    for row in rows:
        program_table.insert("", "end",
                             values=(row["pcode"], row["pname"],
                                     row["pcollege"], row["stu_count"]))


def load_students(student_table, update_all_program_counts_fn, update_all_college_counts_fn):
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT id, name, year_level, program, college, dob, sex, contact, email, address"
            " FROM student ORDER BY name"
        ).fetchall()
    for row in rows:
        student_table.insert("", "end", values=list(row) + ["View"])

    update_all_program_counts_fn()
    update_all_college_counts_fn()


# ── Save ──────────────────────────────────────────────────────

def save_students(student_table):
    try:
        rows = [student_table.item(c)["values"][:10]
                for c in student_table.get_children()]
        with get_connection() as conn:
            conn.execute("DELETE FROM student")
            conn.executemany(
                "INSERT INTO student"
                "(id, name, year_level, program, college, dob, sex, contact, email, address)"
                " VALUES (?,?,?,?,?,?,?,?,?,?)",
                rows,
            )
    except Exception as e:
        messagebox.showerror("Save Failed", f"Cannot save students\n\n{e}")


def save_programs(program_table):
    try:
        rows = [program_table.item(c)["values"][:3]
                for c in program_table.get_children()]
        with get_connection() as conn:
            conn.execute("DELETE FROM program")
            conn.executemany(
                "INSERT OR IGNORE INTO program(code, name, college_code) VALUES (?,?,?)",
                rows,
            )
    except Exception as e:
        messagebox.showerror("Save Failed", f"Cannot save programs\n\n{e}")


def save_colleges(college_table):
    try:
        rows = [college_table.item(c)["values"][:2]
                for c in college_table.get_children()]
        with get_connection() as conn:
            conn.execute("DELETE FROM college")
            conn.executemany(
                "INSERT OR IGNORE INTO college(code, name) VALUES (?,?)",
                rows,
            )
    except Exception as e:
        messagebox.showerror("Save Failed", f"Cannot save colleges\n\n{e}")


# ── Count helpers ─────────────────────────────────────────────

def update_program_student_count(program_name, student_table, program_table):
    if not program_name:
        return
    count = sum(
        1 for c in student_table.get_children()
        if str(student_table.item(c)["values"][3]).strip() == program_name.strip()
    )
    for c in program_table.get_children():
        v = program_table.item(c)["values"]
        if str(v[1]).strip() == program_name.strip():
            program_table.item(c, values=(v[0], v[1], v[2], str(count)))
            break


def update_all_program_counts(student_table, program_table):
    counts = {}
    for c in student_table.get_children():
        prog = str(student_table.item(c)["values"][3]).strip()
        if prog:
            counts[prog] = counts.get(prog, 0) + 1
    for c in program_table.get_children():
        v = program_table.item(c)["values"]
        program_table.item(c, values=(v[0], v[1], v[2],
                                      str(counts.get(str(v[1]).strip(), 0))))


def update_college_student_count(college_name, student_table, college_table):
    if not college_name:
        return
    count = sum(
        1 for c in student_table.get_children()
        if str(student_table.item(c)["values"][4]).strip() == college_name.strip()
    )
    for c in college_table.get_children():
        v = college_table.item(c)["values"]
        if str(v[1]).strip() == college_name.strip():
            college_table.item(c, values=(v[0], v[1], v[2], str(count)))
            break


def update_all_college_counts(student_table, college_table):
    counts = {}
    for c in student_table.get_children():
        col = str(student_table.item(c)["values"][4]).strip()
        if col:
            counts[col] = counts.get(col, 0) + 1
    for c in college_table.get_children():
        v = college_table.item(c)["values"]
        college_table.item(c, values=(v[0], v[1], v[2],
                                      str(counts.get(str(v[1]).strip(), 0))))