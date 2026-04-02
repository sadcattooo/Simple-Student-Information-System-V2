import csv
from tkinter import messagebox


def load_colleges(college_table):
    try:
        with open("colleges.csv", "r", encoding="utf-8") as f:
            reader = csv.reader(f)
            next(reader, None)
            for row in reader:
                if len(row) >= 2:
                    college_table.insert("", "end", values=(row[0], row[1], "0", "0"))
    except FileNotFoundError:
        pass


def load_programs(program_table):
    try:
        with open("programs.csv", "r", encoding="utf-8") as f:
            reader = csv.reader(f)
            next(reader, None)
            for row in reader:
                if len(row) >= 3:
                    program_table.insert("", "end", values=(row[0], row[1], row[2], "0"))
    except FileNotFoundError:
        pass


def load_students_from_csv(student_table, update_all_program_counts_fn, update_all_college_counts_fn):
    try:
        with open("students.csv", "r", newline="") as file:
            reader = csv.reader(file)
            next(reader, None)
            for row in reader:
                if len(row) >= 5:
                    while len(row) < 10:
                        row.append("")
                    values = row[:10] + ["View"]
                    student_table.insert("", "end", values=values)
    except FileNotFoundError:
        pass
    except Exception as e:
        messagebox.showerror("Error", f"Failed to load students.csv\n{e}")

    update_all_program_counts_fn()
    update_all_college_counts_fn()


def save_all_to_csv(student_table):
    try:
        with open("students.csv", "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["ID", "Name", "Year Level", "Program", "College",
                             "DOB", "Sex", "Contact", "Email", "Address"])
            count = 0
            for child in student_table.get_children():
                values = student_table.item(child)["values"][:-1]
                writer.writerow(values)
                count += 1
            print(f"Saved {count} students to students.csv")
    except Exception as e:
        messagebox.showerror("Save Failed", f"Cannot save students.csv\n\nError:\n{str(e)}")
        print("Save error:", str(e))


def save_programs_to_csv(program_table):
    try:
        with open("programs.csv", "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["Program ID", "Program Name", "College", "No. of Students"])
            count = 0
            for child in program_table.get_children():
                values = program_table.item(child)["values"]
                writer.writerow(values)
                count += 1
            print(f"Saved {count} programs to programs.csv")
    except Exception as e:
        messagebox.showerror("Save Failed", f"Cannot save programs.csv\n\nError:\n{str(e)}")
        print("Save error:", str(e))


def save_colleges_to_csv(college_table):
    try:
        with open("colleges.csv", "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["College ID", "College Name", "No. of Programs", "No. of Students"])
            count = 0
            for child in college_table.get_children():
                values = college_table.item(child)["values"]
                writer.writerow(values)
                count += 1
            print(f"Saved {count} colleges to colleges.csv")
    except Exception as e:
        messagebox.showerror("Save Failed", f"Cannot save colleges.csv\n\nError:\n{str(e)}")
        print("Save error:", str(e))


def update_program_student_count(program_name, student_table, program_table):
    if not program_name:
        return
    count = 0
    for child in student_table.get_children():
        values = student_table.item(child)["values"]
        if len(values) >= 4 and values[3].strip() == program_name.strip():
            count += 1
    for child in program_table.get_children():
        prog_values = program_table.item(child)["values"]
        if len(prog_values) >= 4 and prog_values[1].strip() == program_name.strip():
            new_values = (prog_values[0], prog_values[1], prog_values[2], str(count))
            program_table.item(child, values=new_values)
            break


def update_all_program_counts(student_table, program_table):
    program_student_map = {}
    for child in student_table.get_children():
        values = student_table.item(child)["values"]
        if len(values) >= 4:
            prog = values[3].strip()
            if prog:
                program_student_map[prog] = program_student_map.get(prog, 0) + 1
    for child in program_table.get_children():
        prog_values = program_table.item(child)["values"]
        if len(prog_values) >= 4:
            prog_name = prog_values[1].strip()
            new_count = program_student_map.get(prog_name, 0)
            new_values = (prog_values[0], prog_values[1], prog_values[2], str(new_count))
            program_table.item(child, values=new_values)


def update_college_student_count(college_name, student_table, college_table):
    if not college_name:
        return
    count = 0
    for child in student_table.get_children():
        values = student_table.item(child)["values"]
        if len(values) >= 5 and values[4].strip() == college_name.strip():
            count += 1
    for child in college_table.get_children():
        col_values = college_table.item(child)["values"]
        if len(col_values) >= 4 and col_values[1].strip() == college_name.strip():
            new_values = (col_values[0], col_values[1], col_values[2], str(count))
            college_table.item(child, values=new_values)
            break


def update_all_college_counts(student_table, college_table):
    college_student_map = {}
    for child in student_table.get_children():
        values = student_table.item(child)["values"]
        if len(values) >= 5:
            col = values[4].strip()
            if col:
                college_student_map[col] = college_student_map.get(col, 0) + 1
    for child in college_table.get_children():
        col_values = college_table.item(child)["values"]
        if len(col_values) >= 4:
            col_name = col_values[1].strip()
            new_count = college_student_map.get(col_name, 0)
            new_values = (col_values[0], col_values[1], col_values[2], str(new_count))
            college_table.item(child, values=new_values)
