"""
Validators Module - Duplicate Prevention & Data Validation
Smart Attendance System
"""

import csv
import os
from datetime import datetime

def is_duplicate_attendance(name, roll_no, branch, section, attendance_file):
    """
    Check if student attendance already exists for today
    
    Args:
        name: Student name
        roll_no: Student roll number
        branch: Branch (CSE, AIML, etc.)
        section: Section (A, B)
        attendance_file: Path to attendance CSV
    
    Returns:
        tuple: (is_duplicate: bool, existing_time: str or None)
    """
    if not os.path.exists(attendance_file):
        return False, None
    
    today = datetime.now().strftime("%Y-%m-%d")
    
    try:
        with open(attendance_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                row_name = row.get('Name', '').strip()
                row_roll = row.get('RollNo', '').strip()
                row_branch = row.get('Branch', '').strip()
                row_section = row.get('Section', '').strip()
                row_date = row.get('Date', '').strip()
                
                # Match by name, roll number, and date
                if (row_name == name and 
                    row_roll == roll_no and
                    row_branch == branch and 
                    row_section == section and
                    row_date == today):
                    return True, row.get('Time', '')
        
        return False, None
        
    except Exception as e:
        print(f"❌ Error checking duplicates: {e}")
        return False, None

def get_today_attendance_count(branch, section, attendance_file):
    """
    Get count of unique students marked today for a class
    
    Args:
        branch: Branch code
        section: Section code
        attendance_file: Path to CSV
    
    Returns:
        int: Number of students present today
    """
    if not os.path.exists(attendance_file):
        return 0
    
    today = datetime.now().strftime("%Y-%m-%d")
    marked_students = set()
    
    try:
        with open(attendance_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if (row.get('Branch', '') == branch and 
                    row.get('Section', '') == section and
                    row.get('Date', '') == today):
                    # Use name+roll as unique identifier
                    student_id = f"{row.get('Name', '')}_{row.get('RollNo', '')}"
                    marked_students.add(student_id)
        
        return len(marked_students)
        
    except Exception as e:
        print(f"❌ Error counting attendance: {e}")
        return 0

def remove_duplicate_entries(attendance_file, create_backup=True):
    """
    Remove duplicate entries from CSV keeping only first occurrence
    
    Args:
        attendance_file: Path to CSV file
        create_backup: Whether to create backup before cleaning
    
    Returns:
        int: Number of duplicates removed
    """
    if not os.path.exists(attendance_file):
        return 0
    
    try:
        # Read all records
        records = []
        with open(attendance_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            fieldnames = reader.fieldnames
            records = list(reader)
        
        if not records:
            return 0
        
        # Create backup if requested
        if create_backup:
            backup_file = f"attendance_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            with open(backup_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(records)
            print(f"💾 Backup created: {backup_file}")
        
        # Track unique entries (name, roll, date, branch, section)
        seen = set()
        unique_records = []
        duplicates_removed = 0
        
        for record in records:
            key = (
                record.get('Name', '').strip(),
                record.get('RollNo', '').strip(),
                record.get('Date', '').strip(),
                record.get('Branch', '').strip(),
                record.get('Section', '').strip()
            )
            
            if key not in seen:
                seen.add(key)
                unique_records.append(record)
            else:
                duplicates_removed += 1
                print(f"🗑️  Removing duplicate: {record.get('Name')} ({record.get('RollNo')}) "
                      f"on {record.get('Date')} at {record.get('Time')}")
        
        # Write back unique records only if duplicates were found
        if duplicates_removed > 0:
            with open(attendance_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(unique_records)
            
            print(f"✅ Removed {duplicates_removed} duplicate entries")
            print(f"✅ {len(unique_records)} unique records remaining")
        
        return duplicates_removed
        
    except Exception as e:
        print(f"❌ Error removing duplicates: {e}")
        import traceback
        traceback.print_exc()
        return 0

def validate_csv_format(attendance_file):
    """
    Validate that CSV has correct headers and format
    
    Returns:
        tuple: (is_valid: bool, message: str)
    """
    required_headers = ['Name', 'RollNo', 'Branch', 'Section', 'Date', 'Time']
    
    if not os.path.exists(attendance_file):
        return False, "File does not exist"
    
    try:
        with open(attendance_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            headers = reader.fieldnames
            
            if not headers:
                return False, "No headers found"
            
            missing = [h for h in required_headers if h not in headers]
            
            if missing:
                return False, f"Missing headers: {', '.join(missing)}"
            
            return True, "Valid format"
            
    except Exception as e:
        return False, f"Error reading file: {e}"

def get_student_attendance_history(name, roll_no, attendance_file, days=7):
    """
    Get attendance history for a student
    
    Args:
        name: Student name
        roll_no: Student roll number
        attendance_file: Path to CSV
        days: Number of recent days to fetch
    
    Returns:
        list: List of attendance records
    """
    if not os.path.exists(attendance_file):
        return []
    
    history = []
    
    try:
        with open(attendance_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if (row.get('Name', '') == name and 
                    row.get('RollNo', '') == roll_no):
                    history.append({
                        'date': row.get('Date', ''),
                        'time': row.get('Time', ''),
                        'branch': row.get('Branch', ''),
                        'section': row.get('Section', '')
                    })
        
        # Sort by date descending
        history.sort(key=lambda x: x['date'], reverse=True)
        
        return history[:days] if days else history
        
    except Exception as e:
        print(f"❌ Error fetching history: {e}")
        return []