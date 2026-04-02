import tkinter
from tkinter import *
from tkinter import messagebox
from tkinter import ttk
from tkinter.ttk import Combobox, Treeview
from config import SORT_OPTIONS
from ui_helpers import validate_student_id_action, auto_format_student_id, treeview_sort_column, update_dob_days
import data_manager as dm
from tkinter.ttk import Style
from tkinter import PhotoImage

editing_iid = None
current_view = "students"




# ─────────────────────────────────────────────────────────────
#  FUNCTIONS
# ─────────────────────────────────────────────────────────────

def sort_current_table(*args):
    if current_view == "students":
        table = student_table
        type_key = "students"
    elif current_view == "programs":
        table = program_table
        type_key = "programs"
    elif current_view == "colleges":
        table = college_table
        type_key = "colleges"
    else:
        return
    sort_choice = sort_var.get()
    col = SORT_OPTIONS[type_key]["columns"].get(sort_choice)
    if col and table:
        treeview_sort_column(table, col, False)


def update_sort_dropdown():
    if current_view == "students":
        sort_cb["values"] = SORT_OPTIONS["students"]["options"]
        sort_cb.set(SORT_OPTIONS["students"]["default"])
    elif current_view == "programs":
        sort_cb["values"] = SORT_OPTIONS["programs"]["options"]
        sort_cb.set(SORT_OPTIONS["programs"]["default"])
    elif current_view == "colleges":
        sort_cb["values"] = SORT_OPTIONS["colleges"]["options"]
        sort_cb.set(SORT_OPTIONS["colleges"]["default"])


def student_list():
    global current_view
    student_framebtn.grid()
    program_framebtn.grid_remove()
    college_framebtn.grid_remove()
    add_btn.config(text="Add Student", command=add_student)
    current_view = "students"
    update_sort_dropdown()


def program_list():
    global current_view
    program_framebtn.grid()
    student_framebtn.grid_remove()
    college_framebtn.grid_remove()
    add_btn.config(text="Add Program", command=add_program)
    current_view = "programs"
    update_sort_dropdown()


def college_list():
    global current_view
    college_framebtn.grid()
    student_framebtn.grid_remove()
    program_framebtn.grid_remove()
    add_btn.config(text="Add College", command=add_college)
    current_view = "colleges"
    update_sort_dropdown()


def add_student():
    add_student_frame.tkraise()
    add_student_frame.grid(row=0, column=1, sticky="nsew", padx=(5, 5), pady=(5, 0), rowspan=2)


def add_program():
    add_program_frame.grid(row=0, column=1, sticky="nsew", padx=5, pady=5)


def add_college():
    add_college_frame.grid(row=0, column=1, sticky="nsew", padx=5, pady=5)


def save_student():
    global editing_iid

    student_id = sid.get().strip()

    if not student_id:
        messagebox.showwarning("Required", "Student ID is required.")
        sid.focus_set()
        return

    if len(student_id) != 9 or student_id[4] != '-' or not student_id.replace('-', '').isdigit():
        messagebox.showwarning("Invalid Format",
                               "Student ID must be in format: YYYY-0000\n"
                               "Example: 2024-0123, 2025-0005")
        sid.focus_set()
        return

    year_part = student_id[:4]
    if not (year_part.isdigit() and 2000 <= int(year_part) <= 9999):
        messagebox.showwarning("Invalid Year",
                               "Year in Student ID must be between 2000 and 9999")
        sid.focus_set()
        return

    if editing_iid is None:
        for child in student_table.get_children():
            existing_id = student_table.item(child)["values"][0]
            if existing_id == student_id:
                messagebox.showerror("Duplicate", f"Student ID {student_id} already exists!")
                sid.focus_set()
                return
    else:
        current_id = student_table.item(editing_iid)["values"][0]
        if student_id != current_id:
            for child in student_table.get_children():
                if child != editing_iid and student_table.item(child)["values"][0] == student_id:
                    messagebox.showerror("Duplicate", f"Student ID {student_id} is already used by another student!")
                    sid.focus_set()
                    return

    dob_year  = dob_year_cb.get().strip()
    dob_month = dob_month_cb.get().strip()
    dob_day   = dob_day_cb.get().strip()

    if not all([dob_year, dob_month, dob_day]):
        messagebox.showwarning("Incomplete", "Please select full Date of Birth (Year-Month-Day)")
        dob_year_cb.focus_set()
        return

    dob_value = f"{dob_year}-{dob_month}-{dob_day}"

    try:
        y = int(dob_year)
        if not (1950 <= y <= 2025):
            raise ValueError
    except ValueError:
        messagebox.showwarning("Invalid Year", "Year of birth should be between 1950 and 2025")
        dob_year_cb.focus_set()
        return

    if not all([student_id, fname.get().strip(), lname.get().strip(), sex.get().strip()]):
        messagebox.showwarning("Incomplete Form", "Please fill all required fields (*)")
        return

    mid = mname.get().strip()
    mid_initial = (mid[0].upper() + ".") if mid else ""
    fullname = f"{fname.get().strip().title()} {mid_initial} {lname.get().strip().title()}".strip()

    values = (
        student_id,
        fullname,
        year_cb.get(),
        program_cb.get(),
        college_cb.get(),
        dob_value,
        sex.get(),
        cnumber.get().strip(),
        email.get().strip(),
        address.get().strip(),
        "View"
    )

    if editing_iid and editing_iid in student_table.get_children():
        old_values = student_table.item(editing_iid)["values"]
        old_program = old_values[3].strip() if len(old_values) > 3 else ""
        old_college = old_values[4].strip() if len(old_values) > 4 else ""

        student_table.item(editing_iid, values=values)
        msg = "Student updated successfully."

        new_program = values[3].strip()
        new_college = values[4].strip()

        if new_program != old_program:
            if old_program:
                dm.update_program_student_count(old_program, student_table, program_table)
            if new_program:
                dm.update_program_student_count(new_program, student_table, program_table)

        if new_college != old_college:
            if old_college:
                dm.update_college_student_count(old_college, student_table, college_table)
            if new_college:
                dm.update_college_student_count(new_college, student_table, college_table)
    else:
        student_table.insert("", "end", values=values)
        msg = "Student added successfully."

        new_program = values[3].strip()
        if new_program:
            dm.update_program_student_count(new_program, student_table, program_table)

        new_college = values[4].strip()
        if new_college:
            dm.update_college_student_count(new_college, student_table, college_table)

    dm.save_all_to_csv(student_table)
    dm.save_programs_to_csv(program_table)
    dm.save_colleges_to_csv(college_table)

    for widget in [sid, fname, mname, lname, cnumber, email, address]:
        widget.delete(0, END)
    dob_year_cb.set("")
    dob_month_cb.set("")
    dob_day_cb.set("")
    for cb in [sex, year_cb, college_cb, program_cb]:
        cb.set("")

    add_student_frame.grid_remove()
    bot_btn.config(text="Save", command=save_student)

    messagebox.showinfo("Success", msg)
    editing_iid = None


