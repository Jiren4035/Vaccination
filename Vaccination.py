import tkinter as tk
from tkinter import messagebox
from datetime import datetime, timedelta
import os

# -------------------- Constants --------------------
VACCINES = {
    "AF": {"doses": 2, "interval": 14, "min_age": 12},
    "BV": {"doses": 2, "interval": 21, "min_age": 18},
    "CZ": {"doses": 2, "interval": 21, "min_age": 12, "max_age": 45},
    "DM": {"doses": 2, "interval": 28, "min_age": 12},
    "EC": {"doses": 1, "interval": 0, "min_age": 18}
}

PATIENTS_FILE = "patients.txt"
VACCINATIONS_FILE = "vaccinations.txt"

# -------------------- Utility Functions --------------------
def load_patients():
    if not os.path.exists(PATIENTS_FILE):
        return []
    with open(PATIENTS_FILE, "r") as f:
        return [line.strip().split(",") for line in f]

def load_vaccinations():
    if not os.path.exists(VACCINATIONS_FILE):
        return []
    with open(VACCINATIONS_FILE, "r") as f:
        return [line.strip().split(",") for line in f]

def get_new_patient_id():
    patients = load_patients()
    return f"P{len(patients) + 1:04d}"

def save_patient(patient_data):
    with open(PATIENTS_FILE, "a") as f:
        f.write(",".join(patient_data) + "\n")

def save_vaccination(vaccine_data):
    with open(VACCINATIONS_FILE, "a") as f:
        f.write(",".join(vaccine_data) + "\n")

def get_patient_by_id(pid):
    for patient in load_patients():
        if patient[0] == pid:
            return patient
    return None

def get_last_dose(pid):
    doses = [v for v in load_vaccinations() if v[0] == pid]
    return sorted(doses, key=lambda x: x[2])[-1] if doses else None

# -------------------- GUI Functions --------------------
def register_patient():
    def submit():
        name = entry_name.get().strip()
        age = int(entry_age.get().strip())
        contact = entry_contact.get().strip()
        vc = vc_var.get()
        vaccine = vaccine_var.get()

        if vaccine not in VACCINES:
            messagebox.showerror("Error", "Invalid vaccine selected.")
            return
        vac_info = VACCINES[vaccine]
        if age < vac_info["min_age"] or ("max_age" in vac_info and age > vac_info["max_age"]):
            messagebox.showerror("Error", "Patient is not eligible for this vaccine.")
            return

        pid = get_new_patient_id()
        save_patient([pid, name, str(age), contact, vc, vaccine])
        messagebox.showinfo("Success", f"Patient registered with ID: {pid}")
        top.destroy()

    top = tk.Toplevel(root)
    top.title("Register Patient")

    tk.Label(top, text="Name").grid(row=0, column=0)
    entry_name = tk.Entry(top)
    entry_name.grid(row=0, column=1)

    tk.Label(top, text="Age").grid(row=1, column=0)
    entry_age = tk.Entry(top)
    entry_age.grid(row=1, column=1)

    tk.Label(top, text="Contact").grid(row=2, column=0)
    entry_contact = tk.Entry(top)
    entry_contact.grid(row=2, column=1)

    tk.Label(top, text="Vaccination Centre").grid(row=3, column=0)
    vc_var = tk.StringVar(value="VC1")
    tk.OptionMenu(top, vc_var, "VC1", "VC2").grid(row=3, column=1)

    tk.Label(top, text="Vaccine").grid(row=4, column=0)
    vaccine_var = tk.StringVar(value="AF")
    tk.OptionMenu(top, vaccine_var, *VACCINES.keys()).grid(row=4, column=1)

    tk.Button(top, text="Register", command=submit).grid(row=5, columnspan=2)

def administer_dose():
    def submit():
        pid = entry_pid.get().strip()
        dose_type = dose_var.get()
        date_str = entry_date.get().strip()

        try:
            date = datetime.strptime(date_str, "%Y-%m-%d")
        except:
            messagebox.showerror("Error", "Invalid date format. Use YYYY-MM-DD")
            return

        patient = get_patient_by_id(pid)
        if not patient:
            messagebox.showerror("Error", "Patient ID not found.")
            return

        vaccine = patient[5]
        vac_info = VACCINES[vaccine]

        last_dose = get_last_dose(pid)
        if last_dose:
            last_dose_date = datetime.strptime(last_dose[2], "%Y-%m-%d")
            days_diff = (date - last_dose_date).days
            if dose_type == "D2" and days_diff < vac_info["interval"]:
                messagebox.showerror("Error", f"Too early for second dose. Wait {vac_info['interval']} days.")
                return
            if dose_type == "D1":
                messagebox.showerror("Error", "Dose 1 already administered.")
                return
        elif dose_type == "D2":
            messagebox.showerror("Error", "No Dose 1 found. Administer Dose 1 first.")
            return

        save_vaccination([pid, vaccine, date_str, dose_type])
        messagebox.showinfo("Success", f"{dose_type} recorded for {pid}.")
        top.destroy()

    top = tk.Toplevel(root)
    top.title("Administer Dose")

    tk.Label(top, text="Patient ID").grid(row=0, column=0)
    entry_pid = tk.Entry(top)
    entry_pid.grid(row=0, column=1)

    tk.Label(top, text="Dose").grid(row=1, column=0)
    dose_var = tk.StringVar(value="D1")
    tk.OptionMenu(top, dose_var, "D1", "D2").grid(row=1, column=1)

    tk.Label(top, text="Date (YYYY-MM-DD)").grid(row=2, column=0)
    entry_date = tk.Entry(top)
    entry_date.grid(row=2, column=1)

    tk.Button(top, text="Administer", command=submit).grid(row=3, columnspan=2)

# -------------------- Main Window --------------------
root = tk.Tk()
root.title("Vaccination Scheduler")

tk.Label(root, text="COVID-19 Vaccination Record System", font=("Arial", 14)).pack(pady=10)

tk.Button(root, text="Register New Patient", command=register_patient, width=30).pack(pady=5)
tk.Button(root, text="Administer Vaccine Dose", command=administer_dose, width=30).pack(pady=5)
tk.Button(root, text="Exit", command=root.destroy, width=30).pack(pady=5)

root.mainloop()
