# src/ui/dialogs.py
"""
Dialog windows for Face Recognition System
Handles employee addition, face enrollment, and other modal interactions
"""
import tkinter as tk
from tkinter import ttk, messagebox
import threading

class EmployeeDialog:
    """Dialog for adding new employees"""
    
    def __init__(self, parent, emp_db):
        self.emp_db = emp_db
        self.result = None
        
        # Create dialog window
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Add New Employee")
        self.dialog.geometry("400x300")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Center the dialog
        self.dialog.geometry("+%d+%d" % (parent.winfo_rootx() + 50, parent.winfo_rooty() + 50))
        
        self.create_widgets()
    
    def create_widgets(self):
        """Create dialog widgets"""
        main_frame = ttk.Frame(self.dialog)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Name
        ttk.Label(main_frame, text="Name *:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.name_entry = ttk.Entry(main_frame, width=30)
        self.name_entry.grid(row=0, column=1, pady=5, padx=(10, 0))
        
        # Phone
        ttk.Label(main_frame, text="Phone:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.phone_entry = ttk.Entry(main_frame, width=30)
        self.phone_entry.grid(row=1, column=1, pady=5, padx=(10, 0))
        
        # Department
        ttk.Label(main_frame, text="Department:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.dept_entry = ttk.Entry(main_frame, width=30)
        self.dept_entry.grid(row=2, column=1, pady=5, padx=(10, 0))
        
        # Position
        ttk.Label(main_frame, text="Position:").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.pos_entry = ttk.Entry(main_frame, width=30)
        self.pos_entry.grid(row=3, column=1, pady=5, padx=(10, 0))
        
        # Work start time
        ttk.Label(main_frame, text="Work Start Time:").grid(row=4, column=0, sticky=tk.W, pady=5)
        self.time_entry = ttk.Entry(main_frame, width=30)
        self.time_entry.insert(0, "09:00")
        self.time_entry.grid(row=4, column=1, pady=5, padx=(10, 0))
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=5, column=0, columnspan=2, pady=20)
        
        ttk.Button(button_frame, text="Add Employee", command=self.add_employee).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=self.cancel).pack(side=tk.LEFT, padx=5)
        
        # Focus on name entry
        self.name_entry.focus()
    
    def add_employee(self):
        """Add the employee"""
        name = self.name_entry.get().strip()
        if not name:
            messagebox.showerror("Error", "Name is required!")
            return
        
        try:
            employee_id = self.emp_db.add_employee(
                name=name,
                phone=self.phone_entry.get().strip() or None,
                department=self.dept_entry.get().strip() or None,
                position=self.pos_entry.get().strip() or None,
                work_start_time=self.time_entry.get().strip() or "09:00"
            )
            
            self.result = employee_id
            self.dialog.destroy()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to add employee: {e}")
    
    def cancel(self):
        """Cancel dialog"""
        self.dialog.destroy()

def show_manual_attendance_dialog(parent, emp_db, refresh_callback):
    """Show manual attendance recording dialog"""
    employees = emp_db.list_employees()
    if not employees:
        messagebox.showwarning("Warning", "No employees found. Add employees first.")
        return
    
    # Create selection dialog
    dialog = tk.Toplevel(parent)
    dialog.title("Manual Attendance")
    dialog.geometry("350x450")
    dialog.transient(parent)
    dialog.grab_set()
    
    ttk.Label(dialog, text="Select Employee for Attendance:").pack(pady=10)
    
    # Employee listbox
    emp_listbox = tk.Listbox(dialog, height=15)
    emp_listbox.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    
    for emp in employees:
        emp_listbox.insert(tk.END, f"{emp['name']} ({emp['employee_id']})")
    
    def record_selected():
        selection = emp_listbox.curselection()
        if not selection:
            messagebox.showwarning("Warning", "Please select an employee.")
            return
        
        selected_emp = employees[selection[0]]
        try:
            emp_db.record_attendance(selected_emp['employee_id'])
            messagebox.showinfo("Success", f"Attendance recorded for {selected_emp['name']}")
            dialog.destroy()
            refresh_callback()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to record attendance: {e}")
    
    ttk.Button(dialog, text="Record Attendance", command=record_selected).pack(pady=10)
    ttk.Button(dialog, text="Cancel", command=dialog.destroy).pack()

def show_face_enrollment_dialog(parent, employee, face_db, reload_callback):
    """Show face enrollment dialog and process"""
    messagebox.showinfo("Face Enrollment", 
                       f"Starting face enrollment for {employee['name']}.\n\n"
                       "Instructions:\n"
                       "- Look directly at the camera\n"
                       "- Keep your face well-lit\n"
                       "- Move slightly between samples\n"
                       "- Press 'q' to quit early\n\n"
                       "The enrollment window will open shortly...")
    
    # Run enrollment in separate thread
    threading.Thread(
        target=run_face_enrollment_thread, 
        args=(parent, employee, face_db, reload_callback), 
        daemon=True
    ).start()

def run_face_enrollment_thread(parent, employee, face_db, reload_callback):
    """Run face enrollment in separate thread"""
    try:
        # Import enrollment class
        from ..processing.face_enrollment import FaceEnrollment
        from ..processing.video_stream import VideoStream
        
        # Create enrollment instance
        enrollment = FaceEnrollment(face_db, VideoStream)
        
        # Run enrollment (captures 5 samples)
        success = enrollment.enroll_person(employee['name'], num_samples=5)
        
        if success:
            # Link face to employee
            from ..database.employee_database import EmployeeDatabase
            emp_db = EmployeeDatabase()
            linked_count = emp_db.link_face_to_employee(employee['employee_id'], employee['name'])
            emp_db.close()
            
            # Update UI in main thread
            parent.after(0, lambda: messagebox.showinfo("Success", 
                f"Face enrollment completed for {employee['name']}!\n"
                f"Linked {linked_count} face samples.\n"
                f"Employee can now be automatically recognized."))
            parent.after(0, reload_callback)
            
            print(f"✅ Face enrollment completed for {employee['name']}")
            
        else:
            parent.after(0, lambda: messagebox.showerror("Error", 
                f"Face enrollment failed for {employee['name']}.\n"
                "Please try again with better lighting."))
    
    except Exception as e:
        print(f"Face enrollment error: {e}")
        parent.after(0, lambda: messagebox.showerror("Error", 
            f"Face enrollment error: {e}"))

def show_face_link_dialog(parent, emp_db, face_db, reload_callback):
    """Show dialog to manually link existing face to employee"""
    employees = emp_db.list_employees()
    if not employees:
        messagebox.showwarning("Warning", "No employees found.")
        return
    
    # Get available face names
    all_faces = face_db.get_all_faces()
    face_names = list(set([face[0] for face in all_faces]))
    
    if not face_names:
        messagebox.showwarning("Warning", "No face data found.")
        return
    
    # Create linking dialog
    dialog = tk.Toplevel(parent)
    dialog.title("Link Face to Employee")
    dialog.geometry("450x350")
    dialog.transient(parent)
    dialog.grab_set()
    
    ttk.Label(dialog, text="Select Employee:").pack(pady=5)
    emp_var = tk.StringVar()
    emp_combo = ttk.Combobox(dialog, textvariable=emp_var, state="readonly", width=50)
    emp_combo['values'] = [f"{emp['name']} ({emp['employee_id']})" for emp in employees]
    emp_combo.pack(fill=tk.X, padx=10, pady=5)
    
    ttk.Label(dialog, text="Select Face Name:").pack(pady=5)
    face_var = tk.StringVar()
    face_combo = ttk.Combobox(dialog, textvariable=face_var, state="readonly", width=50)
    face_combo['values'] = face_names
    face_combo.pack(fill=tk.X, padx=10, pady=5)
    
    def link_face():
        if not emp_var.get() or not face_var.get():
            messagebox.showwarning("Warning", "Please select both employee and face.")
            return
        
        emp_index = emp_combo.current()
        selected_emp = employees[emp_index]
        selected_face = face_var.get()
        
        try:
            linked_count = emp_db.link_face_to_employee(selected_emp['employee_id'], selected_face)
            messagebox.showinfo("Success", 
                f"Linked {linked_count} face samples: {selected_face} → {selected_emp['name']}")
            dialog.destroy()
            reload_callback()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to link face: {e}")
    
    ttk.Button(dialog, text="Link Face", command=link_face).pack(pady=20)
    ttk.Button(dialog, text="Cancel", command=dialog.destroy).pack()