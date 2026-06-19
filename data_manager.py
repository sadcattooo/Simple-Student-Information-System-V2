import sqlite3
from pathlib import Path
from tkinter import messagebox
from config import SEED_COLLEGES, SEED_PROGRAMS, SEED_FIRSTNAMES, SEED_LASTNAMES

DB_PATH = Path(__file__).resolve().parent / "app.db"

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

            CREATE TABLE IF NOT EXISTS history (
                id        INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                action    TEXT NOT NULL,
                entity    TEXT NOT NULL,
                details   TEXT NOT NULL
            );

            CREATE INDEX IF NOT EXISTS idx_student_program ON student(program);
            CREATE INDEX IF NOT EXISTS idx_student_college ON student(college);
            CREATE INDEX IF NOT EXISTS idx_program_college ON program(college_code);
        """)


# ── History ───────────────────────────────────────────────────

def log_action(action: str, entity: str, details: str):
    """Log an action to the history table. action: Added/Edited/Deleted. entity: Student/Program/College."""
    from datetime import datetime
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with get_connection() as conn:
        conn.execute(
            "INSERT INTO history(timestamp, action, entity, details) VALUES (?,?,?,?)",
            (timestamp, action, entity, details)
        )


def load_history():
    with get_connection() as conn:
        return conn.execute(
            "SELECT timestamp, action, entity, details FROM history ORDER BY id DESC"
        ).fetchall()


def clear_history():
    with get_connection() as conn:
        conn.execute("DELETE FROM history")


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
            LEFT JOIN student AS s ON s.college = c.code
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
                p.college_code AS pcollege_code,
                COUNT(s.id)    AS stu_count
            FROM program AS p
            LEFT JOIN student AS s ON s.program = p.code
            GROUP BY p.code, p.name, p.college_code
            ORDER BY p.name
        """).fetchall()
    for row in rows:
        program_table.insert("", "end",
                             values=(row["pcode"], row["pname"],
                                     row["pcollege_code"] or "", row["stu_count"]))


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
            conn.execute("PRAGMA foreign_keys = OFF")
            conn.execute("DELETE FROM student")
            conn.executemany(
                "INSERT OR REPLACE INTO student"
                "(id, name, year_level, program, college, dob, sex, contact, email, address)"
                " VALUES (?,?,?,?,?,?,?,?,?,?)",
                rows,
            )
            conn.execute("PRAGMA foreign_keys = ON")
    except Exception as e:
        messagebox.showerror("Save Failed", f"Cannot save students\n\n{e}")


def save_programs(program_table):
    try:
        with get_connection() as conn:
            rows = []
            for c in program_table.get_children():
                v = program_table.item(c)["values"][:3]
                prog_code, prog_name, college_code = v[0], v[1], str(v[2]).strip()
                rows.append((prog_code, prog_name, college_code))
            conn.execute("PRAGMA foreign_keys = OFF")
            conn.execute("DELETE FROM program")
            conn.executemany(
                "INSERT OR REPLACE INTO program(code, name, college_code) VALUES (?,?,?)",
                rows,
            )
            conn.execute("PRAGMA foreign_keys = ON")
    except Exception as e:
        messagebox.showerror("Save Failed", f"Cannot save programs\n\n{e}")


def save_colleges(college_table):
    try:
        rows = [college_table.item(c)["values"][:2]
                for c in college_table.get_children()]
        with get_connection() as conn:
            conn.execute("PRAGMA foreign_keys = OFF")
            conn.execute("DELETE FROM college")
            conn.executemany(
                "INSERT OR REPLACE INTO college(code, name) VALUES (?,?)",
                rows,
            )
            conn.execute("PRAGMA foreign_keys = ON")
    except Exception as e:
        messagebox.showerror("Save Failed", f"Cannot save colleges\n\n{e}")


# ── Data Count ─────────────────────────────────────────────

