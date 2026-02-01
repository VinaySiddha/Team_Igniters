#!/usr/bin/env python3
"""
Smart Attendance System - Diagnostic Tool
Run this to check if your system is ready
"""

import sys
import os

print("=" * 60)
print("🔍 SMART ATTENDANCE SYSTEM - DIAGNOSTIC CHECK")
print("=" * 60)
print()

issues_found = []
warnings = []

# 1. Check Python version
print("1️⃣  Checking Python version...")
version = sys.version_info
if version.major >= 3 and version.minor >= 8:
    print(f"   ✅ Python {version.major}.{version.minor}.{version.micro} - OK")
else:
    print(f"   ❌ Python {version.major}.{version.minor}.{version.micro} - TOO OLD")
    issues_found.append("Python version < 3.8")
print()

# 2. Check required packages
print("2️⃣  Checking required packages...")
required_packages = {
    'flask': 'Flask',
    'flask_cors': 'Flask-CORS',
    'cv2': 'OpenCV',
    'numpy': 'NumPy',
    'pandas': 'Pandas'
}

for module_name, display_name in required_packages.items():
    try:
        if module_name == 'flask_cors':
            __import__('flask_cors')
        else:
            __import__(module_name)
        print(f"   ✅ {display_name} - Installed")
    except ImportError:
        print(f"   ❌ {display_name} - NOT FOUND")
        issues_found.append(f"{display_name} not installed")
print()

# 3. Check cv2.face module (for face recognition)
print("3️⃣  Checking OpenCV face module...")
try:
    import cv2
    recognizer = cv2.face.LBPHFaceRecognizer_create()
    print("   ✅ OpenCV face module - Available")
except AttributeError:
    print("   ❌ OpenCV face module - NOT FOUND")
    print("      Install: pip install opencv-contrib-python")
    issues_found.append("opencv-contrib-python not installed")
except ImportError:
    print("   ❌ OpenCV - NOT FOUND")
    issues_found.append("OpenCV not installed")
print()

# 4. Check camera
print("4️⃣  Checking camera access...")
try:
    import cv2
    cam = cv2.VideoCapture(0)
    if cam.isOpened():
        ret, frame = cam.read()
        if ret:
            print(f"   ✅ Camera - Working (Resolution: {frame.shape[1]}x{frame.shape[0]})")
        else:
            print("   ⚠️  Camera opens but cannot read frames")
            warnings.append("Camera connection unstable")
        cam.release()
    else:
        print("   ❌ Camera - CANNOT OPEN")
        issues_found.append("Camera not accessible")
except Exception as e:
    print(f"   ❌ Camera - ERROR: {e}")
    issues_found.append("Camera error")
print()

# 5. Check dataset folder
print("5️⃣  Checking dataset folder...")
dataset_path = "dataset"
if os.path.exists(dataset_path):
    persons = [d for d in os.listdir(dataset_path) if os.path.isdir(os.path.join(dataset_path, d))]
    if persons:
        print(f"   ✅ Dataset folder - Found ({len(persons)} persons)")
        for person in persons:
            person_path = os.path.join(dataset_path, person)
            image_count = len([f for f in os.listdir(person_path) if f.endswith(('.jpg', '.png'))])
            print(f"      📁 {person}: {image_count} images")
            if image_count < 30:
                warnings.append(f"{person} has only {image_count} images (recommend 50+)")
    else:
        print("   ⚠️  Dataset folder exists but EMPTY")
        warnings.append("No face data captured")
else:
    print("   ❌ Dataset folder - NOT FOUND")
    issues_found.append("Dataset folder missing - run face_capture.py")
print()

# 6. Check trainer model
print("6️⃣  Checking trainer model...")
trainer_path = "trainer/trainer.yml"
if os.path.exists(trainer_path):
    file_size = os.path.getsize(trainer_path)
    print(f"   ✅ Trainer model - Found ({file_size} bytes)")
    if file_size < 1000:
        warnings.append("Trainer file seems too small")
