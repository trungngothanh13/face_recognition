# src/database/employee_database.py
"""
Employee database operations
Handles employee CRUD operations and attendance tracking
"""
import pymongo
from datetime import datetime, time
import uuid

from .database_manager import get_database_manager

class EmployeeDatabase:
    """Employee database operations"""
    
    def __init__(self):
        self.db_manager = get_database_manager()
        
        # Get collections
        self.employees_collection = self.db_manager.get_collection("employees")
        self.attendance_collection = self.db_manager.get_collection("attendance")
        self.faces_collection = self.db_manager.get_collection("faces")  # For linking
        
        # Create indexes
        self._create_indexes()
    
    def _create_indexes(self):
        """Create database indexes"""
        employee_indexes = [
            {"keys": "employee_id", "unique": True},
            {"keys": "phone", "unique": True, "sparse": True},
            {"keys": "name"}
        ]
        
        attendance_indexes = [
            {"keys": [("employee_id", 1), ("date", 1)], "unique": True},
            {"keys": "date"},
            {"keys": "enter_time"}
        ]
        
        face_indexes = [
            {"keys": "employee_id", "sparse": True}
        ]
        
        self.db_manager.create_indexes("employees", employee_indexes)
        self.db_manager.create_indexes("attendance", attendance_indexes)
        self.db_manager.create_indexes("faces", face_indexes)
    
    def add_employee(self, name, phone=None, department=None, position=None, work_start_time="09:00"):
        """Add a new employee"""
        employee_id = f"EMP{str(uuid.uuid4())[:8].upper()}"
        
        employee_doc = {
            "employee_id": employee_id,
            "name": name,
            "phone": phone,
            "department": department,
            "position": position,
            "work_start_time": work_start_time,
            "created_at": datetime.now(),
            "is_active": True,
            "face_enrolled": False
        }
        
        try:
            self.employees_collection.insert_one(employee_doc)
            print(f"✅ Employee added: {name} (ID: {employee_id})")
            return employee_id
        except pymongo.errors.DuplicateKeyError as e:
            if "phone" in str(e):
                raise ValueError(f"Phone number {phone} already exists")
            else:
                raise ValueError(f"Employee ID {employee_id} already exists")
    
    def get_employee(self, employee_id):
        """Get employee by ID"""
        return self.employees_collection.find_one({"employee_id": employee_id})
    
    def get_employee_by_name(self, name):
        """Get employee by name (case insensitive)"""
        return self.employees_collection.find_one({"name": {"$regex": f"^{name}$", "$options": "i"}})
    
    def list_employees(self, active_only=True):
        """List all employees"""
        filter_query = {"is_active": True} if active_only else {}
        return list(self.employees_collection.find(filter_query).sort("name", 1))
    
    def link_face_to_employee(self, employee_id, face_name):
        """Link existing face samples to an employee"""
        employee = self.get_employee(employee_id)
        if not employee:
            raise ValueError(f"Employee {employee_id} not found")
        
        # Update face documents to include employee_id
        result = self.faces_collection.update_many(
            {"name": face_name},
            {"$set": {"employee_id": employee_id}}
        )
        
        # Mark employee as face enrolled
        if result.modified_count > 0:
            self.employees_collection.update_one(
                {"employee_id": employee_id},
                {"$set": {"face_enrolled": True}}
            )
        
        print(f"✅ Linked {result.modified_count} face samples to employee {employee_id}")
        return result.modified_count
    
    def record_attendance(self, employee_id, enter_time=None):
        """Record employee attendance"""
        if enter_time is None:
            enter_time = datetime.now()
        
        employee = self.get_employee(employee_id)
        if not employee:
            raise ValueError(f"Employee {employee_id} not found")
        
        # Get date for attendance record
        attendance_date = datetime.combine(enter_time.date(), datetime.min.time())
        
        # Check if attendance already exists for today
        existing = self.attendance_collection.find_one({
            "employee_id": employee_id,
            "date": attendance_date
        })
        
        if existing:
            print(f"⚠️ Attendance already recorded for {employee['name']} today")
            return existing["_id"]
        
        # Calculate if late
        work_start_str = employee.get("work_start_time", "09:00")
        work_start_hour, work_start_minute = map(int, work_start_str.split(":"))
        work_start_time = time(work_start_hour, work_start_minute)
        
        is_late = enter_time.time() > work_start_time
        
        # Create attendance record
        attendance_doc = {
            "employee_id": employee_id,
            "employee_name": employee["name"],
            "date": attendance_date,
            "enter_time": enter_time,
            "is_late": is_late,
            "is_present": True,
            "created_at": datetime.now()
        }
        
        result = self.attendance_collection.insert_one(attendance_doc)
        
        # Log the attendance
        status = "LATE" if is_late else "ON TIME"
        print(f"📋 Attendance recorded: {employee['name']} - {status} at {enter_time.strftime('%H:%M:%S')}")
        
        return result.inserted_id
    
    def get_today_attendance(self):
        """Get today's attendance records"""
        today = datetime.combine(datetime.now().date(), datetime.min.time())
        return list(self.attendance_collection.find({"date": today}).sort("enter_time", 1))
    
    def get_employee_attendance_history(self, employee_id, days=30):
        """Get attendance history for an employee"""
        from datetime import timedelta
        start_date = datetime.combine(
            (datetime.now().date() - timedelta(days=days)), 
            datetime.min.time()
        )
        
        return list(self.attendance_collection.find({
            "employee_id": employee_id,
            "date": {"$gte": start_date}
        }).sort("date", -1))
    
    def find_employee_by_face_name(self, face_name):
        """Find employee by face name"""
        # First try to find by linked face
        face_doc = self.faces_collection.find_one({"name": face_name})
        if face_doc and "employee_id" in face_doc:
            return self.get_employee(face_doc["employee_id"])
        
        # Fallback: try to find employee with matching name
        return self.get_employee_by_name(face_name)
    
    def close(self):
        """Close database connection"""
        # Database manager handles connection closure
        pass