import csv
import os
from datetime import datetime

print("=" * 60)
print("🔍 CSV DEBUG TOOL")
print("=" * 60)

attendance_file = "attendance.csv"

# Check if file exists
if not os.path.exists(attendance_file):
    print(f"❌ File '{attendance_file}' does not exist!")
    print(f"📁 Current directory: {os.getcwd()}")
    print(f"📁 Files in directory: {os.listdir('.')}")
    exit(1)

print(f"✅ File exists: {attendance_file}")
print(f"📁 File size: {os.path.getsize(attendance_file)} bytes")
print()

# Read and display CSV contents
print("📖 CSV CONTENTS:")
print("-" * 60)

with open(attendance_file, 'r', encoding='utf-8') as f:
    content = f.read()
    print(content)

print("-" * 60)
print()

# Parse CSV
with open(attendance_file, 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    
    print(f"📋 Headers: {reader.fieldnames}")
    print()
    
    today = datetime.now().strftime("%Y-%m-%d")
    print(f"📅 Today's date: {today}")
    print()
    
    print("📊 PARSED RECORDS:")
    print("-" * 60)
    
    records = list(reader)
    
    if not records:
        print("❌ No records found in CSV!")
    else:
        for i, row in enumerate(records, 1):
            print(f"Record {i}:")
            print(f"  Name: {row.get('Name', 'N/A')}")
            print(f"  Roll No: {row.get('RollNo', 'N/A')}")
            print(f"  Branch: {row.get('Branch', 'N/A')}")
            print(f"  Section: {row.get('Section', 'N/A')}")
            print(f"  Date: {row.get('Date', 'N/A')}")
            print(f"  Time: {row.get('Time', 'N/A')}")
            
            # Check if today
            is_today = (row.get('Date', '') == today)
            print(f"  Is Today: {is_today}")
            print()
    
    print("-" * 60)
    print(f"Total records: {len(records)}")
    
    # Count by date
    dates = {}
    for row in records:
        date = row.get('Date', 'Unknown')
        dates[date] = dates.get(date, 0) + 1
    
    print(f"\n📊 Records by date:")
    for date, count in dates.items():
        print(f"  {date}: {count} records")

print("=" * 60)