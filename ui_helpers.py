from tkinter import END

def validate_student_id_action(new_value):
    if new_value == "":
        return True
    cleaned = new_value.replace("-", "")
    if len(cleaned) > 8:
        return False
    if not cleaned.isdigit():
        return False
    if "-" in new_value:
        parts = new_value.split("-")
        if len(parts) != 2:
            return False
        if len(parts[0]) != 4 or not parts[0].isdigit():
            return False
        if len(parts[1]) > 4:
            return False
    return True


def auto_format_student_id(sid_entry):
    value = sid_entry.get()
    cleaned = value.replace("-", "")
    if len(cleaned) >= 4 and len(value) < 5:
        new_value = cleaned[:4] + "-" + cleaned[4:]
        sid_entry.delete(0, END)
        sid_entry.insert(0, new_value)
        sid_entry.icursor(END)


def treeview_sort_column(tv, col, reverse):
    data = [(tv.set(child, col), child) for child in tv.get_children('')]
    try:
        data.sort(key=lambda t: (float(t[0]) if t[0].replace('.', '').isdigit() else t[0].lower(), t[1]), reverse=reverse)
    except:
        data.sort(key=lambda t: (t[0].lower(), t[1]), reverse=reverse)
    for index, (val, child) in enumerate(data):
        tv.move(child, '', index)
    tv.heading(col, command=lambda: treeview_sort_column(tv, col, not reverse))


def update_dob_days(dob_year_cb, dob_month_cb, dob_day_cb, *args):
    month = dob_month_cb.get()
    year  = dob_year_cb.get()

    if not (month and year):
        dob_day_cb["values"] = []
        dob_day_cb.set("")
        return

    try:
        m = int(month)
        y = int(year)
    except ValueError:
        dob_day_cb["values"] = []
        dob_day_cb.set("")
        return

    days_in_month = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]

    if m == 2 and ((y % 4 == 0 and y % 100 != 0) or (y % 400 == 0)):
        days_in_month[1] = 29

    max_d = days_in_month[m - 1]
    dob_day_cb["values"] = [f"{d:02d}" for d in range(1, max_d + 1)]

    curr = dob_day_cb.get()
    if curr and int(curr) <= max_d:
        dob_day_cb.set(curr)
    else:
        dob_day_cb.set("")