def save_college():
    cid = college_id_entry.get().strip()
    cname = college_name_entry.get().strip()

    if not cid or not cname:
        messagebox.showwarning("Missing", "College Code and Name are required.")
        return

    for child in college_table.get_children():
        existing_cid = college_table.item(child)["values"][0]
        if existing_cid == cid:
            messagebox.showerror("Duplicate", f"College Code '{cid}' already exists!")
            college_id_entry.focus_set()
            return

    college_table.insert("", "end", values=(cid, cname, "0", "0"))
    dm.save_colleges_to_csv(college_table)
    refresh_college_comboboxes()
    refresh_programs()

    college_id_entry.delete(0, END)
    college_name_entry.delete(0, END)
    add_college_frame.grid_remove()
    messagebox.showinfo("Success", "College added successfully!")


def save_program():
    pid   = prog_id_entry.get().strip()
    pname = prog_name_entry.get().strip()
    cname = prog_college_cb.get().strip()

    if not pid or not pname or not cname:
        messagebox.showwarning("Missing", "All fields are required.")
        return

    for child in program_table.get_children():
        existing_pid = program_table.item(child)["values"][0]
        if existing_pid == pid:
            messagebox.showerror("Duplicate", f"Program Code '{pid}' already exists!")
            prog_id_entry.focus_set()
            return

    for child in program_table.get_children():
        ex_pid, ex_pname, ex_college, _ = program_table.item(child)["values"]
        if ex_college == cname and ex_pname.lower() == pname.lower():
            messagebox.showerror("Duplicate", f"Program '{pname}' already exists in college '{cname}'!")
            prog_name_entry.focus_set()
            return

    program_table.insert("", "end", values=(pid, pname, cname, "0"))
    dm.save_programs_to_csv(program_table)

    if college_cb.get() == cname:
        current_programs = list(program_cb["values"])
        if pname not in current_programs:
            current_programs.append(pname)
            program_cb["values"] = sorted(current_programs)

    prog_id_entry.delete(0, END)
    prog_name_entry.delete(0, END)
    prog_college_cb.set("")

    refresh_college_comboboxes()
    refresh_programs()
    add_program_frame.grid_remove()
    messagebox.showinfo("Success", "Program added successfully!")


def refresh_college_comboboxes():
    colleges = [college_table.item(child)["values"][1] for child in college_table.get_children()]
    college_cb["values"] = colleges
    prog_college_cb["values"] = colleges


def refresh_programs():
    selected_college = college_cb.get().strip()
    if not selected_college:
        program_cb["values"] = []
        program_cb.config(state="disabled")
        return
    programs = [program_table.item(c)["values"][1].strip()
                for c in program_table.get_children()
                if len(program_table.item(c)["values"]) >= 4
                and program_table.item(c)["values"][2].strip() == selected_college]
    program_cb["values"] = sorted(programs)
    program_cb.config(state="readonly" if programs else "disabled")


