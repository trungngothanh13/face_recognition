# src/ui/main_window.py
"""
Main application window for Face Recognition System
Coordinates between video panel, info tabs, and system components
"""
import tkinter as tk
from tkinter import ttk, messagebox
import threading
import time
from datetime import datetime

from .video_panel import VideoPanel
from .info_tabs import InfoTabs
from .dialogs import EmployeeDialog, show_face_enrollment_dialog
from ..database.employee_database import EmployeeDatabase
from ..database.face_database import FaceDatabase
from ..processing.face_processor import ImprovedFaceProcessor

class MainWindow:
    """Main application window"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("Face Recognition Attendance System")
        self.root.geometry("1400x800")
        
        # Initialize databases
        self.emp_db = EmployeeDatabase()
        self.face_db = FaceDatabase()
        
        # Initialize face processor
        self.face_processor = ImprovedFaceProcessor()
        
        # Load recognition data
        self.known_encodings = []
        self.known_names = []
        self.employee_map = {}
        self.last_recognition_time = {}
        
        # System state
        self.is_running = False
        self.video_thread = None
        
        # Load known faces
        self.load_known_faces()
        
        # Create UI components
        self.create_layout()
        
        # Start status updates
        self.update_status()
    
    def create_layout(self):
        """Create the main application layout"""
        # Create main paned window
        main_paned = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        main_paned.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Left side - Video panel
        self.video_panel = VideoPanel(main_paned, self)
        main_paned.add(self.video_panel.frame, weight=2)
        
        # Right side - Info tabs
        self.info_tabs = InfoTabs(main_paned, self)
        main_paned.add(self.info_tabs.notebook, weight=1)
        
        # Status bar
        self.status_bar = tk.Label(self.root, text="Ready", relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Load initial data
        self.refresh_all_data()
    
    def load_known_faces(self):
        """Load known face encodings and create employee mapping"""
        try:
            if not self.face_processor.use_face_recognition:
                print("⚠️ face_recognition not available - automatic recognition disabled")
                return
            
            all_faces = self.face_db.get_all_faces()
            self.known_names = [face[0] for face in all_faces]
            self.known_encodings = [face[1] for face in all_faces]
            
            # Create mapping from face names to employee IDs
            self.employee_map = {}
            for face_name in set(self.known_names):
                employee = self.emp_db.find_employee_by_face_name(face_name)
                if employee:
                    self.employee_map[face_name] = employee['employee_id']
            
            print(f"✅ Loaded {len(self.known_encodings)} face encodings")
            print(f"✅ Mapped {len(self.employee_map)} faces to employees")
            
        except Exception as e:
            print(f"❌ Error loading faces: {e}")
            self.known_encodings = []
            self.known_names = []
            self.employee_map = {}
    
    def start_recognition(self):
        """Start the face recognition system"""
        if self.is_running:
            return
        
        try:
            # Initialize video processing
            self.video_panel.start_video_processing()
            
            # Update state
            self.is_running = True
            
            # Start video thread
            self.video_thread = threading.Thread(target=self.video_processing_loop, daemon=True)
            self.video_thread.start()
            
            # Update status
            mode = "Recognition" if self.face_processor.use_face_recognition and self.known_encodings else "Detection"
            self.update_status_bar(f"Face {mode} started")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to start recognition: {e}")
            self.is_running = False
    
    def stop_recognition(self):
        """Stop the face recognition system"""
        self.is_running = False
        
        # Stop video processing
        self.video_panel.stop_video_processing()
        
        # Update status
        self.update_status_bar("Face recognition stopped")
    
    def video_processing_loop(self):
        """Main video processing loop"""
        while self.is_running:
            try:
                # Let video panel handle the actual processing
                # This allows the video panel to manage its own video stream
                recognition_results = self.video_panel.process_frame(
                    self.known_encodings, 
                    self.known_names, 
                    self.face_processor
                )
                
                # Process any recognition results
                if recognition_results:
                    for name, confidence, location in recognition_results:
                        if name != "Unknown" and confidence > 0.6:
                            if self.should_record_attendance(name):
                                self.process_recognition(name, confidence)
                
                time.sleep(0.03)  # ~30 FPS
                
            except Exception as e:
                print(f"Video processing error: {e}")
                break
    
    def should_record_attendance(self, name):
        """Check if we should record attendance (avoid spam)"""
        current_time = time.time()
        if name in self.last_recognition_time:
            return current_time - self.last_recognition_time[name] > 30
        return True
    
    def process_recognition(self, face_name, confidence):
        """Process a successful face recognition"""
        try:
            if face_name in self.employee_map:
                employee_id = self.employee_map[face_name]
                
                # Record attendance
                self.emp_db.record_attendance(employee_id)
                
                # Update last recognition time
                self.last_recognition_time[face_name] = time.time()
                
                # Update displays
                self.root.after(0, self.refresh_attendance)
                
                # Show success message
                success_msg = f"✅ Attendance recorded for {face_name}"
                self.video_panel.show_recognition_status(success_msg, "green")
                
                print(f"✅ Attendance recorded for {face_name} (confidence: {confidence:.2f})")
            
        except Exception as e:
            print(f"Error processing recognition: {e}")
            self.video_panel.show_recognition_status("❌ Attendance error", "red")
    
    def add_employee(self):
        """Add a new employee"""
        dialog = EmployeeDialog(self.root, self.emp_db)
        if dialog.result:
            self.refresh_employees()
            messagebox.showinfo("Success", f"Employee {dialog.result} added successfully!")
    
    def enroll_face(self):
        """Enroll face for selected employee"""
        selected_employee = self.info_tabs.get_selected_employee()
        if not selected_employee:
            messagebox.showwarning("Warning", "Please select an employee first.")
            return
        
        if not self.face_processor.use_face_recognition:
            messagebox.showerror("Error", "Face enrollment requires face_recognition library.")
            return
        
        # Show enrollment dialog
        show_face_enrollment_dialog(self.root, selected_employee, self.face_db, self.reload_faces_callback)
    
    def reload_faces_callback(self):
        """Callback after face enrollment"""
        self.load_known_faces()
        self.refresh_employees()
    
    def manual_attendance(self):
        """Manual attendance recording"""
        from .dialogs import show_manual_attendance_dialog
        show_manual_attendance_dialog(self.root, self.emp_db, self.refresh_attendance)
    
    def refresh_all_data(self):
        """Refresh all data displays"""
        self.refresh_employees()
        self.refresh_attendance()
    
    def refresh_employees(self):
        """Refresh employee list"""
        self.info_tabs.refresh_employees()
    
    def refresh_attendance(self):
        """Refresh attendance list"""
        self.info_tabs.refresh_attendance()
    
    def update_status(self):
        """Update system status information"""
        try:
            # Get database stats
            employee_count = self.emp_db.employees_collection.count_documents({"is_active": True})
            face_count = self.face_db.faces_collection.count_documents({})
            event_count = self.face_db.events_collection.count_documents({})
            
            # Update info tabs
            self.info_tabs.update_system_info({
                'employee_count': employee_count,
                'face_count': face_count,
                'known_faces': len(self.known_encodings),
                'event_count': event_count,
                'is_running': self.is_running,
                'face_recognition_available': self.face_processor.use_face_recognition
            })
            
            # Update attendance
            self.refresh_attendance()
            
        except Exception as e:
            print(f"Error updating status: {e}")
        
        # Schedule next update
        self.root.after(5000, self.update_status)
    
    def update_status_bar(self, message):
        """Update the status bar"""
        timestamp = datetime.now().strftime('%H:%M:%S')
        self.status_bar.config(text=f"{timestamp} - {message}")
    
    def on_closing(self):
        """Handle application closing"""
        if self.is_running:
            self.stop_recognition()
        
        # Close database connections
        self.emp_db.close()
        self.face_db.close()
        
        self.root.destroy()