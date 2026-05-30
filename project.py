import tkinter as tk
from tkinter import ttk, messagebox
import mysql.connector

# ------------------ DATABASE CONNECTION ------------------
def connect_db():
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="0000",
            database="hospital_db"
        )
        return conn
    except mysql.connector.Error as err:
        messagebox.showerror("Database Error", f"Error: {err}")
        return None

# ------------------ FETCH PATIENT NAMES ------------------
def get_patient_names():
    conn = connect_db()
    if conn:
        cur = conn.cursor()
        cur.execute("SELECT name FROM patients ORDER BY name")
        names = [r[0] for r in cur.fetchall()]
        conn.close()
        return names
    return []

# ------------------ FETCH DOCTOR NAMES ------------------
def get_doctor_names():
    conn = connect_db()
    if conn:
        cur = conn.cursor()
        cur.execute("SELECT name FROM doctors ORDER BY name")
        names = [r[0] for r in cur.fetchall()]
        conn.close()
        return names
    return []

# ------------------ REFRESH COMBOBOXES ------------------
def refresh_comboboxes():
    a_patient['values'] = get_patient_names()
    a_doctor['values'] = get_doctor_names()

# ------------------ ADD PATIENT ------------------
def add_patient():
    conn = connect_db()
    if conn:
        cur = conn.cursor()
        try:
            cur.execute("""
                INSERT INTO patients (name, age, gender, phone, location, guardian_name, guardian_phone)
                VALUES (%s,%s,%s,%s,%s,%s,%s)
            """, (
                p_name.get(), p_age.get(), p_gender.get(), p_phone.get(),
                p_loc.get(), p_guardian.get(), p_guardian_phone.get()
            ))
            conn.commit()
            messagebox.showinfo("Success", "✅ Patient Added Successfully!")
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Failed to add patient: {err}")
        finally:
            conn.close()

# ------------------ VIEW PATIENTS ------------------
def view_patients():
    conn = connect_db()
    if conn:
        cur = conn.cursor()
        cur.execute("SELECT patient_id, name, age, gender, phone FROM patients")
        records = cur.fetchall()
        view_text.delete(1.0, tk.END)
        for r in records:
            view_text.insert(tk.END, f"🧍 ID: {r[0]} | {r[1]} | Age: {r[2]} | {r[3]} | 📞 {r[4]}\n")
        conn.close()

# ------------------ ADD DOCTOR ------------------
def add_doctor():
    conn = connect_db()
    if conn:
        cur = conn.cursor()
        try:
            cur.execute("""
                INSERT INTO doctors (name, specialization, experience, phone, email)
                VALUES (%s,%s,%s,%s,%s)
            """, (
                d_name.get(), d_spec.get(), d_exp.get(),
                d_phone.get(), d_email.get()
            ))
            conn.commit()
            messagebox.showinfo("Success", "👨‍⚕ Doctor Added Successfully!")
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Failed to add doctor: {err}")
        finally:
            conn.close()

# ------------------ VIEW DOCTORS ------------------
def view_doctors():
    conn = connect_db()
    if conn:
        cur = conn.cursor()
        cur.execute("SELECT doctor_id, name, specialization, experience FROM doctors")
        records = cur.fetchall()
        view_text.delete(1.0, tk.END)
        for r in records:
            view_text.insert(tk.END, f"🩺 ID: {r[0]} | Dr. {r[1]} ({r[2]}) | Exp: {r[3]} yrs\n")
        conn.close()

# ------------------ BOOK APPOINTMENT (1 slot per doctor) ------------------
def book_appointment():
    conn = connect_db()
    if conn:
        cur = conn.cursor()

        patient_name = a_patient.get().strip()
        doctor_name  = a_doctor.get().strip()
        slot         = a_slot.get().strip()

        # ---- GET PATIENT ID ----
        cur.execute("SELECT patient_id FROM patients WHERE name=%s", (patient_name,))
        pid = cur.fetchone()

        # ---- GET DOCTOR ID ----
        cur.execute("SELECT doctor_id FROM doctors WHERE name=%s", (doctor_name,))
        did = cur.fetchone()

        if not pid or not did:
            messagebox.showerror("Error", "❌ Select valid patient and doctor!")
            return

        # ---- CHECK IF DOCTOR ALREADY BOOKED IN SAME SLOT ----
        cur.execute("""
            SELECT appointment_id FROM appointments
            WHERE doctor_id=%s AND slot=%s
        """, (did[0], slot))

        exists = cur.fetchone()

        if exists:
            messagebox.showerror(
                "Slot Taken",
                f"❌ Dr. {doctor_name} is already booked at {slot}.\nChoose another time slot."
            )
            return

        # ---- INSERT APPOINTMENT ----
        try:
            cur.execute("""
                INSERT INTO appointments (patient_id, doctor_id, department, slot, fee)
                VALUES (%s,%s,%s,%s,%s)
            """, (
                pid[0], did[0], a_dept.get(), slot, a_fee.get()
            ))
            conn.commit()

            messagebox.showinfo(
                "Success",
                f"✅ Appointment booked for {patient_name} with Dr. {doctor_name} at {slot}"
            )

        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Failed to book appointment: {err}")

        finally:
            conn.close()