def delete_item():
    current_table = None
    item_type = "item"

    if student_framebtn.winfo_ismapped():
        current_table = student_table
        item_type = "student"
    elif program_framebtn.winfo_ismapped():
        current_table = program_table
        item_type = "program"
    elif college_framebtn.winfo_ismapped():
        current_table = college_table
        item_type = "college"
    refresh_college_comboboxes()
    refresh_programs()

    if not current_table:
        messagebox.showinfo("Info", "No list is open.")
        return

    items = current_table.selection()
    if not items:
        messagebox.showinfo("Info", f"No {item_type} selected!")
        return

    for item in items:
        values = current_table.item(item)["values"]
        name = values[1] if len(values) > 1 else ""
        confirm = messagebox.askyesno("Confirm Delete", f"Delete {item_type.capitalize()}: {name}?")
        if confirm:
            if current_table == student_table:
                prog = values[3].strip() if len(values) > 3 else ""
                coll = values[4].strip() if len(values) > 4 else ""
                current_table.delete(item)
                if prog:
                    dm.update_program_student_count(prog, student_table, program_table)
                if coll:
                    dm.update_college_student_count(coll, student_table, college_table)
                dm.save_all_to_csv(student_table)
                dm.save_programs_to_csv(program_table)
                dm.save_colleges_to_csv(college_table)
            else:
                current_table.delete(item)

    if current_table == student_table:
        dm.save_all_to_csv(student_table)
    elif current_table == program_table:
        dm.save_programs_to_csv(program_table)
    elif current_table == college_table:
        dm.save_colleges_to_csv(college_table)


def search_current():
    query = search_entry.get().lower()
    if not query:
        return

    current_tree = None
    if student_framebtn.winfo_ismapped():
        current_tree = student_table
    elif program_framebtn.winfo_ismapped():
        current_tree = program_table
    elif college_framebtn.winfo_ismapped():
        current_tree = college_table

    if current_tree:
        current_tree.selection_remove(current_tree.selection())
        matches = []
        for child in current_tree.get_children():
            values = ' '.join(map(str, current_tree.item(child)['values'])).lower()
            if query in values:
                matches.append(child)
        current_tree.selection_set(matches)


def clear_list():
    current_table = None
    item_type = ""

    if student_framebtn.winfo_ismapped():
        current_table = student_table
        item_type = "student list"
    elif program_framebtn.winfo_ismapped():
        current_table = program_table
        item_type = "program list"
    elif college_framebtn.winfo_ismapped():
        current_table = college_table
        item_type = "college list"

    refresh_college_comboboxes()
    refresh_programs()

    if not current_table:
        messagebox.showinfo("Info", "No list is open.")
        return

    warn = messagebox.askyesno("Clear List",
                                f"Are you sure you want to clear the {item_type}? This cannot be undone.")
    if warn:
        current_table.delete(*current_table.get_children())
        if current_table == student_table:
            dm.save_all_to_csv(student_table)
        elif current_table == program_table:
            dm.save_programs_to_csv(program_table)
        elif current_table == college_table:
            dm.save_colleges_to_csv(college_table)


def update_programs(event):
    selected_college = college_cb.get().strip()
    if not selected_college:
        program_cb["values"] = []
        program_cb.set("")
        program_cb.config(state="disabled")
        return

    programs = []
    for child in program_table.get_children():
        values = program_table.item(child)["values"]
        if len(values) >= 4:
            college_value = values[2] if len(values) > 2 else ""
            if str(college_value).strip() == selected_college:
                programs.append(str(values[1]).strip())

    program_cb["values"] = sorted(programs)
    program_cb.set("")
    program_cb.config(state="readonly" if programs else "disabled")


def view(student_data):

    if not student_data or len(student_data) < 10:
        return
    
    global editing_iid

    selected = student_table.selection()
    if not selected:
        return

    view_win = Toplevel(window)
    view_win.title("Student Details")
    view_win.geometry("520x620")
    view_win.resizable(False, False)

    labels = [
        "Student ID", "Full Name", "Year Level", "Program", "College",
        "Date of Birth", "Sex", "Contact Number", "Email", "Address"
    ]

    entries = {}
    for i, txt in enumerate(labels):
        Label(view_win, text=txt + ":", font=("Arial", 10, "bold")) \
            .grid(row=i, column=0, sticky="w", padx=20, pady=8)
        e = Entry(view_win, width=45, font=("Arial", 10))
        e.grid(row=i, column=1, padx=10, pady=8, sticky="ew")
        entries[txt] = e

    for lbl, idx in zip(labels, range(10)):
        entries[lbl].insert(0, student_data[idx])
    for e in entries.values():
        e.config(state="readonly")

    def start_edit():
        sid.delete(0, END)
        sid.insert(0, student_data[0])

        name = student_data[1].strip()
        parts = name.split()
        fname_val = parts[0] if parts else ""
        lname_val = parts[-1] if len(parts) > 1 else ""
        middle = " ".join(parts[1:-1]) if len(parts) > 2 else ""
        mname_val = middle.rstrip('.') if middle.endswith('.') else middle

        fname.delete(0, END)
        fname.insert(0, fname_val)
        mname.delete(0, END)
        mname.insert(0, mname_val)
        lname.delete(0, END)
        lname.insert(0, lname_val)

        dob_str = student_data[5].strip() if len(student_data) > 5 else ""
        if dob_str and len(dob_str) == 10 and dob_str[4] == '-' and dob_str[7] == '-':
            try:
                year, month, day = dob_str.split('-')
                dob_year_cb.set(year)
                dob_month_cb.set(month)
                dob_day_cb.set(day)
                update_dob_days(dob_year_cb, dob_month_cb, dob_day_cb)
            except Exception:
                dob_year_cb.set("")
                dob_month_cb.set("")
                dob_day_cb.set("")
        else:
            dob_year_cb.set("")
            dob_month_cb.set("")
            dob_day_cb.set("")

        sex.set(student_data[6])
        cnumber.delete(0, END)
        cnumber.insert(0, student_data[7])
        email.delete(0, END)
        email.insert(0, student_data[8])
        address.delete(0, END)
        address.insert(0, student_data[9])
        year_cb.set(student_data[2])
        college_cb.set(student_data[4])
        update_programs(None)
        program_cb.set(student_data[3])

        add_student()
        bot_btn.config(text="Update", command=save_student)
        view_win.destroy()

    bf = Frame(view_win)
    bf.grid(row=len(labels) + 1, column=0, columnspan=2, pady=20)
    Button(bf, text="Edit",  width=12, command=start_edit).pack(side=LEFT, padx=20)
    Button(bf, text="Close", width=12, command=view_win.destroy).pack(side=LEFT, padx=20)


