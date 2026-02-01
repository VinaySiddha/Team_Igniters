import json
import os
from datetime import datetime

STUDENT_DB = "student_database.json"

def load_db():
    if os.path.exists(STUDENT_DB):
        with open(STUDENT_DB, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def save_db(db):
    with open(STUDENT_DB, 'w', encoding='utf-8') as f:
        json.dump(db, indent=4, fp=f)

def list_all_students():
    """List all registered students"""
    db = load_db()
    
    if not db:
        print("\n📭 No students registered yet.")
        return
    
    print("\n" + "=" * 90)
    print("📚 REGISTERED STUDENTS DATABASE")
    print("=" * 90)
    print(f"{'Name':<25} {'Roll No':<15} {'Branch':<8} {'Sec':<5} {'Images':<8} {'Date':<20}")
    print("-" * 90)
    
    for student_id, info in sorted(db.items()):
        print(f"{info['name']:<25} {info['rollNo']:<15} {info['branch']:<8} "
              f"{info['section']:<5} {info.get('imagesCount', 0):<8} "
              f"{info.get('registeredDate', 'N/A'):<20}")
    
    print("=" * 90)
    print(f"Total Students: {len(db)}")
    print("=" * 90)

def list_by_class():
    """List students by class"""
    db = load_db()
    
    if not db:
        print("\n📭 No students registered yet.")
        return
    
    branch = input("\nEnter branch (CSE/AIML/ECE/EEE/MECH/CIVIL): ").strip().upper()
    section = input("Enter section (A/B): ").strip().upper()
    
    students = [info for info in db.values() 
                if info.get('branch') == branch and info.get('section') == section]
    
    if not students:
        print(f"\n📭 No students found for {branch}-{section}")
        return
    
    print(f"\n📚 Students in {branch}-{section}")
    print("=" * 60)
    
    for i, info in enumerate(sorted(students, key=lambda x: x['rollNo']), 1):
        print(f"{i}. {info['name']} ({info['rollNo']}) - {info.get('imagesCount', 0)} images")
    
    print("=" * 60)
    print(f"Total: {len(students)} students")

def search_student():
    """Search for a specific student"""
    db = load_db()
    
    search = input("\nEnter name or roll number to search: ").strip().lower()
    
    found = []
    for student_id, info in db.items():
        if (search in info['name'].lower() or 
            search in info.get('rollNo', '').lower()):
            found.append(info)
    
    if found:
        print(f"\n✅ Found {len(found)} student(s):")
        print("-" * 60)
        for info in found:
            print(f"👤 Name: {info['name']}")
            print(f"🎓 Roll No: {info['rollNo']}")
            print(f"🏢 Class: {info['branch']}-{info['section']}")
            print(f"📸 Images: {info.get('imagesCount', 0)}")
            print(f"📅 Registered: {info.get('registeredDate', 'N/A')}")
            print(f"📁 Path: {info.get('datasetPath', 'N/A')}")
            print("-" * 60)
    else:
        print("❌ No students found")

def delete_student():
    """Delete a student from database"""
    db = load_db()
    
    search = input("\nEnter name of student to delete: ").strip().lower()
    student_id = search.replace(" ", "_")
    
    if student_id in db:
        info = db[student_id]
        print(f"\n⚠️  Found student:")
        print(f"   Name: {info['name']}")
        print(f"   Roll No: {info['rollNo']}")
        print(f"   Class: {info['branch']}-{info['section']}")
        
        confirm = input("\n⚠️  Are you sure you want to delete? (yes/no): ").strip().lower()
        
        if confirm == 'yes':
            del db[student_id]
            save_db(db)
            print("✅ Student deleted from database")
            print("⚠️  Note: Dataset folder not deleted. Delete manually if needed.")
        else:
            print("❌ Deletion cancelled")
    else:
        print("❌ Student not found")

def export_to_csv():
    """Export database to CSV"""
    db = load_db()
    
    if not db:
        print("\n📭 No students to export")
        return
    
    import csv
    filename = f"student_database_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['Name', 'Roll No', 'Branch', 'Section', 'Images', 'Registered Date', 'Dataset Path'])
        
        for info in db.values():
            writer.writerow([
                info['name'],
                info['rollNo'],
                info['branch'],
                info['section'],
                info.get('imagesCount', 0),
                info.get('registeredDate', 'N/A'),
                info.get('datasetPath', 'N/A')
            ])
    
    print(f"\n✅ Database exported to: {filename}")

def main():
    while True:
        print("\n" + "=" * 60)
        print("📚 STUDENT MANAGEMENT SYSTEM")
        print("=" * 60)
        print("1. List all students")
        print("2. List students by class")
        print("3. Search student")
        print("4. Delete student")
        print("5. Export to CSV")
        print("6. Exit")
        print("=" * 60)
        
        choice = input("\nEnter choice (1-6): ").strip()
        
        if choice == '1':
            list_all_students()
        elif choice == '2':
            list_by_class()
        elif choice == '3':
            search_student()
        elif choice == '4':
            delete_student()
        elif choice == '5':
            export_to_csv()
        elif choice == '6':
            print("\n👋 Goodbye!")
            break
        else:
            print("\n❌ Invalid choice! Please enter 1-6")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye!")