else:
    print("   ❌ Trainer model - NOT FOUND")
    issues_found.append("Trainer model missing - run train_model.py")
print()

# 7. Check Haar Cascade
print("7️⃣  Checking Haar Cascade classifier...")
try:
    import cv2
    cascade_path = cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
    if os.path.exists(cascade_path):
        cascade = cv2.CascadeClassifier(cascade_path)
        if not cascade.empty():
            print("   ✅ Haar Cascade - Loaded")
        else:
            print("   ❌ Haar Cascade - Failed to load")
            issues_found.append("Haar Cascade loading failed")
    else:
        print("   ❌ Haar Cascade - File not found")
        issues_found.append("Haar Cascade file missing")
except Exception as e:
    print(f"   ❌ Haar Cascade - ERROR: {e}")
    issues_found.append("Haar Cascade error")
print()

# 8. Check attendance file
print("8️⃣  Checking attendance file...")
attendance_file = "attendance.csv"
if os.path.exists(attendance_file):
    file_size = os.path.getsize(attendance_file)
    print(f"   ✅ Attendance file - Found ({file_size} bytes)")
else:
    print("   ℹ️  Attendance file - Not found (will be created)")
print()

# 9. Check project files
print("9️⃣  Checking project files...")
required_files = {
    'app.py': 'Backend server',
    'face_capture.py': 'Face capture script',
    'train_model.py': 'Model training script',
    'recognize_attendance.py': 'Recognition script',
    'index.html': 'Login page',
    'pages/faculty-dashboard.html': 'Faculty dashboard'
}

for file_path, description in required_files.items():
    if os.path.exists(file_path):
        print(f"   ✅ {description} - Found")
    else:
        print(f"   ❌ {description} - NOT FOUND")
        issues_found.append(f"{file_path} missing")
print()

# Summary
print("=" * 60)
print("📊 DIAGNOSTIC SUMMARY")
print("=" * 60)
print()

if not issues_found and not warnings:
    print("🎉 ALL CHECKS PASSED!")
    print("   Your system is ready to run.")
    print()
    print("📝 Next steps:")
    print("   1. Start backend: python app.py")
    print("   2. Open index.html in browser")
    print("   3. Login as faculty (faculty/1234)")
    print("   4. Select branch and section")
    print("   5. Click 'Start Attendance'")
else:
    if issues_found:
        print(f"❌ CRITICAL ISSUES FOUND: {len(issues_found)}")
        for i, issue in enumerate(issues_found, 1):
            print(f"   {i}. {issue}")
        print()
    
    if warnings:
        print(f"⚠️  WARNINGS: {len(warnings)}")
        for i, warning in enumerate(warnings, 1):
            print(f"   {i}. {warning}")
        print()
    
    print("🔧 RECOMMENDED ACTIONS:")
    print()
    
    # Provide specific solutions
    if any("not installed" in issue for issue in issues_found):
        print("   Install missing packages:")
        print("   → pip install flask flask-cors opencv-python opencv-contrib-python numpy pandas")
        print()
    
    if any("Dataset" in issue for issue in issues_found):
        print("   Capture face data:")
        print("   → python face_capture.py")
        print("   → Enter each student's name and capture 50+ images")
        print()
    
    if any("Trainer" in issue for issue in issues_found):
        print("   Train the model:")
        print("   → python train_model.py")
        print("   → This creates the trainer.yml file")
        print()
    
    if any("Camera" in issue for issue in issues_found):
        print("   Fix camera issues:")
        print("   → Close other apps using camera (Zoom, Teams, etc.)")
        print("   → Check camera permissions in system settings")
        print("   → Try: python -c 'import cv2; print(cv2.VideoCapture(0).isOpened())'")
        print()

print("=" * 60)
print()
print("💡 For detailed help, see the Setup Guide")
print("🐛 Still having issues? Check:")
print("   • Flask terminal output")
print("   • Browser console (F12)")
print("   • Camera window for recognition status")
print()