def on_tree_click(event):
    region = student_table.identify("region", event.x, event.y)
    if region != "cell":
        return

    column_num = int(student_table.identify_column(event.x)[1:])
    item = student_table.identify_row(event.y)
    if not item:
        return

    visible_cols = len(student_table["displaycolumns"])
    if column_num == visible_cols:   # "View" column
        values = student_table.item(item, "values")
        if values:   
            view(values)


def on_closing():
    dm.save_all_to_csv(student_table)
    window.destroy()


# ─────────────────────────────────────────────────────────────
#  MAIN WINDOW SETUP
# ─────────────────────────────────────────────────────────────

window = Tk()
window.geometry("1100x619")
window.title("Student Management System")
#window.iconphoto(False, PhotoImage(file=""))
window.configure(bg="#fbfcfc")

window.columnconfigure(0, weight=1)
window.columnconfigure(1, weight=3)
window.rowconfigure(0, weight=1)

# Style

style = Style()
style.theme_use('clam')

# Button (rounded, pastel, hover)
style.configure("Pastel.TButton", font=("Segoe UI", 11, "bold"), padding=10)
style.map("Pastel.TButton",
          background=[('active', '#b3e0ff'), ('!disabled', '#a8d8ff')],
          foreground=[('active', '#2c3e50'), ('!disabled', '#2c3e50')])

# Entry & Combobox
style.configure("Pastel.TEntry", font=("Segoe UI", 10), padding=6)
style.configure("Pastel.TCombobox", font=("Segoe UI", 10))
style.map("Pastel.TCombobox", fieldbackground=[('readonly', 'white')])

# Treeview (alternating rows, modern headers)
style.configure("Pastel.Treeview", font=("Segoe UI", 10), rowheight=25)
style.configure("Pastel.Treeview.Heading", font=("Segoe UI", 11, "bold"), padding=6)
style.map("Pastel.Treeview",
          background=[('selected', '#c4f4e8'), ('!selected', '#f8f9fa')],
          foreground=[('selected', '#2c3e50')])

# Required note
style.configure("RedNote.TLabel", font=("Segoe UI", 10, "italic"), foreground="#e74c3c")






# ── Info and CRUDL Button Frame ──────────────────────────────
Info_btn_frame = tkinter.Frame(window, bg="#fbfcfc")
Info_btn_frame.grid(row=0, column=1, sticky="nsew", padx=(0,10), pady=0)

Info_btn_frame.rowconfigure(0, weight=1)
Info_btn_frame.rowconfigure(1, weight=15)
Info_btn_frame.columnconfigure(0, weight=1)
Info_btn_frame.rowconfigure(2, weight=1)

search_frame = tkinter.Frame(Info_btn_frame, bg="#055b65")
search_frame.grid(row=0, column=0, sticky="nsew", ipadx=20, pady=5)

search_frame.columnconfigure(0, weight=1)
search_frame.columnconfigure(1, weight=0)
search_frame.rowconfigure(0, weight=1)

sort_label = Label(search_frame, text="Sort by:", bg="#055b65", fg="white", font=("Arial", 9))
sort_label.grid(row=0, column=2, ipadx=10, pady=0, sticky="e")

sort_var = StringVar(value="Name")

sort_cb = Combobox(
    search_frame,
    textvariable=sort_var,
    values=["Name", "Student ID", "Year Level", "Program", "College"],
    state="readonly",
    width=16,
    font=("Arial", 9)
)
sort_cb.grid(row=0, column=3, padx=(5,10), pady=0)
sort_cb.bind("<<ComboboxSelected>>", sort_current_table)