def update_all_college_program_counts(program_table, college_table):
    """Recalculate No. of Programs column for every college row."""
    count_map = {}
    for c in program_table.get_children():
        v = program_table.item(c)["values"]
        if len(v) >= 3:
            col = str(v[2]).strip()   # holds college CODE
            if col and col.lower() != "null":
                count_map[col] = count_map.get(col, 0) + 1
    for c in college_table.get_children():
        v = college_table.item(c)["values"]
        if len(v) >= 4:
            ccode = str(v[0]).strip()   # match by college CODE
            college_table.item(c, values=(v[0], v[1], str(count_map.get(ccode, 0)), v[3]))


def update_program_student_count(program_code, student_table, program_table):
    if not program_code:
        return
    count = sum(
        1 for c in student_table.get_children()
        if str(student_table.item(c)["values"][3]).strip() == program_code.strip()
    )
    for c in program_table.get_children():
        v = program_table.item(c)["values"]
        if str(v[0]).strip() == program_code.strip():
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
                                      str(counts.get(str(v[0]).strip(), 0))))


def update_college_student_count(college_code, student_table, college_table):
    if not college_code:
        return
    count = sum(
        1 for c in student_table.get_children()
        if str(student_table.item(c)["values"][4]).strip() == college_code.strip()
    )
    for c in college_table.get_children():
        v = college_table.item(c)["values"]
        if str(v[0]).strip() == college_code.strip():
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
                                      str(counts.get(str(v[0]).strip(), 0))))


# ── Cascade Rename ────────────────────────────────────────────

def cascade_rename_program(old_code: str, new_code: str):
    """When a program's code changes, update every student row that references it."""
    if old_code == new_code:
        return
    with get_connection() as conn:
        conn.execute(
            "UPDATE student SET program = ? WHERE program = ?",
            (new_code, old_code)
        )


def cascade_rename_college(old_code: str, new_code: str):
    """When a college's code changes, update every student row that references it."""
    if old_code == new_code:
        return
    with get_connection() as conn:
        conn.execute(
            "UPDATE student SET college = ? WHERE college = ?",
            (new_code, old_code)
        )


# ── seed ──────────────────────────────────────────────────────

def seed_db():
    """Pre-populate colleges, programs, and 5000 students. Skips if already seeded."""
    import random

    with get_connection() as conn:
        conn.execute("PRAGMA foreign_keys = OFF")
        conn.executemany(
            "INSERT OR IGNORE INTO college(code, name) VALUES (?,?)", SEED_COLLEGES
        )
        conn.executemany(
            "INSERT OR IGNORE INTO program(code, name, college_code) VALUES (?,?,?)", SEED_PROGRAMS
        )

        count = conn.execute("SELECT COUNT(*) FROM student").fetchone()[0]
        if count < 5000:
            year_levels = ["1st Year", "2nd Year", "3rd Year", "4th Year"]
            sexes       = ["Male", "Female", "Other"]
            existing    = {r[0] for r in conn.execute("SELECT id FROM student").fetchall()}
            batch = []

            for _ in range(5000 - count):
                yr  = random.randint(2019, 2024)
                seq = random.randint(1, 9999)
                sid = f"{yr}-{seq:04d}"
                while sid in existing:
                    seq = random.randint(1, 9999)
                    sid = f"{yr}-{seq:04d}"
                existing.add(sid)

                prog_code, prog_name, col_code = random.choice(SEED_PROGRAMS)
                fullname   = f"{random.choice(SEED_FIRSTNAMES)} {random.choice(SEED_LASTNAMES)}"
                year_level = random.choice(year_levels)
                sex        = random.choices(sexes, weights=[48, 48, 4])[0]

                batch.append((sid, fullname, year_level, prog_code, col_code,
                              "", sex, "", "", ""))

                if len(batch) >= 500:
                    conn.executemany(
                        "INSERT OR IGNORE INTO student"
                        "(id,name,year_level,program,college,dob,sex,contact,email,address)"
                        " VALUES (?,?,?,?,?,?,?,?,?,?)",
                        batch
                    )
                    batch.clear()

            if batch:
                conn.executemany(
                    "INSERT OR IGNORE INTO student"
                    "(id,name,year_level,program,college,dob,sex,contact,email,address)"
                    " VALUES (?,?,?,?,?,?,?,?,?,?)",
                    batch
                )

        conn.execute("PRAGMA foreign_keys = ON")