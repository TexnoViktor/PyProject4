import tkinter as tk
from tkinter import simpledialog, messagebox, Toplevel
import pandas as pd
import sqlite3

# Підключення до бази даних
conn = sqlite3.connect('dormitory.db')
c = conn.cursor()


def create_tables():
    c.execute('''
        CREATE TABLE IF NOT EXISTS Students (
            ID INTEGER PRIMARY KEY AUTOINCREMENT,
            FirstName TEXT,
            LastName TEXT,
            Age INTEGER,
            Gender TEXT,
            PhoneNumber TEXT,
            Email TEXT,
            RoomNumber INTEGER
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS Administrators (
            ID INTEGER PRIMARY KEY AUTOINCREMENT,
            FirstName TEXT,
            LastName TEXT,
            ContactInfo TEXT
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS Rooms (
            RoomNumber INTEGER PRIMARY KEY,
            Floor INTEGER,
            BedCount INTEGER,
            OccupiedBeds INTEGER
        )
    ''')
    conn.commit()


create_tables()


def add_data(window_title, table_name, fields):
    def submit():
        values = [entry.get() for entry in entries]
        placeholders = ', '.join('?' * len(values))
        c.execute(f'INSERT INTO {table_name} ({", ".join(fields.keys())}) VALUES ({placeholders})', values)
        if table_name == "Students":
            # Оновлення зайнятих місць у кімнаті
            room_number = values[fields["RoomNumber"]]
            c.execute('UPDATE Rooms SET OccupiedBeds = OccupiedBeds + 1 WHERE RoomNumber = ?', (room_number,))
        conn.commit()
        messagebox.showinfo("Success", "Data added successfully!")
        top.destroy()
        display_data(table_name)

    top = Toplevel(root)
    top.title(f"Add {window_title}")
    top.geometry("300x400")
    top.attributes('-topmost', 'true')

    entries = []
    for field, label in fields.items():
        tk.Label(top, text=label).pack()
        entry = tk.Entry(top)
        entry.pack()
        entries.append(entry)

    if table_name == "Students":
        tk.Label(top, text="Room Number").pack()
        room_var = tk.IntVar(top)
        c.execute('SELECT RoomNumber FROM Rooms WHERE OccupiedBeds < BedCount')
        available_rooms = [room[0] for room in c.fetchall()]
        if available_rooms:
            tk.OptionMenu(top, room_var, *available_rooms).pack()
            entries.append(room_var)  # Оновлено тут
        else:
            messagebox.showerror("Error", "No rooms available!")
            return

    submit_btn = tk.Button(top, text="Submit", command=submit)
    submit_btn.pack()


def delete_data(table_name, id_value):
    c.execute(f'DELETE FROM {table_name} WHERE ID = ?', (id_value,))
    if table_name == "Students":
        student = c.execute('SELECT RoomNumber FROM Students WHERE ID = ?', (id_value,)).fetchone()
        if student:
            room_number = student[0]
            c.execute('UPDATE Rooms SET OccupiedBeds = OccupiedBeds - 1 WHERE RoomNumber = ?', (room_number,))
    conn.commit()
    messagebox.showinfo("Success", "Data deleted successfully!")
    display_data(table_name)


def display_data(table_name):
    df = pd.read_sql_query(f"SELECT * FROM {table_name}", conn)
    top = Toplevel(root)
    top.title(f"{table_name} Data")
    tk.Label(top, text=df).pack()


root = tk.Tk()
root.title("Dormitory Management System")
root.geometry("600x500")

tk.Button(root, text="Add Student", command=lambda: add_data("Student", "Students", {
    "FirstName": "First Name", "LastName": "Last Name", "Age": "Age",
    "Gender": "Gender", "PhoneNumber": "Phone Number", "Email": "Email", "RoomNumber": "Room Number"
})).pack(pady=10)

tk.Button(root, text="Add Administrator", command=lambda: add_data("Administrator", "Administrators", {
    "FirstName": "First Name", "LastName": "Last Name", "ContactInfo": "Contact Info"
})).pack(pady=10)

tk.Button(root, text="Add Room", command=lambda: add_data("Room", "Rooms", {
    "RoomNumber": "Room Number", "Floor": "Floor", "BedCount": "Bed Count", "OccupiedBeds": "Occupied Beds"
})).pack(pady=10)

tk.Button(root, text="Delete Student",
          command=lambda: delete_data("Students", simpledialog.askinteger("Input", "Student ID"))).pack(pady=10)

tk.Button(root, text="Delete Administrator",
          command=lambda: delete_data("Administrators", simpledialog.askinteger("Input", "Administrator ID"))).pack(
    pady=10)

tk.Button(root, text="Delete Room",
          command=lambda: delete_data("Rooms", simpledialog.askinteger("Input", "Room Number"))).pack(pady=10)

tk.Button(root, text="Display Students", command=lambda: display_data("Students")).pack(pady=10)

tk.Button(root, text="Display Administrators", command=lambda: display_data("Administrators")).pack(pady=10)

tk.Button(root, text="Display Rooms", command=lambda: display_data("Rooms")).pack(pady=10)

root.mainloop()