info_frame = tkinter.Frame(Info_btn_frame)
info_frame.grid(row=1, column=0, sticky="nsew", padx=0, pady=0)

info_frame.rowconfigure(0, weight=1)
info_frame.columnconfigure(0, weight=1)

btn_frame = tkinter.Frame(Info_btn_frame, bg="#fbfcfc")
btn_frame.grid(row=2, column=0, sticky="nsew", padx=0, pady=0, columnspan=2)

# ── Add Student Frame ────────────────────────────────────────
add_student_frame = Frame(Info_btn_frame, bg="#45828b", bd=2, relief="groove")
add_student_frame.rowconfigure(0, weight=0)
add_student_frame.columnconfigure(0, weight=1)
add_student_frame.rowconfigure(1, weight=2)
add_student_frame.rowconfigure(2, weight=8)

add_top = Frame(add_student_frame, bg="#45828b")
add_top.grid(row=0, column=0, padx=0, pady=0, sticky="n")

add_mid = Frame(add_student_frame, bg="#45828b")
add_mid.grid(row=1, column=0, sticky="nsew", padx=0, ipadx=20, pady=0)

for i in range(3):
    add_mid.columnconfigure(i, weight=1)

add_prog = Frame(add_student_frame, bg="#45828b")
add_prog.grid(row=2, column=0, sticky="nsew", padx=0, pady=0)

add_prog.columnconfigure(0, weight=1)
add_prog.columnconfigure(1, weight=2)

add_bot = Frame(add_student_frame, bg="#45828b")
add_bot.grid(row=3, column=0, sticky="nsew", padx=0, pady=0)

# Personal Information
Label(add_top, text="Student Personal Information", bg="#45828b", highlightthickness=0, relief="flat").grid(pady=10, row=0, column=0, sticky="NSEW")

Label(add_mid, text="Student ID", bg="#45828b", highlightthickness=0, relief="flat").grid(padx=5, pady=0, row=0, column=0, sticky="W")
sid = Entry(add_mid, validate="key")
sid.config(validatecommand=(window.register(validate_student_id_action), '%P'))
sid.bind("<KeyRelease>", lambda e: auto_format_student_id(sid))
sid.grid(padx=5, pady=(0, 10), row=1, column=0, sticky="W", columnspan=3)

Label(add_mid, text="First Name*",  bg="#45828b", highlightthickness=0, relief="flat").grid(padx=5, pady=0, row=2, column=0, sticky="W")
fname = Entry(add_mid)
fname.grid(padx=5, pady=(0, 10), row=3, column=0, sticky="EW", columnspan=3)

Label(add_mid, text="Middle Name*", bg="#45828b", highlightthickness=0, relief="flat").grid(padx=5, row=2, column=1, sticky="W")
mname = Entry(add_mid)
mname.grid(padx=5, pady=(0, 10), row=3, column=1, sticky="EW")

Label(add_mid, text="Last Name*",   bg="#45828b", highlightthickness=0, relief="flat").grid(padx=5, row=2, column=2, sticky="W")
lname = Entry(add_mid)
lname.grid(padx=5, pady=(0, 10), row=3, column=2, sticky="EW")

Label(add_mid, text="Date of Birth", bg="#45828b", highlightthickness=0, relief="flat").grid(padx=5, row=4, column=0, sticky="W")

dob_frame = Frame(add_mid, bg="#45828b")
dob_frame.grid(row=5, column=0, sticky="W", padx=5, pady=(0, 10))

dob_year_cb = Combobox(dob_frame, values=list(range(1950, 2026)), state="readonly", width=5)
dob_year_cb.grid(row=0, column=0, padx=(0, 5))
dob_year_cb.set("")

dob_month_cb = Combobox(dob_frame, values=[f"{m:02d}" for m in range(1, 13)], state="readonly", width=3)
dob_month_cb.grid(row=0, column=1, padx=5)
dob_month_cb.set("")

dob_day_cb = Combobox(dob_frame, values=[f"{d:02d}" for d in range(1, 32)], state="readonly", width=3)
dob_day_cb.grid(row=0, column=2, padx=(5, 0))
dob_day_cb.set("")

Label(dob_frame, text="Year",  bg="#45828b", font=("Arial", 8), highlightthickness=0, relief="flat").grid(row=1, column=0)
Label(dob_frame, text="Month", bg="#45828b", font=("Arial", 8), highlightthickness=0, relief="flat").grid(row=1, column=1)
Label(dob_frame, text="Day",   bg="#45828b", font=("Arial", 8), highlightthickness=0, relief="flat").grid(row=1, column=2)

dob_year_cb.bind("<<ComboboxSelected>>",  lambda e: update_dob_days(dob_year_cb, dob_month_cb, dob_day_cb))
dob_month_cb.bind("<<ComboboxSelected>>", lambda e: update_dob_days(dob_year_cb, dob_month_cb, dob_day_cb))

Label(add_mid, text="Sex*", bg="#45828b", highlightthickness=0, relief="flat").grid(padx=5, row=4, column=1, sticky="W")
sex = Combobox(add_mid, width=18, values=["Male", "Female", "Other"], state="readonly")
sex.grid(padx=0, pady=0, row=5, column=1, sticky="EW")

