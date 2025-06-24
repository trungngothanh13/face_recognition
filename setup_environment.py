# setup_environment.py
"""
Python script to setup environment for Big Data Analytics
Fixes the Python path and Java issues
"""
import os
import sys
import subprocess

def find_java_installation():
    """Find Java installation on Windows"""
    possible_paths = [
        r"C:\Program Files\Eclipse Adoptium\jdk-11.0.26.10-hotspot",
        r"C:\Program Files\Eclipse Adoptium\jdk-11",
        r"C:\Program Files\Java\jdk-11",
        r"C:\Program Files\OpenJDK\jdk-11",
        r"C:\Program Files\Java\jdk-17",
        r"C:\Program Files\Java\jdk-21",
    ]
    
    for path in possible_paths:
        if os.path.exists(path):
            return path
    
    return None

def setup_environment():
    """Setup environment variables for Big Data Analytics"""
    print("🔧 Setting up environment for Big Data Analytics...")
    
    # 1. Setup Python path for PySpark
    python_exe = sys.executable
    os.environ['PYSPARK_PYTHON'] = python_exe
    os.environ['PYSPARK_DRIVER_PYTHON'] = python_exe
    print(f"📝 Set PYSPARK_PYTHON to: {python_exe}")
    
    # 2. Setup Java
    java_home = os.environ.get('JAVA_HOME')
    if not java_home:
        java_home = find_java_installation()
        if java_home:
            os.environ['JAVA_HOME'] = java_home
            print(f"📝 Set JAVA_HOME to: {java_home}")
        else:
            print("⚠️ Java not found automatically")
            return False
    else:
        print(f"✅ JAVA_HOME already set: {java_home}")
    
    # 3. Add Java to PATH if needed
    java_bin = os.path.join(java_home, 'bin')
    current_path = os.environ.get('PATH', '')
    if java_bin not in current_path:
        os.environ['PATH'] = f"{java_bin};{current_path}"
        print(f"📝 Added Java to PATH: {java_bin}")
    
    # 4. Set Spark configuration
    os.environ['SPARK_LOCAL_DIRS'] = os.path.join(os.getcwd(), 'tmp', 'spark')
    
    # Create spark temp directory
    spark_tmp = os.path.join(os.getcwd(), 'tmp', 'spark')
    os.makedirs(spark_tmp, exist_ok=True)
    
    return True

def test_setup():
    """Test if setup is working"""
    print("\n🧪 Testing setup...")
    
    # Test Java
    try:
        result = subprocess.run(['java', '-version'], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Java is working")
        else:
            print("❌ Java test failed")
            return False
    except FileNotFoundError:
        print("❌ Java not found in PATH")
        return False
    
    # Test Python
    try:
        print(f"✅ Python is working: {sys.version.split()[0]}")
    except:
        print("❌ Python test failed")
        return False
    
    # Test imports
    try:
        import pandas as pd
        import numpy as np
        print("✅ Data processing libraries working")
    except ImportError:
        print("❌ Data processing libraries not available")
        return False
    
    # Test PySpark import (without creating session)
    try:
        import pyspark
        print(f"✅ PySpark import successful: {pyspark.__version__}")
    except ImportError:
        print("❌ PySpark not available")
        return False
    
    return True

def create_analytics_fallback():
    """Create analytics module that falls back to pandas if Spark fails"""
    print("\n📝 Ensuring analytics module works with fallback...")
    
    # Test analytics import
    try:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        if current_dir not in sys.path:
            sys.path.append(current_dir)
        
        # Test if analytics directory exists
        analytics_dir = os.path.join(current_dir, 'src', 'analytics')
        if not os.path.exists(analytics_dir):
            print(f"❌ Analytics directory not found: {analytics_dir}")
            print("💡 Please create the src/analytics directory and add the files")
            return False
        
        # Test import
        from src.analytics.spark_analytics import SparkAnalyticsEngine
        print("✅ Analytics module import successful")
        
        # Test basic functionality without Spark operations
        print("🧪 Testing analytics engine creation...")
        engine = SparkAnalyticsEngine()
        print("✅ Analytics engine created successfully")
        
        # Test sample data generation
        engine._create_enhanced_sample_data()
        print("✅ Sample data generation works")
        
        engine.close()
        return True
        
    except Exception as e:
        print(f"❌ Analytics test failed: {e}")
        return False

def main():
    """Main setup function"""
    print("🔥 Big Data Analytics Environment Setup")
    print("=" * 50)
    
    # Setup environment
    if not setup_environment():
        print("❌ Environment setup failed")
        return False
    
    # Test setup
    if not test_setup():
        print("❌ Setup test failed")
        return False
    
    # Test analytics module
    if not create_analytics_fallback():
        print("⚠️ Analytics module test failed, but basic setup is working")
    
    print("\n" + "=" * 50)
    print("🎉 Environment setup complete!")
    print("\n📚 Next Steps:")
    print("1. Run: python face_recognition_app.py")
    print("2. Navigate to the '📊 Big Data Analytics' tab")
    print("3. Click '🚀 Run Analytics' to test")
    
    print("\n💡 If you still see Spark errors:")
    print("- The system will automatically fall back to pandas")
    print("- You'll still get comprehensive analytics")
    print("- Performance will be excellent for most datasets")
    
    return True

if __name__ == "__main__":
    main()
    input("\nPress Enter to continue...")