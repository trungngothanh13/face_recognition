# face_recognition_app_refactored.py
"""
Main entry point for Face Recognition Desktop Application
Now simplified and organized with separated components
"""
import tkinter as tk
import sys
import os

# Add project directory to path
project_dir = os.path.abspath('.')
if project_dir not in sys.path:
    sys.path.append(project_dir)

# Import main window
from src.ui.main_window import MainWindow
from src.database.database_manager import close_database_manager

# Check for face_recognition availability
try:
    import face_recognition
    FACE_RECOGNITION_AVAILABLE = True
    print("✅ face_recognition library available - using advanced recognition")
except ImportError:
    FACE_RECOGNITION_AVAILABLE = False
    print("⚠️ face_recognition library not available - using OpenCV detection only")

def main():
    """Main application entry point"""
    print("🚀 Starting Face Recognition Desktop Application...")
    print("📋 Features:")
    print(f"   - Face Recognition: {'✅ Available' if FACE_RECOGNITION_AVAILABLE else '❌ Detection Only'}")
    print("   - Larger camera display (800x600)")
    print("   - Automatic attendance recording")
    print("   - Motion detection + face recognition")
    print("   - Employee management")
    print("   - Manual attendance option")
    print("   - Modular architecture with separated components")
    
    if FACE_RECOGNITION_AVAILABLE:
        print("\n🎯 This version will automatically recognize faces and record attendance!")
    else:
        print("\n⚠️ face_recognition library not available - using detection mode only")
        print("   Install face_recognition for automatic recognition: pip install face-recognition")
    
    # Create main window
    root = tk.Tk()
    
    try:
        # Initialize main application
        app = MainWindow(root)
        
        # Handle window closing
        def on_closing():
            app.on_closing()
            close_database_manager()
        
        root.protocol("WM_DELETE_WINDOW", on_closing)
        
        # Start the application
        print("\n✅ Application initialized successfully!")
        print("🎮 GUI Controls:")
        print("   - Start Recognition: Begin face detection/recognition")
        print("   - Stop Recognition: Stop camera processing")
        print("   - Manual Attendance: Record attendance manually")
        print("   - Add Employee: Add new employee to system")
        print("   - Enroll Face: Capture face samples for employee")
        print("   - Link Face: Connect existing face data to employee")
        
        root.mainloop()
        
    except Exception as e:
        print(f"❌ Application error: {e}")
        close_database_manager()
        raise
    
    finally:
        # Ensure cleanup
        close_database_manager()
        print("👋 Application closed")

if __name__ == "__main__":
    main()