Label(add_mid, text="Contact Number", bg="#45828b", highlightthickness=0, relief="flat").grid(padx=5, row=6, column=0, sticky="W")
cnumber = Entry(add_mid)
cnumber.grid(padx=5, pady=(0, 10), row=7, column=0, sticky="EW")

Label(add_mid, text="Email", bg="#45828b", highlightthickness=0, relief="flat").grid(padx=5, row=6, column=1, sticky="W")
email = Entry(add_mid)
email.grid(padx=5, pady=(0, 10), row=7, column=1, sticky="EW")

Label(add_mid, text="Address", bg="#45828b", highlightthickness=0, relief="flat").grid(padx=5, row=8, column=0, sticky="W")
address = Entry(add_mid)
address.grid(padx=5, pady=(0, 10), row=9, column=0, sticky="EW", columnspan=3)

# Program Information
Label(add_prog, text="Student Program Information*", bg="#45828b", highlightthickness=0, relief="flat",
      font=("Arial", 11, "bold")).grid(row=0, column=0, columnspan=2, pady=10, sticky="eW")

Label(add_prog, text="Current Year Level", bg="#45828b", highlightthickness=0, relief="flat").grid(row=1, column=0, padx=5, pady=5, sticky="W")
year_cb = Combobox(add_prog, values=["1st Year", "2nd Year", "3rd Year", "4th Year"], state="readonly")
year_cb.grid(row=1, column=1, padx=5, pady=5, sticky="EW")

Label(add_prog, text="College", bg="#45828b", highlightthickness=0, relief="flat").grid(row=2, column=0, padx=5, pady=5, sticky="W")
college_cb = Combobox(add_prog, values=[], state="readonly")
college_cb.grid(row=2, column=1, padx=5, pady=5, sticky="EW")

Label(add_prog, text="Program", bg="#45828b", highlightthickness=0, relief="flat").grid(row=3, column=0, padx=5, pady=5, sticky="W")
program_cb = Combobox(add_prog, state="disabled")
program_cb.grid(row=3, column=1, padx=5, pady=5, sticky="EW")

college_cb.bind("<<ComboboxSelected>>", update_programs)

bot_btn = Button(add_bot, text="Save", bg="#fbfcfc", width=10, height=2, command=save_student)
bot_btn.pack(side=RIGHT, padx=5, pady=5)

bot_btn2 = Button(add_bot, text="Cancel", bg="#fbfcfc", width=10, height=2, command=add_student_frame.grid_remove)
bot_btn2.pack(side=RIGHT, padx=5, pady=5)

Label(add_bot, text="* Required Fields", font=("Arial", 8, "italic"), bg="#45828b", fg="red", highlightthickness=0, relief="flat").pack(side=LEFT, padx=5, pady=5)

# ── Add Program Frame ────────────────────────────────────────
add_program_frame = Frame(Info_btn_frame, bg="#45828b", bd=2, relief=RAISED)
add_program_frame.grid(row=0, column=1, sticky="nsew", padx=(5, 5), pady=(5, 0), rowspan=2)
add_program_frame.grid_remove()

add_program_frame.rowconfigure(0, weight=0)
add_program_frame.rowconfigure(1, weight=1)
add_program_frame.rowconfigure(2, weight=0)
add_program_frame.columnconfigure(0, weight=1)

add_program_frame_top = Frame(add_program_frame, bg="#45828b",highlightthickness=0, relief="flat")
add_program_frame_top.grid(row=0, column=0, sticky="ew", padx=10, pady=10)

Label(add_program_frame_top, text="Add Program", bg="#45828b",highlightthickness=0, relief="flat",
      font=("Arial", 12, "bold")).grid(row=0, column=0, pady=5, sticky="w")

Label(add_program_frame_top, text="Program Code", bg="#45828b",highlightthickness=0, relief="flat").grid(row=1, column=0, sticky="w", pady=2)
prog_id_entry = Entry(add_program_frame_top, width=35)
prog_id_entry.grid(row=2, column=0, pady=5, sticky="ew")

Label(add_program_frame_top, text="Program Name", bg="#45828b",highlightthickness=0, relief="flat").grid(row=3, column=0, sticky="w", pady=2)
prog_name_entry = Entry(add_program_frame_top, width=35)
prog_name_entry.grid(row=4, column=0, pady=5, sticky="ew")

Label(add_program_frame_top, text="College", bg="#45828b",highlightthickness=0, relief="flat").grid(row=5, column=0, sticky="w", pady=2)
prog_college_cb = Combobox(add_program_frame_top, values=[], state="readonly", width=32)
prog_college_cb.grid(row=6, column=0, pady=5, sticky="ew")

add_program_frame_bot = Frame(add_program_frame, bg="#45828b",highlightthickness=0, relief="flat")
add_program_frame_bot.grid(row=2, column=0, sticky="sew", padx=10, pady=10)

btn_frame_prog = Frame(add_program_frame_bot, bg="#45828b",highlightthickness=0, relief="flat")
btn_frame_prog.pack(side=BOTTOM, fill=X)

