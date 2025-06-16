import sqlite3
import os
import tkinter as tk
from tkinter import messagebox
from datetime import datetime, timedelta


login_root = tk.Tk()
login_root.title("Open Screen")

username_label = tk.Label(login_root, text="Username:")
username_label.pack()
username_entry = tk.Entry(login_root,show="*")
username_entry.pack()

password_label = tk.Label(login_root, text="Password:")
password_label.pack()
password_entry = tk.Entry(login_root, show="#")
password_entry.pack()

def check_credentials(username, password):
    try:
        conn = sqlite3.connect("users.db")
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
        user = cursor.fetchone()
        conn.close()

        if user:
            return True  
        else:
            return False  
    except sqlite3.Error:
        return False  

def histor(usr, pswd):
    try:
        conn = sqlite3.connect("users.db")
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username=? AND password=?", (usr,pswd))
        user = cursor.fetchone()
        conn.close()

        if user:
            return True  
        else:
            return False  
    except sqlite3.Error:
        return False  


def login():
    entered_username = username_entry.get()
    entered_password = password_entry.get()

    if check_credentials(entered_username, entered_password):
        login_root.destroy()
    else:
        messagebox.showerror("Error", "Wrong Username or Wrong Password")

login_button = tk.Button(login_root, text="Main App", command=login)

login_button.pack()
conn = sqlite3.connect("users.db")
cursor = conn.cursor()

def register():
    entered_username = username_entry.get()
    entered_password = password_entry.get()

    try:
        conn = sqlite3.connect("users.db")
        cursor = conn.cursor()
        cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (entered_username, entered_password))
        conn.commit()
        conn.close()
        messagebox.showinfo("Sucesfully", "User Be Add The Database")
    except sqlite3.IntegrityError:
        messagebox.showerror("Error", "This User Be Add In The Past")

register_button = tk.Button(login_root, text="Registering", command=register)
register_button.pack()

cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        username TEXT PRIMARY KEY,
        password TEXT
    )
''')
conn.commit()
conn.close()

login_root.mainloop()

history_conn = sqlite3.connect("history.db")
history_cursor = history_conn.cursor()

history_cursor.execute('''
    CREATE TABLE IF NOT EXISTS parking_history (
        action TEXT,
        vehicle_type TEXT,
        plate TEXT,
        brand TEXT,
        model TEXT,
        color TEXT,
        owner_name TEXT,
        owner_contact TEXT,
        entry_time TEXT,
        timestamp TEXT
    )
''')
history_conn.commit()

def log_history(action, vehicle):
    timestamp = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
    history_cursor.execute('''
        INSERT INTO parking_history (action, vehicle_type, plate, brand, model, color, owner_name, owner_contact, entry_time, timestamp)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (action, vehicle.vehicle_type, vehicle.plate, vehicle.brand, vehicle.model, vehicle.color, vehicle.owner_name, vehicle.owner_contact, vehicle.entry_time, timestamp))
    history_conn.commit()

def create_if_not_exists(file_name):
    if not os.path.exists(file_name):
        with open(file_name, "w") as file:
             pass

create_if_not_exists("start_and_finish_time.txt")

conn = sqlite3.connect("record.db")
cursor = conn.cursor()

cursor.execute('''
    CREATE TABLE IF NOT EXISTS vehicles (
        vehicle_type TEXT,
        plate TEXT PRIMARY KEY,
        brand TEXT,
        model TEXT,
        color TEXT,
        owner_name TEXT,
        owner_contact TEXT,
        entry_time TEXT
    )
''')
conn.commit()


def log_start_time():
    start_time = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
    with open("start_and_finish_time.txt", "a") as file:
        file.write( "App Is Be Running: " + start_time + "\n")

log_start_time() 

class Vehicle:
    def __init__(self, vehicle_type, plate, brand, model, color, owner_name, owner_contact, entry_time):
        self.vehicle_type = vehicle_type
        self.plate = plate
        self.brand = brand
        self.model = model
        self.color = color
        self.owner_name = owner_name
        self.owner_contact = owner_contact
        self.entry_time = entry_time
        self.parking_fee = 0

