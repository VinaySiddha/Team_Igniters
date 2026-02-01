"""
Face Recognition Attendance System
Smart Attendance - Sri Vasavi Engineering College
"""

import cv2
import csv
import os
import sys
import json
from datetime import datetime
from validators import is_duplicate_attendance, remove_duplicate_entries, get_today_attendance_count

# Load student database
def load_student_database():
    db_file = "student_database.json"
    if os.path.exists(db_file):
        try:
            with open(db_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {}
    return {}

print("=" * 60)
print("🎓 Smart Attendance System - Face Recognition")
print("   Sri Vasavi Engineering College")
print("=" * 60)

# Get branch and section from command line
if len(sys.argv) < 3:
    print("❌ Error: Branch and Section arguments required")
    print("Usage: python recognize_attendance.py <BRANCH> <SECTION>")
    print("Example: python recognize_attendance.py AIML A")
    sys.exit(1)

branch = sys.argv[1]
section = sys.argv[2]

print(f"✅ Branch: {branch}")
print(f"✅ Section: {section}")

# Load student database
student_db = load_student_database()
print(f"✅ Loaded database with {len(student_db)} students")

# Load trained recognizer
recognizer = cv2.face.LBPHFaceRecognizer_create()
trainer_path = "trainer/trainer.yml"

if not os.path.exists(trainer_path):
    print(f"❌ Error: {trainer_path} not found. Please train the model first.")
    print("Run: python train_model.py")
    sys.exit(1)

try:
    recognizer.read(trainer_path)
    print("✅ Model loaded successfully")
except Exception as e:
    print(f"❌ Error loading model: {e}")
    sys.exit(1)

# Load face cascade
face_cascade = cv2.CascadeClassifier(
    cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
)

if face_cascade.empty():
    print("❌ Error: Could not load face cascade")
    sys.exit(1)

print("✅ Face cascade loaded")

# Load label mapping and student info
dataset_path = "dataset"
label_map = {}
name_to_info = {}
label_id = 0

if not os.path.exists(dataset_path):
    print(f"❌ Error: {dataset_path} folder not found")
    sys.exit(1)

for person_name in os.listdir(dataset_path):
    person_folder = os.path.join(dataset_path, person_name)
    if os.path.isdir(person_folder):
        label_map[label_id] = person_name
        
        # Find student info in database
        student_id = person_name.lower().replace(" ", "_")
        if student_id in student_db:
            name_to_info[person_name] = student_db[student_id]
        else:
            # If not in database, create basic info
            name_to_info[person_name] = {
                'rollNo': 'N/A',
                'branch': 'UNKNOWN',
                'section': 'UNKNOWN'
            }
        
        label_id += 1

print(f"✅ Loaded {len(label_map)} students from dataset")

# Attendance file
attendance_file = "attendance.csv"

if not os.path.exists(attendance_file):
    with open(attendance_file, "w", newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(["Name", "RollNo", "Branch", "Section", "Date", "Time"])
    print("✅ Created new attendance.csv file")

# Clean up any existing duplicates before starting
print("🧹 Checking for duplicate entries...")
duplicates_removed = remove_duplicate_entries(attendance_file, create_backup=False)
if duplicates_removed > 0:
    print(f"✅ Cleaned {duplicates_removed} duplicate entries")

# Check how many already marked today
already_marked = get_today_attendance_count(branch, section, attendance_file)
print(f"📊 Students already marked today: {already_marked}")

marked_names = set()

# Start camera
print("🎥 Opening camera...")
cam = cv2.VideoCapture(0)

if not cam.isOpened():
    print("❌ Error: Cannot open camera")
    sys.exit(1)

print(f"✅ Camera opened successfully")
print(f"📸 Starting attendance for {branch}-{section}")
print("=" * 60)
print("💡 INSTRUCTIONS:")
print("  • Students should look at the camera")
print("  • Green box = Recognized and marked")
print("  • Orange box = Already marked today")
print("  • Blue box = Wrong class")
print("  • Red box = Unknown face")
print("  • Press 'Q' to stop")
print("=" * 60)

frame_count = 0
last_recognition_time = {}  # Track last recognition time per face

while True:
    ret, frame = cam.read()
    if not ret:
        print("❌ Error: Cannot read from camera")
        break

    frame_count += 1
    
    # Flip for mirror effect
    frame = cv2.flip(frame, 1)
    
    # Convert to grayscale for detection
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    
    # Detect faces (do this every frame for smooth display)
    faces = face_cascade.detectMultiScale(gray, 1.2, 5, minSize=(100, 100))

    current_time = datetime.now()

    for (x, y, w, h) in faces:
        # Only process recognition every 5th frame to reduce flickering
        # but draw boxes every frame for smooth display
        should_process = (frame_count % 5 == 0)
        
        if should_process:
            face_img = gray[y:y+h, x:x+w]
            
            try:
                label, confidence = recognizer.predict(face_img)
                
                # Calculate match percentage (lower confidence = better match)
                # confidence ranges from 0-100+, we invert it for display
                match_percentage = max(0, min(100, 100 - confidence))
                
                if confidence < 80:  # Good match threshold
                    name = label_map.get(label, "Unknown")
                    
                    # Get student info from database
                    student_info = name_to_info.get(name, {})
                    roll_no = student_info.get('rollNo', 'N/A')
                    student_branch = student_info.get('branch', 'UNKNOWN')
                    student_section = student_info.get('section', 'UNKNOWN')
                    
                    # Store in frame for display
                    face_data = {
                        'name': name,
                        'roll_no': roll_no,
                        'branch': student_branch,
                        'section': student_section,
                        'confidence': confidence,
                        'match_percentage': match_percentage,
                        'recognized': True
                    }
                    
                    # Check if belongs to this class
                    if student_branch == branch and student_section == section:
                        
                        if name not in marked_names:
                            # Check if already marked today
                            is_dup, existing_time = is_duplicate_attendance(
                                name, roll_no, branch, section, attendance_file
                            )
                            
                            if is_dup:
                                # Already marked - orange
                                face_data['status'] = 'already_marked'
                                face_data['time'] = existing_time
                                marked_names.add(name)
                                print(f"⚠️  SKIPPED: {name} ({roll_no}) already marked at {existing_time}")
                            else:
                                # Mark attendance
                                now = datetime.now()
                                date_str = now.strftime("%Y-%m-%d")
                                time_str = now.strftime("%H:%M:%S")
                                
                                try:
                                    with open(attendance_file, "a", newline='', encoding='utf-8') as f:
                                        writer = csv.writer(f)
                                        writer.writerow([name, roll_no, branch, section, date_str, time_str])
                                    
                                    marked_names.add(name)
                                    face_data['status'] = 'marked'
                                    print(f"✅ MARKED: {name} ({roll_no}) | Match: {match_percentage:.1f}% | {time_str}")
                                except Exception as e:
                                    print(f"❌ Error: {e}")
                        else:
                            face_data['status'] = 'present'
                    else:
                        # Wrong class
                        face_data['status'] = 'wrong_class'
                else:
                    # Low confidence / Unknown
                    face_data = {
                        'name': 'Unknown',
                        'confidence': confidence,
                        'match_percentage': match_percentage,
                        'status': 'unknown',
                        'recognized': False
                    }
            except:
                face_data = {
                    'name': 'Error',
                    'status': 'error',
                    'recognized': False
                }
        else:
            # Use last known data or default
            if not hasattr(cv2, '_last_face_data'):
                cv2._last_face_data = {}
            face_key = f"{x}_{y}"
            face_data = cv2._last_face_data.get(face_key, {
                'name': 'Processing...',
                'status': 'processing',
                'recognized': False
            })
        
        # Store for next frame
        if not hasattr(cv2, '_last_face_data'):
            cv2._last_face_data = {}
        cv2._last_face_data[f"{x}_{y}"] = face_data
        
        # ============ DRAW FACE BOX AND INFO ============
        
        if face_data.get('recognized', False):
            status = face_data.get('status', 'unknown')
            name = face_data['name']
            confidence = face_data.get('confidence', 0)
            match_pct = face_data.get('match_percentage', 0)
            
            # Determine color based on status
            if status == 'marked':
                color = (0, 255, 0)  # Green - just marked
                status_text = "✓ MARKED!"
                thickness = 4
            elif status == 'already_marked':
                color = (0, 165, 255)  # Orange - already marked
                status_text = "ALREADY MARKED"
                thickness = 3
            elif status == 'present':
                color = (0, 255, 0)  # Green - present
                status_text = "PRESENT"
                thickness = 2
            elif status == 'wrong_class':
                color = (255, 0, 0)  # Blue - wrong class
                status_text = "WRONG CLASS"
                thickness = 2
            else:
                color = (128, 128, 128)  # Gray - other
                status_text = "RECOGNIZED"
                thickness = 2
            
            # Draw rectangle
            cv2.rectangle(frame, (x, y), (x+w, y+h), color, thickness)
            
            # Background for text
            cv2.rectangle(frame, (x, y-120), (x+w, y), (0, 0, 0), -1)
            cv2.rectangle(frame, (x, y-120), (x+w, y), color, 2)
            
            # Display name
            cv2.putText(frame, name, (x+5, y-95),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            
            # Display status
            cv2.putText(frame, status_text, (x+5, y-70),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
            
            # Display roll number
            if face_data.get('roll_no'):
                cv2.putText(frame, f"Roll: {face_data['roll_no']}", (x+5, y-48),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
            
            # Display match percentage with bar
            cv2.putText(frame, f"Match: {match_pct:.1f}%", (x+5, y-28),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
            
            # Draw match percentage bar
            bar_width = w - 10
            bar_height = 8
            bar_x = x + 5
            bar_y = y - 15
            
            # Background bar
            cv2.rectangle(frame, (bar_x, bar_y), (bar_x + bar_width, bar_y + bar_height), 
                         (50, 50, 50), -1)
            
            # Fill bar based on percentage
            fill_width = int((match_pct / 100) * bar_width)
            
            # Color based on match quality
            if match_pct >= 70:
                bar_color = (0, 255, 0)  # Green - excellent
            elif match_pct >= 50:
                bar_color = (0, 255, 255)  # Yellow - good
            else:
                bar_color = (0, 165, 255)  # Orange - low
            
            cv2.rectangle(frame, (bar_x, bar_y), (bar_x + fill_width, bar_y + bar_height),
                         bar_color, -1)
            
            # Display time if already marked
            if status == 'already_marked' and face_data.get('time'):
                cv2.putText(frame, f"At: {face_data['time']}", (x+5, y-5),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)
            
        else:
            # Unknown or error
            if face_data.get('status') == 'unknown':
                color = (0, 0, 255)  # Red
                cv2.rectangle(frame, (x, y), (x+w, y+h), color, 2)
                
                # Background
                cv2.rectangle(frame, (x, y-80), (x+w, y), (0, 0, 0), -1)
                cv2.rectangle(frame, (x, y-80), (x+w, y), color, 2)
                
                cv2.putText(frame, "UNKNOWN", (x+5, y-55),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
                
                # Show confidence
                if face_data.get('confidence'):
                    conf = face_data['confidence']
                    match_pct = face_data.get('match_percentage', 0)
                    cv2.putText(frame, f"Match: {match_pct:.1f}%", (x+5, y-30),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
                    cv2.putText(frame, f"(Too Low)", (x+5, y-10),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)
            else:
                # Processing or error
                cv2.rectangle(frame, (x, y), (x+w, y+h), (128, 128, 128), 1)
                cv2.putText(frame, "Detecting...", (x+5, y-10),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (128, 128, 128), 1)

    # ============ DISPLAY DASHBOARD INFO ============
    
    # Dark semi-transparent background for info panel
    overlay = frame.copy()
    cv2.rectangle(overlay, (0, 0), (400, 130), (0, 0, 0), -1)
    cv2.addWeighted(overlay, 0.7, frame, 0.3, 0, frame)
    
    # Display class info
    cv2.putText(frame, f"Class: {branch}-{section}", (10, 30),
               cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
    
    cv2.putText(frame, f"Marked in session: {len(marked_names)}", (10, 65),
               cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
    
    total_today = already_marked + len(marked_names)
    cv2.putText(frame, f"Total today: {total_today}", (10, 95),
               cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
    
    # Instructions at bottom
    cv2.rectangle(overlay, (0, frame.shape[0]-40), (frame.shape[1], frame.shape[0]), (0, 0, 0), -1)
    cv2.addWeighted(overlay, 0.7, frame, 0.3, 0, frame)
    
    cv2.putText(frame, "Press 'Q' to Stop | Green=Marked | Orange=Already Present | Red=Unknown", 
               (10, frame.shape[0] - 15), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)

    # Show frame (no flickering because we show every frame)
    cv2.imshow(f"Smart Attendance - {branch}-{section}", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        print("\n⏹️  Stopping by user request...")
        break

cam.release()
cv2.destroyAllWindows()

print("\n" + "=" * 60)
print("✅ ATTENDANCE SESSION COMPLETED")
print("=" * 60)
print(f"📊 Class: {branch}-{section}")
print(f"👥 Marked in this session: {len(marked_names)}")

if marked_names:
    print("\n📋 Students Marked:")
    for i, name in enumerate(sorted(marked_names), 1):
        info = name_to_info.get(name, {})
        roll = info.get('rollNo', 'N/A')
        print(f"   {i}. {name} ({roll})")
else:
    print("\n⚠️  No new students marked in this session")

print("=" * 60)
print(f"💾 Attendance saved to: {attendance_file}")
print("=" * 60)