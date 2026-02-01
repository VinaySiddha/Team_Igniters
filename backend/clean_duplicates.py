"""
Duplicate Cleaner Tool
Removes duplicate attendance entries
"""

import csv
from datetime import datetime
from validators import remove_duplicate_entries, validate_csv_format

attendance_file = "attendance.csv"

print("=" * 60)
print("🧹 DUPLICATE CLEANER TOOL")
print("   Smart Attendance System")
print("=" * 60)

# Validate CSV format
is_valid, message = validate_csv_format(attendance_file)

if not is_valid:
    print(f"❌ {message}")
    exit(1)

print(f"✅ CSV format: {message}")
print()

# Read all records
with open(attendance_file, 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    records = list(reader)

print(f"📊 Total records: {len(records)}")

# Find duplicates
seen = {}
duplicates = []
unique_records = []

for record in records:
    key = (
        record['Name'],
        record['RollNo'],
        record['Date'],
        record['Branch'],
        record['Section']
    )
    
    if key in seen:
        duplicates.append(record)
    else:
        seen[key] = record
        unique_records.append(record)

print(f"📊 Duplicates found: {len(duplicates)}")
print(f"📊 Unique records: {len(unique_records)}")

if duplicates:
    print("\n🗑️  Duplicate Entries:")
    for dup in duplicates:
        print(f"   • {dup['Name']} ({dup['RollNo']}) on {dup['Date']} at {dup['Time']}")
    
    print()
    confirm = input("⚠️  Remove all duplicates? (yes/no): ").strip().lower()
    
    if confirm == 'yes':
        removed = remove_duplicate_entries(attendance_file, create_backup=True)
        print(f"\n✅ Cleaned! Removed {removed} duplicates")
        print(f"✅ {len(unique_records)} unique records remaining")
    else:
        print("❌ Cancelled - No changes made")
else:
    print("\n✅ No duplicates found! Database is clean.")

print("=" * 60)