# Face Recognition System - Installation Guide

Face recognition attendance system with motion detection and MongoDB integration.

## 🔧 System Requirements

- **Python 3.11** (REQUIRED for Spark compatibility)
- **Java JDK 11** and **Apache Hadoop 3.0+** (for Apache Spark)
- **MongoDB** (local or remote)
- **Webcam** or video input device
- **Windows 10/11** (recommended for easier dlib installation)

## 📦 Installation Steps

### 1. Install Java JDK 11
1. Download **OpenJDK 11** from [Microsoft OpenJDK](https://docs.microsoft.com/en-us/java/openjdk/download#openjdk-11)
2. Install to default location: `C:\Program Files\Java\jdk-11`
3. Add to system PATH and set `JAVA_HOME` environment variable

### 2. Install Apache Hadoop
1. Download **Hadoop 3.0.0** from [Apache Hadoop](https://hadoop.apache.org/releases.html)
2. Extract to: `C:\hadoop-3.0.0`
3. Download `winutils.exe` from [WinUtils Repository](https://github.com/steveloughran/winutils)
4. Copy `winutils.exe` to: `C:\hadoop-3.0.0\bin\winutils.exe`
5. Add Hadoop to system PATH and set `HADOOP_HOME` environment variable

### 3. Environment Variables Setup

Add these environment variables to your system:

```bash
# Java
JAVA_HOME=C:\Program Files\Java\jdk-11

# Hadoop
HADOOP_HOME=C:\hadoop-3.0.0

# Spark Python Configuration
PYSPARK_PYTHON=[path_to_your_python.exe]
PYSPARK_DRIVER_PYTHON=[path_to_your_python.exe]

# Add to PATH
PATH=%PATH%;%JAVA_HOME%\bin;%HADOOP_HOME%\bin
```

### 4. Install MongoDB
1. Download from [MongoDB Download Center](https://www.mongodb.com/try/download/community)
2. Install with default settings
3. MongoDB will run on `localhost:27017` by default

### 5. Install Python Dependencies

```bash
# Create virtual environment (recommended)
python -m venv face_recognition_env

# Activate virtual environment
face_recognition_env\Scripts\activate

# Install core dependencies
pip install -r requirements.txt

# Install face recognition library
pip install face-recognition

# If dlib installation fails on Windows:
pip install cmake
pip install dlib
```

### 6. Setup for dlib

If `pip install face-recognition` fails:

1. **Install Visual Studio Build Tools**:
   - Download from [Microsoft Visual Studio](https://visualstudio.microsoft.com/downloads/)
   - Select "Desktop development with C++" workload
   - Include Windows 11 SDK

2. **Alternative - Use pre-compiled wheels**:
   ```bash
   pip install dlib --find-links https://github.com/sachadee/Dlib
   pip install face-recognition
   ```

### 7. Verify Installations

```bash
# Test libraries
python -c "import cv2, face_recognition, pymongo; print('All dependencies installed')"

# Test Java
java -version

# Test Hadoop
hadoop version

# Test Spark
python -c "import pyspark; print('Spark version:', pyspark.__version__)"
```

## 🚀 Quick Start

### 1. Start MongoDB
MongoDB usually starts automatically after installation, check MongoDB service to be sure

### 2. Run the Application

```bash
# Navigate to project directory
cd face_recognition_system

# Run the refactored application
python face_recognition_app_refactored.py
```

### 3. First Time Setup

1. **Add Employees**: Click "Add Employee" to register people
2. **Enroll Faces**: Select employee and click "Enroll Face" to capture face samples
3. **Start Recognition**: Click "Start Recognition" to begin automatic attendance
4. **Data Analytics**: Navigate to "Data Analytics" tab and click "Run Analytics"

## 📋 Features

- **Automatic Face Recognition** (with face_recognition library)
- **Motion Detection** (conserves resources)
- **Employee Management** (add, view, manage employees)
- **Attendance Tracking** (automatic and manual)
- **Real-time Video Processing** (800x600 display)
- **MongoDB Integration** (persistent data storage)
- **Scalable Data Analytics** (designed for large datasets)

## Troubleshooting

### Common Issues

**1. Camera not found**
```
Error: Unable to open video source 0
```
- Check if camera is connected and not used by another app
- Try different camera index in config: `"source": 1`

**2. MongoDB connection failed**
```
Error: Database connection failed
```
- Ensure MongoDB is running: `mongod --version`
- Check connection string in `config/system_config.json`

**3. Hadoop/WinUtils Error**
```HADOOP_HOME and hadoop.home.dir are unset```
- Download and install winutils.exe in Hadoop bin directory
- Set HADOOP_HOME environment variable
- Add Hadoop bin to PATH

**4. face_recognition library not found**
```
face_recognition library not available
```
- System will work in "detection only" mode
- Install face_recognition: `pip install face-recognition`

**5. Poor face recognition**
- Ensure good lighting during enrollment
- Capture multiple samples (5 recommended)
- Keep face centered and clearly visible

### Performance Tips

- **Good Lighting**: Ensure well-lit environment for better recognition
- **Camera Position**: Place camera at eye level for best results
- **Distance**: Stay 2-3 feet from camera during enrollment
- **Multiple Samples**: Capture 5+ samples with slight pose variations

## 🔧 Configuration

Edit `config/system_config.json` to customize:

```json
{
    "video": {
        "source": 0,          // Camera index
        "frame_width": 640,
        "frame_height": 480
    },
    "motion_detection": {
        "threshold": 25,      // Lower = more sensitive
        "min_area": 500
    },
    "face_recognition": {
        "recognition_threshold": 0.6  // Lower = more strict
    },
    "database": {
        "mongodb_uri": "mongodb://localhost:27017/",
        "database_name": "face_recognition_db"
    }
}
```

## Project Structure
```
face_recognition/
├── README.md
├── face_recognition_app.py                 # Main entry point
├── requirements.txt
├── .gitignore
│
├── config/
│   └── system_config.json                  # System configuration
│
├── src/
│   ├── __init__.py
│   │
│   ├── analytics/                          # Big Data Analytics
│   │   ├── __init__.py
│   │   └── spark_analytics.py              # Spark distributed processing
│   │
│   ├── database/                           # Database layer
│   │   ├── __init__.py
│   │   ├── employee_database.py            # Employee operations
│   │   ├── face_database.py                # Face data operations
│   │   └── database_manager.py             # Database connection manager
│   │
│   ├── processing/                         # Core processing logic
│   │   ├── __init__.py
│   │   ├── video_stream.py                 # Video capture
│   │   ├── motion_detector.py              # Motion detection
│   │   ├── face_processor.py               # Face detection/recognition
│   │   ├── face_enrollment.py              # Face enrollment logic
│   │   └── integrated_system.py            # System integration
│   │
│   ├── ui/                                 # User Interface components
│   │   ├── __init__.py
│   │   ├── main_window.py                  # Main application window
│   │   ├── video_panel.py                  # Video display panel
│   │   ├── info_tabs.py                    # Information tabs (including analytics)
│   │   ├── dialogs.py                      # Dialog windows
│   │   └── components.py                   # Reusable UI components
│   │
│   └── utils/                              # Utilities
│       ├── __init__.py
│       └── config_loader.py                # Configuration loading
│
└── test_notebooks/                         # Jupyter notebooks for testing
    ├── 2_face_enrollment.ipynb
    └── 3_integrated_system.ipynb
```

## System Architecture

```
┌─────────────────┐        ┌──────────────────┐    ┌─────────────────┐
│   Camera Input  │     →  │ Motion Detection │ →  │ Face Recognition│
└─────────────────┘        └──────────────────┘    └─────────────────┘
                                     ↓
┌─────────────────┐        ┌──────────────────┐    ┌─────────────────┐
│   UI Display    │     ←  │ Main Application │ →  │ MongoDB Storage │
└─────────────────┘        └──────────────────┘    └─────────────────┘
                                     ↓
┌─────────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│ Analytics Dashboard │ ←  │   Apache Spark   │ →  │ Hadoop Ecosystem│
└─────────────────────┘    └──────────────────┘    └─────────────────┘
```

## Database Collections

The system creates these MongoDB collections automatically:

- **employees**: Employee information and settings
- **faces**: Face encodings and samples
- **attendance**: Daily attendance records
- **recognition_events**: Face recognition event logs