class ParkingSystem:
    def __init__(self):
        self.start_time = datetime.now()  

    def add_vehicle(self, vehicle):
        try:
            cursor.execute('''
                INSERT INTO vehicles VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (vehicle.vehicle_type, vehicle.plate, vehicle.brand, vehicle.model, vehicle.color, vehicle.owner_name, vehicle.owner_contact, vehicle.entry_time))
            conn.commit()
            messagebox.showinfo("Inf", "Vehicle Be Add")
        except sqlite3.IntegrityError:
            messagebox.showinfo("Inf", "Wehicle Already Registered")

    def remove_vehicle(self, plate):
        try:
            cursor.execute('DELETE FROM vehicles WHERE plate=?', (plate,))
            conn.commit()
            return True
        except sqlite3.Error:
            return False

    def search_vehicle(self, plate):
        cursor.execute('SELECT * FROM vehicles WHERE plate=?', (plate,))
        row = cursor.fetchone()
        if row:
            vehicle_type, plate, brand, model, color, owner_name, owner_contact, entry_time = row
            return Vehicle(vehicle_type, plate, brand, model, color, owner_name, owner_contact, entry_time)
        else:
            return None

    def calculate_parking_duration(self, entry_time):
        now = datetime.now()
        entry_time = datetime.strptime(entry_time, "%d-%m-%Y %H:%M:%S")
        duration = now - entry_time
        return duration

    def calculate_parking_fee(self, parking_duration):
        hours, remainder = divmod(parking_duration.seconds, 3600)
        minutes, _ = divmod(remainder, 60)
        total_minutes = hours * 60 + minutes
        fee = (total_minutes // 1) * 2
        return fee

    def calculate_uptime(self):
        uptime = datetime.now() - self.start_time
        return uptime

parking_system = ParkingSystem()

def add_vehicle():
    vehicle_type = type_entry.get()
    plate = plate_entry.get()
    brand = brand_entry.get()
    model = model_entry.get()
    color = color_entry.get()
    owner_name = owner_name_entry.get()
    owner_contact = owner_contact_entry.get()
    entry_time = datetime.now().strftime("%d-%m-%Y %H:%M:%S")

    new_vehicle = Vehicle(vehicle_type, plate, brand, model, color, owner_name, owner_contact, entry_time)
    parking_system.add_vehicle(new_vehicle)
    log_history("adding", new_vehicle)

def remove_vehicle():
    plate = plate_entry.get()
    vehicle = parking_system.search_vehicle(plate)
    if vehicle:
        removed = parking_system.remove_vehicle(plate)
        if removed:
            messagebox.showinfo("Inf", "Vehicle Is Be Delete.")
            log_history("kayıt silme", vehicle) 
        else:
            messagebox.showinfo("Inf", "Error About Delete.")
    else:
        messagebox.showinfo("Inf", "Vehicle Is Dont Find.")

def search_vehicle():
    plate = plate_entry.get()
    vehicle = parking_system.search_vehicle(plate)
    if vehicle:
        parking_duration = parking_system.calculate_parking_duration(vehicle.entry_time)
        parking_fee = parking_system.calculate_parking_fee(parking_duration)
        result_text.set(f"Type: {vehicle.vehicle_type}\nBrand: {vehicle.brand}\nModel: {vehicle.model}\nColor: {vehicle.color}\nOwnerName: {vehicle.owner_name}\nOwnerContact: {vehicle.owner_contact}\nParc Time: {parking_duration}\nfee: {parking_fee} TL")
    else:
        result_text.set("Dont Be Find.")

def show_uptime():
    uptime = parking_system.calculate_uptime()
    uptime_str = str(uptime).split('.')[0]
    uptime_label.config(text=f"Total Using Time: {uptime_str}")
    root.after(1000, show_uptime)

root = tk.Tk()
root.title("Ana Ekran")

type_label = tk.Label(root, text="Type:")
type_label.pack()
type_entry = tk.Entry(root)
type_entry.pack()

plate_label = tk.Label(root, text="Plate:")
plate_label.pack()
plate_entry = tk.Entry(root)
plate_entry.pack()

brand_label = tk.Label(root, text="Brand")
brand_label.pack()
brand_entry = tk.Entry(root)
brand_entry.pack()

model_label = tk.Label(root, text="Model:")
model_label.pack()
model_entry = tk.Entry(root)
model_entry.pack()

color_label = tk.Label(root, text="Color:")
color_label.pack()
color_entry = tk.Entry(root)
color_entry.pack()

owner_name_label = tk.Label(root, text="Owner Name and Surname:")
owner_name_label.pack()
owner_name_entry = tk.Entry(root)
owner_name_entry.pack()

owner_contact_label = tk.Label(root, text="Owner Contact Info")
owner_contact_label.pack()
owner_contact_entry = tk.Entry(root)
owner_contact_entry.pack()

add_button = tk.Button(root, text="Vehicle Add", command=add_vehicle)
add_button.pack()

remove_button = tk.Button(root, text="Vehicle Delete", command=remove_vehicle)
remove_button.pack()

search_button = tk.Button(root, text="Vehicle Query", command=search_vehicle)
search_button.pack()

result_text = tk.StringVar()
result_label = tk.Label(root, textvariable=result_text)
result_label.pack()

uptime_label = tk.Label(root, text="Total Using Time: 00:00:00")
uptime_label.pack()

def show_current_time():
    current_time = datetime.now().strftime("%d-%m-%y %H:%M:%S")
    current_time_label.config(text=f"Turkish Time Is: {current_time}")
    root.after(1000, show_current_time)

current_time_label = tk.Label(root, text="Turkish Time: ")
current_time_label.pack()

def close_program():
    finish_time = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
    with open("start_and_finish_time.txt", "a") as file:
        file.write("Shoting Down: " + finish_time + "\n")
    quit()
    
close_button = tk.Button(root, text="Shot Down", command=close_program)
close_button.pack()


def panel_oppener():
		root.destroy()
	
panel_button = tk.Button(root,text="History Review Screen",command=panel_oppener)
panel_button.pack()

show_current_time()
show_uptime()
root.mainloop()

import tkinter as tk
import sqlite3
from datetime import datetime

panel = tk.Tk()
panel.title("History")

with open("start_and_finish_time.txt", "a") as file:
    file.write("Uygulama geçmiş sorulama panelinde tekrar açıldı " +  "\n")

history_conn = sqlite3.connect("history.db")
history_cursor = history_conn.cursor()

history_cursor.execute('''
    CREATE TABLE IF NOT EXISTS parking_history (
        action TEXT,
        vehicle_type TEXT,
        plate TEXT,
        brand TEXT,
        model TEXT,
        color TEXT,
        owner_name TEXT,
        owner_contact TEXT,
        entry_time TEXT,
        timestamp TEXT
    )
''')
history_conn.commit()

type_label = tk.Label(panel, text="Type:")
type_label.pack()
type_entry = tk.Entry(panel)
type_entry.pack()

plate_label = tk.Label(panel, text="Plate:")
plate_label.pack()
plate_entry = tk.Entry(panel)
plate_entry.pack()

brand_label = tk.Label(panel, text="Brand:")
brand_label.pack()
brand_entry = tk.Entry(panel)
brand_entry.pack()

model_label = tk.Label(panel, text="Model:")
model_label.pack()
model_entry = tk.Entry(panel)
model_entry.pack()

color_label = tk.Label(panel, text="Color:")
color_label.pack()
color_entry = tk.Entry(panel)
color_entry.pack()

owner_name_label = tk.Label(panel, text="Owner Name and Surname:")
owner_name_label.pack()
owner_name_entry = tk.Entry(panel)
owner_name_entry.pack()

owner_contact_label = tk.Label(panel, text="Owner Contact Information:")
owner_contact_label.pack()
owner_contact_entry = tk.Entry(panel)
owner_contact_entry.pack()

def show_history():
    plate = plate_entry.get()
    history_cursor.execute('SELECT * FROM parking_history WHERE plate=?', (plate,))
    history_entries = history_cursor.fetchall()

    if history_entries:
        history_text = "History:\n"
        for entry in history_entries:
            action, vehicle_type, plate, brand, model, color, owner_name, owner_contact, entry_time, timestamp = entry
            history_text += f"Change: {action}, Time: {timestamp}\n"

        result_text.set(history_text)
    else:
        result_text.set("Be Not Find Ind The History")

show_history_button = tk.Button(panel, text="Watch History", command=show_history)
show_history_button.pack()

result_text = tk.StringVar()
result_label = tk.Label(panel, textvariable=result_text)
result_label.pack()

def close_program2():
    finish_time = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
    with open("start_and_finish_time.txt", "a") as file:
        file.write("History Watching" + finish_time + "\n")
    panel.quit()
    
close_button = tk.Button(panel, text="Shot Down", command=close_program2)
close_button.pack()

panel.mainloop()