# ------------------ VIEW APPOINTMENTS ------------------
def view_appointments():
    conn = connect_db()
    if conn:
        cur = conn.cursor()
        cur.execute("""
            SELECT a.appointment_id, p.name, d.name, a.department, a.slot, a.fee 
            FROM appointments a
            JOIN patients p ON a.patient_id = p.patient_id
            JOIN doctors d ON a.doctor_id = d.doctor_id
        """)
        records = cur.fetchall()

        view_text.delete(1.0, tk.END)
        for r in records:
            view_text.insert(
                tk.END,
                f"📅 Appt ID: {r[0]} | 👤 {r[1]} | 👨‍⚕ {r[2]} | {r[3]} | {r[4]} | 💰 ₹{r[5]}\n"
            )
        conn.close()

# ------------------ GUI ------------------
root = tk.Tk()
root.title("🏥 Hospital Management System")
root.geometry("900x650")
root.config(bg="#e8f1f8")

style = ttk.Style()
style.theme_use("clam")

style.configure("TNotebook", background="#d1e7f0")
style.configure("TNotebook.Tab", background="#a8d8ea", padding=10, font=("Arial", 11, "bold"))
style.map("TNotebook.Tab", background=[("selected", "#5aa9e6")])

tabControl = ttk.Notebook(root)
tab1 = ttk.Frame(tabControl)
tab2 = ttk.Frame(tabControl)
tab3 = ttk.Frame(tabControl)
tab4 = ttk.Frame(tabControl)

tabControl.add(tab1, text='➕ Add Patient')
tabControl.add(tab2, text='👨‍⚕ Add Doctor')
tabControl.add(tab3, text='📅 Book Appointment')
tabControl.add(tab4, text='📖 View Records')
tabControl.pack(expand=1, fill="both", padx=10, pady=10)

tabControl.bind("<<NotebookTabChanged>>", lambda e: refresh_comboboxes())

# ------------ ADD PATIENT UI ------------
fields = [
    ("Patient Name", "p_name"),
    ("Age", "p_age"),
    ("Gender", "p_gender"),
    ("Phone", "p_phone"),
    ("Location", "p_loc"),
    ("Guardian Name", "p_guardian"),
    ("Guardian Phone", "p_guardian_phone")
]

for i, (label, var) in enumerate(fields):
    ttk.Label(tab1, text=label).grid(row=i, column=0, padx=10, pady=6)
    globals()[var] = ttk.Entry(tab1, width=30)
    globals()[var].grid(row=i, column=1, padx=10, pady=6)

ttk.Button(tab1, text="Add Patient", command=add_patient).grid(
    row=len(fields), column=0, columnspan=2, pady=15
)

# ------------ ADD DOCTOR UI ------------
doctor_fields = [
    ("Doctor Name", "d_name"),
    ("Specialization", "d_spec"),
    ("Experience (yrs)", "d_exp"),
    ("Phone", "d_phone"),
    ("Email", "d_email")
]

for i, (label, var) in enumerate(doctor_fields):
    ttk.Label(tab2, text=label).grid(row=i, column=0, padx=10, pady=6)
    globals()[var] = ttk.Entry(tab2, width=30)
    globals()[var].grid(row=i, column=1, padx=10, pady=6)

ttk.Button(tab2, text="Add Doctor", command=add_doctor).grid(
    row=len(doctor_fields), column=0, columnspan=2, pady=15
)

# ------------ BOOK APPOINTMENT UI ------------
ttk.Label(tab3, text="Patient Name").grid(row=0, column=0, padx=10, pady=6)
a_patient = ttk.Combobox(tab3, width=28, state="readonly")
a_patient.grid(row=0, column=1)

ttk.Label(tab3, text="Doctor Name").grid(row=1, column=0, padx=10, pady=6)
a_doctor = ttk.Combobox(tab3, width=28, state="readonly")
a_doctor.grid(row=1, column=1)

ttk.Label(tab3, text="Department").grid(row=2, column=0, padx=10, pady=6)
a_dept = ttk.Combobox(tab3, values=["General Medicine", "Cardiology", "Dental", "Ortho", "ENT"],
                      width=28, state="readonly")
a_dept.grid(row=2, column=1)
a_dept.set("General Medicine")

ttk.Label(tab3, text="Time Slot").grid(row=3, column=0, padx=10, pady=6)
a_slot = ttk.Combobox(
    tab3,
    values=["09:00-10:00", "10:00-11:00", "11:00-12:00", "04:00-05:00"],
    width=28,
    state="readonly"
)
a_slot.grid(row=3, column=1)
a_slot.set("09:00-10:00")

ttk.Label(tab3, text="Fee (₹)").grid(row=4, column=0, padx=10, pady=6)
a_fee = ttk.Entry(tab3, width=30)
a_fee.grid(row=4, column=1)
a_fee.insert(0, "500")

ttk.Button(tab3, text="Book Appointment", command=book_appointment).grid(
    row=5, column=0, columnspan=2, pady=15
)

# ------------ VIEW RECORDS UI ------------
frame_view = tk.Frame(tab4, bg="#e8f1f8")
frame_view.pack(pady=10)

ttk.Button(frame_view, text="View Patients", command=view_patients).grid(row=0, column=0, padx=5)
ttk.Button(frame_view, text="View Doctors", command=view_doctors).grid(row=0, column=1, padx=5)
ttk.Button(frame_view, text="View Appointments", command=view_appointments).grid(row=0, column=2, padx=5)

view_text = tk.Text(tab4, height=25, width=95, bg="#f0f9ff",
                    fg="#003049", font=("Consolas", 10))
view_text.pack(pady=15)

root.mainloop()