ttk.Button(btn_frame_prog, text="Save", style="Pastel.TButton",   command=save_program).pack(side=RIGHT, padx=10)
ttk.Button(btn_frame_prog, text="Cancel", style="Pastel.TButton",  command=add_program_frame.grid_remove).pack(side=RIGHT, padx=10)

# ── Add College Frame ────────────────────────────────────────
add_college_frame = Frame(Info_btn_frame, bg="#45828b", bd=2, relief=RAISED)
add_college_frame.grid(row=0, column=1, sticky="nsew", padx=(5, 5), pady=(5, 0), rowspan=2)
add_college_frame.grid_remove()

add_college_frame.rowconfigure(0, weight=0)
add_college_frame.rowconfigure(1, weight=1)
add_college_frame.rowconfigure(2, weight=0)
add_college_frame.columnconfigure(0, weight=1)

add_college_frame_top = Frame(add_college_frame, bg="#45828b")
add_college_frame_top.grid(row=0, column=0, sticky="ew", padx=10, pady=10)

Label(add_college_frame_top, text="Add College", bg="#45828b", highlightthickness=0, relief="flat",
      font=("Arial", 12, "bold")).grid(row=0, column=0, pady=5, sticky="w")

Label(add_college_frame_top, text="College Code", bg="#45828b",highlightthickness=0, relief="flat").grid(row=1, column=0, sticky="w", pady=2)
college_id_entry = Entry(add_college_frame_top, width=35)
college_id_entry.grid(row=2, column=0, pady=5, sticky="ew")

Label(add_college_frame_top, text="College Name", bg="#45828b",highlightthickness=0, relief="flat").grid(row=3, column=0, sticky="w", pady=2)
college_name_entry = Entry(add_college_frame_top, width=35)
college_name_entry.grid(row=4, column=0, pady=5, sticky="ew")

add_college_frame_bot = Frame(add_college_frame, bg="#45828b",highlightthickness=0, relief="flat")
add_college_frame_bot.grid(row=2, column=0, sticky="sew", padx=10, pady=10)

btn_frame_col = Frame(add_college_frame_bot, bg="#45828b",highlightthickness=0, relief="flat")
btn_frame_col.pack(side=BOTTOM, fill=X)

Button(btn_frame_col, text="Save",   command=save_college).pack(side=RIGHT, padx=10)
Button(btn_frame_col, text="Cancel", command=add_college_frame.grid_remove).pack(side=RIGHT, padx=10)

# ── Navigation Frame ─────────────────────────────────────────
navframe = tkinter.Frame(window, bg="#e0e5e9", width=150)
navframe.grid(row=0, column=0, sticky="nsew", padx=5, pady=10)
navframe.grid_propagate(False)

navframe.rowconfigure(0, weight=1)
navframe.rowconfigure(1, weight=5)
navframe.columnconfigure(0, weight=1)

logo_frame = tkinter.Frame(navframe, bg="#e0e5e9")
logo_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=(10, 5))

nav_btn_frame = tkinter.Frame(navframe, bg="#e0e5e9")
nav_btn_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=(0, 10))

# ── Search Frame ─────────────────────────────────────────────
search_entry = Entry(search_frame)
search_entry.grid(row=0, column=0, sticky="ew", padx=5, pady=5)

search_button = ttk.Button(search_frame, text="Search", style="Pastel.TButton", width=10, command=search_current)
search_button.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

# ── Navigation Buttons ───────────────────────────────────────
student_btn =  ttk.Button(nav_btn_frame, text="Student", style="Pastel.TButton", width=10, command=student_list)
student_btn.pack(side=TOP, fill=X, padx=5, pady=5)

program_btn = ttk.Button(nav_btn_frame, text="Program", style="Pastel.TButton", width=10,  command=program_list)
program_btn.pack(side=TOP, fill=X, padx=5, pady=5)

college_btn = ttk.Button(nav_btn_frame, text="College", style="Pastel.TButton", width=10, command=college_list)
college_btn.pack(side=TOP, fill=X, padx=5, pady=5)

logout_btn  = ttk.Button(nav_btn_frame, text="Logout",  style="Pastel.TButton", width=10)
logout_btn.pack(side=BOTTOM, fill=X, padx=5, pady=5)

history_btn = ttk.Button(nav_btn_frame, text="History", style="Pastel.TButton", width=10)
history_btn.pack(side=BOTTOM, fill=X, padx=5, pady=5)

add_btn    = ttk.Button(btn_frame, text="Add Student", style="Pastel.TButton", width=15,  command=add_student)
add_btn.pack(side=RIGHT, padx=5, pady=5)

delete_btn = ttk.Button(btn_frame, text="Delete", style="Pastel.TButton", width=15,  command=delete_item)
delete_btn.pack(side=RIGHT, padx=5, pady=5)

clear_btn  = ttk.Button(btn_frame, text="Clear",  style="Pastel.TButton", width=15, command=clear_list)
clear_btn.pack(side=RIGHT, padx=5, pady=5)

