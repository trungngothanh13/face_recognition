# src/ui/info_tabs.py
"""
Information tabs for Face Recognition System
Displays system status, attendance, and employee information
"""
import tkinter as tk
from tkinter import ttk
from datetime import datetime

class InfoTabs:
    """Information display tabs"""
    
    def __init__(self, parent, main_window):
        self.parent = parent
        self.main_window = main_window
        
        # Create notebook
        self.notebook = ttk.Notebook(parent)
        
        # Create tabs
        self.create_system_info_tab()
        self.create_attendance_tab()
        self.create_employee_tab()
    
    def create_system_info_tab(self):
        """Create system information tab"""
        info_frame = ttk.Frame(self.notebook)
        self.notebook.add(info_frame, text="System Info")
        
        self.stats_text = tk.Text(info_frame, width=40, height=15, wrap=tk.WORD)
        self.stats_text.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
    
    def create_attendance_tab(self):
        """Create attendance tab"""
        attendance_frame = ttk.Frame(self.notebook)
        self.notebook.add(attendance_frame, text="Today's Attendance")
        
        self.attendance_listbox = tk.Listbox(attendance_frame)
        self.attendance_listbox.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        ttk.Button(
            attendance_frame, 
            text="Refresh Attendance", 
            command=self.refresh_attendance
        ).pack(pady=5)
    
    def create_employee_tab(self):
        """Create employee management tab"""
        emp_frame = ttk.Frame(self.notebook)
        self.notebook.add(emp_frame, text="Employees")
        
        self.employee_listbox = tk.Listbox(emp_frame)
        self.employee_listbox.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Employee management buttons
        emp_buttons = ttk.Frame(emp_frame)
        emp_buttons.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Button(emp_buttons, text="Add Employee", 
                  command=self.main_window.add_employee).pack(side=tk.LEFT, padx=2)
        ttk.Button(emp_buttons, text="Enroll Face", 
                  command=self.main_window.enroll_face).pack(side=tk.LEFT, padx=2)
        ttk.Button(emp_buttons, text="Link Face", 
                  command=self.manual_face_link).pack(side=tk.LEFT, padx=2)
        ttk.Button(emp_buttons, text="Refresh", 
                  command=self.refresh_employees).pack(side=tk.LEFT, padx=2)
    
    def update_system_info(self, stats):
        """Update system information display"""
        mode = "AUTOMATIC RECOGNITION" if stats['face_recognition_available'] and stats['known_faces'] > 0 else "DETECTION ONLY"
        
        status_text = f"""System Status:

Mode: {mode}
Active Employees: {stats['employee_count']}
Face Samples: {stats['face_count']}
Known Faces: {stats['known_faces']}
Recognition Events: {stats['event_count']}
Status: {'Running' if stats['is_running'] else 'Stopped'}

face_recognition library: {'✅ Available' if stats['face_recognition_available'] else '❌ Not Available'}

Last Updated: {datetime.now().strftime('%H:%M:%S')}
"""
        
        self.stats_text.delete(1.0, tk.END)
        self.stats_text.insert(1.0, status_text)
    
    def refresh_employees(self):
        """Refresh the employee list"""
        self.employee_listbox.delete(0, tk.END)
        
        try:
            employees = self.main_window.emp_db.list_employees()
            
            if not employees:
                self.employee_listbox.insert(tk.END, "No employees found - Add employees first")
                return
            
            for emp in employees:
                face_count = self.main_window.face_db.faces_collection.count_documents(
                    {"employee_id": emp['employee_id']}
                )
                face_status = "✅" if face_count > 0 else "❌"
                display_text = f"{emp['name']} {face_status}"
                self.employee_listbox.insert(tk.END, display_text)
                
        except Exception as e:
            print(f"Error refreshing employees: {e}")
            self.employee_listbox.insert(tk.END, f"Error loading employees: {e}")
    
    def refresh_attendance(self):
        """Refresh today's attendance list"""
        self.attendance_listbox.delete(0, tk.END)
        
        try:
            today_attendance = self.main_window.emp_db.get_today_attendance()
            
            if not today_attendance:
                self.attendance_listbox.insert(tk.END, "No attendance records for today")
                return
            
            for att in today_attendance:
                status = "LATE" if att['is_late'] else "ON TIME"
                time_str = att['enter_time'].strftime('%H:%M:%S')
                display_text = f"{att['employee_name']} - {time_str} ({status})"
                self.attendance_listbox.insert(tk.END, display_text)
                
        except Exception as e:
            print(f"Error refreshing attendance: {e}")
            self.attendance_listbox.insert(tk.END, f"Error loading attendance: {e}")
    
    def get_selected_employee(self):
        """Get currently selected employee"""
        selection = self.employee_listbox.curselection()
        if not selection:
            return None
        
        # Get employee name from selection (remove status emoji)
        employee_line = self.employee_listbox.get(selection[0])
        if "No employees found" in employee_line or "Error" in employee_line:
            return None
        
        employee_name = employee_line.split(" ✅")[0].split(" ❌")[0]
        return self.main_window.emp_db.get_employee_by_name(employee_name)
    
    def manual_face_link(self):
        """Manually link existing face to employee"""
        from .dialogs import show_face_link_dialog
        show_face_link_dialog(
            self.main_window.root, 
            self.main_window.emp_db, 
            self.main_window.face_db,
            self.main_window.reload_faces_callback
        )