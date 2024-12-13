from flask import Flask, render_template, request, redirect, flash, url_for
import sqlite3
from datetime import datetime
from datetime import datetime, timezone
import time as t

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Used for flashing messages

# Database initialization
DATABASE = 'database.db'
per_page = 10  # Number of logs per page

def init_db():
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS ate_logbook (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                logged_at TEXT,
                date TEXT,
                time TEXT,
                location TEXT,
                initials TEXT,
                remarks TEXT
            )
        ''')
        conn.commit()

def get_logs_n_pagination_data():
    page = request.args.get('page', 1, type=int)
    offset = (page - 1) * per_page

    # Fetch data from the database with pagination
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT id, logged_at, date, time, location, initials, remarks
            FROM ate_logbook ORDER BY id DESC 
            LIMIT ? OFFSET ?
        ''', (per_page, offset))
        logs = cursor.fetchall()

        # Get total count for pagination
        cursor.execute('SELECT COUNT(*) FROM ate_logbook')
        total_logs = cursor.fetchone()[0]

    # Calculate total pages
    total_pages = (total_logs + per_page - 1) // per_page
    return logs, page, total_pages

@app.route('/', methods=['GET'])
def index():
        return redirect('/new_log')

@app.route('/new_log', methods=['GET', 'POST'])
def new_log():
    if request.method == 'POST':
        logged_at = str(int(t.time()))
        date = request.form.get('date')
        time = request.form.get('time')
        location = request.form.get('location')
        initials = request.form.get('initials')
        remarks = request.form.get('remarks')

        # Validation
        if not all([date, time, location, initials, remarks]):
            flash('All fields are required!', 'error')
            return redirect('/new_log')

        # Save to database
        with sqlite3.connect(DATABASE) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO ate_logbook (logged_at, date, time, location, initials, remarks)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (logged_at, date, time, location, initials, remarks))
            conn.commit()

        flash('Log saved successfully!', 'success')
        return redirect('/new_log')

    # Default data for date and UTC time
    current_date = datetime.now(timezone.utc).strftime('%Y-%m-%d')
    current_utc_time = datetime.now(timezone.utc).strftime('%H:%M')  # Ensure 24-hour format
    locations = ["Equipment Room (ESB)", "Flight Ops. Com Room", "GP SHELTER", "DVOR SHELTER", "RX SHELTER", "LLZ SHELTER", "ATE Workshop", "ATE Store Room", "Eng. Mon Room", "Equipment Room (New ATCT)", "ACR", "VCR", "Tape Recording Room", "Operation Office (G 121)", "Police Operation Room G 135", "RADIO ROOM 705", "GS 00", "GS 01", "GS 02", "GS 03", "GS 04", "GS 05", "GS 06", "ARFF Sub Station 1", "ARFF Sub Station 2", "ARFF Main Station", "Logistics Link", "NA"]
    initials = ['MO-1829', 'RP-1831', 'AM-1865', 'SM-1913', 'BJ-1914', 'SS-1962', 'MH-1963', 'AA-1974', 'AB-2008', 'BJ-2059', 'PT-2003', 'HA-1749']

    logs, page, total_pages = get_logs_n_pagination_data()

    return render_template('new_log.html', date=current_date, time=current_utc_time, initials=initials, locations=locations, logs=logs, page=page, total_pages=total_pages)

@app.route('/ate_logs', methods=['GET'])
def ate_logs():
    page = request.args.get('page', 1, type=int)
    offset = (page - 1) * per_page

    # Fetch data from the database with pagination
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT id, logged_at, date, time, location, initials, remarks
            FROM ate_logbook ORDER BY id DESC 
            LIMIT ? OFFSET ?
        ''', (per_page, offset))
        logs = cursor.fetchall()

        # Get total count for pagination
        cursor.execute('SELECT COUNT(*) FROM ate_logbook')
        total_logs = cursor.fetchone()[0]

    # Calculate total pages
    total_pages = (total_logs + per_page - 1) // per_page

    return render_template('ate_logs.html', logs=logs, page=page, total_pages=total_pages)

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