# ── Program List Treeview ────────────────────────────────────
program_framebtn = Frame(info_frame, bg="lightblue", relief=RAISED, bd=2)
program_framebtn.grid(row=0, column=0, sticky="nsew")

Label(program_framebtn, text="Program List", bg="#055b65", highlightthickness=0, relief="flat", fg="white",
      font=("Arial", 14, "bold"), pady=8).pack(side=TOP, fill=X)

y2_scroll = Scrollbar(program_framebtn, orient=VERTICAL)
y2_scroll.pack(side=RIGHT, fill=Y)

program_table = ttk.Treeview(
    program_framebtn,
    style="Pastel.Treeview",
    columns=("Program ID", "Program Name", "College", "No. of Students"),
    show="headings",
    yscrollcommand=y2_scroll.set
)
program_table.heading("Program ID",      text="Program ID")
program_table.heading("Program Name",    text="Program Name")
program_table.heading("College",         text="College")
program_table.heading("No. of Students", text="No. of Students")
program_table.column("Program ID",      width=100)
program_table.column("Program Name",    width=200)
program_table.column("College",         width=80)
program_table.column("No. of Students", width=100)

for col in program_table["columns"]:
    program_table.heading(col, command=lambda c=col: treeview_sort_column(program_table, c, False))

y2_scroll.config(command=program_table.yview)
program_table.pack(side=LEFT, fill=BOTH, expand=True)

# ── College List Treeview ────────────────────────────────────
college_framebtn = Frame(info_frame, bg="#fbfcfc", relief=RAISED, bd=2)
college_framebtn.grid(row=0, column=0, sticky="nsew")

Label(college_framebtn, text="College List", bg="#055b65", highlightthickness=0, relief="flat", fg="white",
      font=("Arial", 14, "bold"), pady=8).pack(side=TOP, fill=X)

y3_scroll = Scrollbar(college_framebtn, orient=VERTICAL)
y3_scroll.pack(side=RIGHT, fill=Y)

college_table = ttk.Treeview(
    college_framebtn,
    style="Pastel.Treeview",
    columns=("College ID", "College Name", "No. of Programs", "No. of Students"),
    show="headings",
    yscrollcommand=y3_scroll.set
)
college_table.heading("College ID",      text="College ID")
college_table.heading("College Name",    text="College Name")
college_table.heading("No. of Programs", text="No. of Programs")
college_table.heading("No. of Students", text="No. of Students")
college_table.column("College ID",      width=100)
college_table.column("College Name",    width=200)
college_table.column("No. of Programs", width=80)
college_table.column("No. of Students", width=100)

y3_scroll.config(command=college_table.yview)
college_table.pack(side=LEFT, fill=BOTH, expand=True)

for col in college_table["columns"]:
    college_table.heading(col, command=lambda c=col: treeview_sort_column(college_table, c, False))

# ── Student List Treeview ────────────────────────────────────
student_framebtn = Frame(info_frame, bg="#055b65", relief=FLAT, bd=2)
student_framebtn.grid(row=0, column=0, sticky="nsew")

y_scroll = Scrollbar(student_framebtn, orient=VERTICAL)
y_scroll.pack(side=RIGHT, fill=Y)

Label(student_framebtn, text="Student List", bg="#055b65", highlightthickness=0, relief="flat", fg="white",
      font=("Arial", 14, "bold"), pady=0).pack(side=TOP, fill=X)

student_table = ttk.Treeview(
    student_framebtn,
    style="Pastel.Treeview",
    yscrollcommand=y_scroll.set,
    columns=("ID", "Name", "Year Level", "Program", "College",
             "DOB", "Sex", "Contact", "Email", "Address", "View"),
    displaycolumns=("ID", "Name", "Year Level", "Program", "College", "View"),
    show="headings"
)
student_table.heading("ID",         text="Student ID")
student_table.heading("Name",       text="Name")
student_table.heading("Year Level", text="Year Level")
student_table.heading("Program",    text="Program")
student_table.heading("College",    text="College")
student_table.heading("View",       text="")

student_table.column("ID",         width=100)
student_table.column("Name",       width=200)
student_table.column("Year Level", width=80)
student_table.column("Program",    width=100)
student_table.column("College",    width=100)
student_table.column("View",       width=80, anchor="center")

for col in student_table["columns"]:
    if col != "View":
        student_table.heading(col, command=lambda c=col: treeview_sort_column(student_table, c, False))

for col in ["DOB", "Sex", "Contact", "Email", "Address"]:
    student_table.column(col, width=0, stretch=False)

student_table.pack(side=LEFT, fill=BOTH, expand=True)
student_table.bind("<Button-1>", on_tree_click)

# ── Load data ────────────────────────────────────────────────
dm.load_colleges(college_table)
dm.load_programs(program_table)
dm.load_students_from_csv(
    student_table,
    update_all_program_counts_fn=lambda: dm.update_all_program_counts(student_table, program_table),
    update_all_college_counts_fn=lambda: dm.update_all_college_counts(student_table, college_table)
)

refresh_college_comboboxes()
refresh_programs()

window.protocol("WM_DELETE_WINDOW", on_closing)
window.mainloop()
