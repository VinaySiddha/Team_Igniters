import cv2
import os
import json
from datetime import datetime

# Student database file
STUDENT_DB = "student_database.json"

def load_student_database():
    """Load existing student database"""
    if os.path.exists(STUDENT_DB):
        with open(STUDENT_DB, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def save_student_database(db):
    """Save student database"""
    with open(STUDENT_DB, 'w', encoding='utf-8') as f:
        json.dump(db, indent=4, fp=f)

def get_next_roll_number(branch, section):
    """Auto-generate next roll number"""
    db = load_student_database()
    prefix = f"{branch}{section}"
    
    # Find highest existing number
    max_num = 0
    for student_id, info in db.items():
        if info.get('branch') == branch and info.get('section') == section:
            try:
                roll = info.get('rollNo', '')
                if roll.startswith(prefix):
                    num = int(roll.replace(prefix, ''))
                    max_num = max(max_num, num)
            except:
                pass
    
    return f"{prefix}{str(max_num + 1).zfill(3)}"

def capture_student_faces():
    """Enhanced face capture with student information"""
    print("=" * 60)
    print("📸 SMART ATTENDANCE - STUDENT FACE CAPTURE")
    print("=" * 60)
    
    # Get student information
    name = input("\nEnter student name: ").strip()
    if not name:
        print("❌ Name cannot be empty!")
        return
    
    # Get branch
    print("\n🏢 Select Branch:")
    branches = ["CSE", "AIML", "ECE", "EEE", "MECH", "CIVIL"]
    for i, b in enumerate(branches, 1):
        print(f"  {i}. {b}")
    
    while True:
        branch_choice = input("\nEnter branch number (1-6): ").strip()
        try:
            branch = branches[int(branch_choice) - 1]
            break
        except:
            print("❌ Invalid choice! Please enter 1-6")
    
    # Get section
    print("\n📋 Select Section:")
    print("  1. Section A")
    print("  2. Section B")
    
    while True:
        section_choice = input("\nEnter section (1-2): ").strip()
        if section_choice in ['1', '2']:
            section = "A" if section_choice == "1" else "B"
            break
        else:
            print("❌ Invalid choice! Please enter 1 or 2")
    
    # Auto-generate or manual roll number
    suggested_roll = get_next_roll_number(branch, section)
    print(f"\n🎓 Suggested Roll Number: {suggested_roll}")
    roll_no = input(f"Press ENTER to use '{suggested_roll}' or type custom roll number: ").strip()
    
    if not roll_no:
        roll_no = suggested_roll
    
    # Check if student already exists
    db = load_student_database()
    student_id = name.lower().replace(" ", "_")
    
    if student_id in db:
        print(f"\n⚠️  WARNING: Student '{name}' already exists in database!")
        print(f"   Existing info: {db[student_id]['rollNo']} - {db[student_id]['branch']}-{db[student_id]['section']}")
        overwrite = input("   Do you want to overwrite? (yes/no): ").strip().lower()
        if overwrite != 'yes':
            print("❌ Capture cancelled")
            return
    
    # Create dataset directory
    dataset_path = os.path.join(os.getcwd(), "dataset", name)
    os.makedirs(dataset_path, exist_ok=True)
    
    # Initialize camera
    print("\n📷 Opening camera...")
    cam = cv2.VideoCapture(0)
    
    if not cam.isOpened():
        print("❌ Cannot open camera!")
        return
    
    # Set camera properties for better quality
    cam.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cam.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    
    # Load face cascade
    face_cascade = cv2.CascadeClassifier(
        cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
    )
    
    if face_cascade.empty():
        print("❌ Error loading face cascade!")
        cam.release()
        return
    
    required_images = 50
    saved_count = 0
    frame_skip = 2  # Capture every 2nd detected face for variety
    detect_counter = 0
    
    print("\n" + "=" * 60)
    print(f"👤 Student: {name}")
    print(f"🎓 Roll No: {roll_no}")
    print(f"🏢 Branch: {branch}")
    print(f"📋 Section: {section}")
    print("=" * 60)
    print(f"📸 Need to capture {required_images} images")
    print("\n💡 INSTRUCTIONS:")
    print("  • Look straight at the camera")
    print("  • Slowly move your head: left, right, up, down")
    print("  • Ensure good lighting")
    print("  • Keep your face in the yellow box")
    print("  • Press 'Q' to quit anytime")
    print("=" * 60)
    print("\n⏳ Starting in 3 seconds...")
    
    import time
    time.sleep(3)
    
    while saved_count < required_images:
        ret, frame = cam.read()
        if not ret:
            print("\n❌ Error reading from camera")
            break
        
        # Flip frame for mirror effect
        frame = cv2.flip(frame, 1)
        
        # Convert to grayscale
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Detect faces with better parameters
        faces = face_cascade.detectMultiScale(
            gray, 
            scaleFactor=1.2, 
            minNeighbors=5,
            minSize=(120, 120)
        )
        
        # Process faces
        face_detected = False
        for (x, y, w, h) in faces:
            face_detected = True
            detect_counter += 1
            
            # Only save every Nth detection for variety
            if detect_counter % frame_skip == 0 and saved_count < required_images:
                face = gray[y:y+h, x:x+w]
                
                # Save face image
                saved_count += 1
                filename = f"{dataset_path}/{saved_count}.jpg"
                cv2.imwrite(filename, face)
                
                # Green box for captured
                cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 3)
                cv2.putText(frame, "✓ CAPTURED!", (x, y-10),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
            else:
                # Yellow box while waiting
                cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 255), 2)
        
        # Show progress bar
        progress = (saved_count / required_images) * 100
        bar_width = 400
        bar_height = 30
        bar_x = 120
        bar_y = 20
        
        # Background
        cv2.rectangle(frame, (bar_x-5, bar_y-5), (bar_x+bar_width+5, bar_y+bar_height+5), 
                     (50, 50, 50), -1)
        
        # Progress bar
        progress_width = int((saved_count / required_images) * bar_width)
        cv2.rectangle(frame, (bar_x, bar_y), (bar_x+progress_width, bar_y+bar_height), 
                     (0, 255, 0), -1)
        
        # Border
        cv2.rectangle(frame, (bar_x, bar_y), (bar_x+bar_width, bar_y+bar_height), 
                     (255, 255, 255), 2)
        
        # Text
        progress_text = f"{saved_count}/{required_images} ({progress:.0f}%)"
        cv2.putText(frame, progress_text, (bar_x+bar_width//2-80, bar_y+22),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        
        # Student info
        cv2.putText(frame, f"Student: {name}", (10, 70),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        cv2.putText(frame, f"Roll No: {roll_no}", (10, 95),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        cv2.putText(frame, f"Class: {branch}-{section}", (10, 120),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        
        # Instructions
        if not face_detected:
            cv2.putText(frame, "⚠ NO FACE DETECTED - Please face the camera", 
                       (10, frame.shape[0] - 20), cv2.FONT_HERSHEY_SIMPLEX, 
                       0.6, (0, 0, 255), 2)
        else:
            cv2.putText(frame, "✓ Face detected - Keep moving slightly", 
                       (10, frame.shape[0] - 20), cv2.FONT_HERSHEY_SIMPLEX, 
                       0.6, (0, 255, 0), 2)
        
        cv2.imshow("Face Capture - Press Q to Quit", frame)
        
        # Exit on 'q'
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q') or key == ord('Q'):
            if saved_count < required_images:
                print(f"\n⚠️  Only {saved_count} images captured (need {required_images})")
                print("   This may affect recognition accuracy!")
                cont = input("   Continue anyway? (yes/no): ").strip().lower()
                if cont != 'yes':
                    print("❌ Capture cancelled")
                    cam.release()
                    cv2.destroyAllWindows()
                    return
            break
    
    cam.release()
    cv2.destroyAllWindows()
    
    # Save student information to database
    db[student_id] = {
        "name": name,
        "rollNo": roll_no,
        "branch": branch,
        "section": section,
        "imagesCount": saved_count,
        "registeredDate": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "datasetPath": dataset_path
    }
    
    save_student_database(db)
    
    print("\n" + "=" * 60)
    print("✅ FACE CAPTURE COMPLETED SUCCESSFULLY!")
    print("=" * 60)
    print(f"👤 Student Name: {name}")
    print(f"🎓 Roll Number: {roll_no}")
    print(f"🏢 Branch-Section: {branch}-{section}")
    print(f"📸 Images Captured: {saved_count}/{required_images}")
    print(f"📁 Dataset Path: {dataset_path}")
    print(f"💾 Database File: {STUDENT_DB}")
    print("=" * 60)
    print("\n🔄 NEXT STEPS:")
    print("  1. Capture more students if needed (run this script again)")
    print("  2. Train the model: python train_model.py")
    print("  3. Start attendance system from dashboard")
    print("=" * 60)

if __name__ == "__main__":
    try:
        capture_student_faces()
    except KeyboardInterrupt:
        print("\n\n❌ Capture cancelled by user (Ctrl+C)")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()