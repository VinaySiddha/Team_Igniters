from flask import Flask, jsonify, send_file, request
from flask_cors import CORS
import csv
import os
from datetime import datetime
import sys
import threading
import time

app = Flask(__name__)
CORS(app)

# Global variable to track attendance status
attendance_running = False
attendance_thread = None

@app.route("/")
def home():
    return jsonify({
        "message": "Smart Attendance Backend Running",
        "status": "active"
    })

# Get today's attendance with branch and section filter
@app.route("/api/attendance/today", methods=['GET'])
def get_today_attendance():
    try:
        branch = request.args.get('branch', '')
        section = request.args.get('section', '')
        
        print(f"📊 Loading attendance for: {branch}-{section}")
        
        attendance_file = "attendance.csv"
        today = str(datetime.now().date())
        
        records = []
        present_count = 0
        total_students = 60
        
        if os.path.exists(attendance_file):
            with open(attendance_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    row_date = str(row.get('Date', '')).strip()
                    row_branch = str(row.get('Branch', '')).strip()
                    row_section = str(row.get('Section', '')).strip()
                    
                    if (row_date == today and 
                        row_branch == branch and 
                        row_section == section):
                        
                        records.append({
                            'name': row.get('Name', 'Unknown'),
                            'rollNo': row.get('RollNo', '--'),
                            'date': row.get('Date', ''),
                            'time': row.get('Time', '')
                        })
                        present_count += 1
        
        print(f"✅ Found {present_count} records for {branch}-{section}")
        
        return jsonify({
            "success": True,
            "data": {
                "total": total_students,
                "present": present_count,
                "records": records
            }
        })
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

# Start attendance recognition
@app.route("/api/attendance/start", methods=['POST'])
def start_attendance():
    global attendance_running, attendance_thread
    
    try:
        data = request.json
        branch = data.get('branch', '')
        section = data.get('section', '')
        
        print(f"🎯 Start request - Branch: '{branch}', Section: '{section}'")
        
        if not branch or not section:
            return jsonify({
                "success": False,
                "message": "Branch and Section required"
            }), 400
        
        if attendance_running:
            return jsonify({
                "success": False,
                "message": "Attendance system already running"
            }), 400
        
        # Create a batch file to run the script
        batch_content = f"""@echo off
cd /d "{os.getcwd()}"
python recognize_attendance.py {branch} {section}
"""
        
        batch_file = "run_attendance.bat"
        with open(batch_file, 'w') as f:
            f.write(batch_content)
        
        print(f"✅ Created batch file: {batch_file}")
        
        # Run the batch file in a new window
        import subprocess
        
        if sys.platform == 'win32':
            # Windows - open new command window
            subprocess.Popen(
                ['cmd', '/c', 'start', 'cmd', '/k', batch_file],
                creationflags=subprocess.CREATE_NEW_CONSOLE
            )
        else:
            # Linux/Mac
            subprocess.Popen(['python', 'recognize_attendance.py', branch, section])
        
        attendance_running = True
        
        print(f"✅ Started attendance for {branch}-{section}")
        
        return jsonify({
            "success": True,
            "message": f"Attendance started for {branch}-{section}. Check the new window!"
        })
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

# Stop attendance
@app.route("/api/attendance/stop", methods=['POST'])
def stop_attendance():
    global attendance_running
    
    try:
        attendance_running = False
        
        print("⏹️ Attendance stopped (close the camera window manually)")
        
        return jsonify({
            "success": True,
            "message": "Attendance stopped. Please close the camera window."
        })
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

# Export attendance as CSV
@app.route("/api/attendance/export", methods=['GET'])
def export_attendance():
    try:
        branch = request.args.get('branch', '')
        section = request.args.get('section', '')
        
        attendance_file = "attendance.csv"
        
        if not os.path.exists(attendance_file):
            return jsonify({
                "success": False,
                "error": "Attendance file not found"
            }), 404
        
        # Create filtered CSV
        filtered_file = f"attendance_{branch}_{section}_{datetime.now().strftime('%Y%m%d')}.csv"
        
        with open(attendance_file, 'r', encoding='utf-8') as infile:
            reader = csv.DictReader(infile)
            
            with open(filtered_file, 'w', newline='', encoding='utf-8') as outfile:
                fieldnames = reader.fieldnames
                writer = csv.DictWriter(outfile, fieldnames=fieldnames)
                writer.writeheader()
                
                for row in reader:
                    if row.get('Branch', '') == branch and row.get('Section', '') == section:
                        writer.writerow(row)
        
        return send_file(
            filtered_file,
            mimetype='text/csv',
            as_attachment=True,
            download_name=f'attendance_{branch}_{section}_{datetime.now().strftime("%Y%m%d")}.csv'
        )
        
    except Exception as e:
        print(f"❌ Export error: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

if __name__ == "__main__":
    print("🚀 Starting Smart Attendance Backend...")
    print(f"📁 Working directory: {os.getcwd()}")
    print(f"🐍 Python: {sys.executable}")
    print("=" * 60)
    app.run(debug=True, host='0.0.0.0', port=5000, use_reloader=False)