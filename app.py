from flask import Flask, render_template, request, redirect, send_file
import sqlite3
import csv
import io
import os

app = Flask(__name__)
DB_FILE = "camp.db"
ADMIN_PASSWORD = "loftadmin"

def init_db():
    with sqlite3.connect(DB_FILE) as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS families (
                id INTEGER PRIMARY KEY,
                parent_name TEXT,
                email TEXT,
                phone TEXT
            )
        ''')
        conn.execute('''
            CREATE TABLE IF NOT EXISTS children (
                id INTEGER PRIMARY KEY,
                family_id INTEGER,
                name TEXT,
                age INTEGER,
                emergency_contact TEXT,
                emergency_phone TEXT,
                allergies TEXT,
                medical TEXT,
                camp_type TEXT
            )
        ''')
        conn.execute('''
            CREATE TABLE IF NOT EXISTS registrations (
                id INTEGER PRIMARY KEY,
                child_id INTEGER,
                week TEXT,
                add_friday BOOLEAN
            )
        ''')

@app.route('/')
def index():
    return render_template('form.html')

@app.route('/submit', methods=['POST'])
def submit():
    parent_name = request.form['parent_name']
    email = request.form['email']
    phone = request.form['phone']
    children_count = int(request.form['children_count'])

    with sqlite3.connect(DB_FILE) as conn:
        cur = conn.cursor()
        cur.execute("INSERT INTO families (parent_name, email, phone) VALUES (?, ?, ?)", (parent_name, email, phone))
        family_id = cur.lastrowid

        for i in range(children_count):
            prefix = f"child_{i}_"
            name = request.form[f"{prefix}name"]
            age = int(request.form[f"{prefix}age"])
            emergency_contact = request.form[f"{prefix}emergency_contact"]
            emergency_phone = request.form[f"{prefix}emergency_phone"]
            allergies = request.form.get(f"{prefix}allergies", "")
            medical = request.form.get(f"{prefix}medical", "")
            camp_type = request.form[f"{prefix}camp_type"]

            cur.execute('''
                INSERT INTO children (family_id, name, age, emergency_contact, emergency_phone, allergies, medical, camp_type)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (family_id, name, age, emergency_contact, emergency_phone, allergies, medical, camp_type))
            child_id = cur.lastrowid

            for week in request.form.getlist(f"{prefix}weeks"):
                add_friday = request.form.get(f"{prefix}friday_{week}", "off") == "on"
                cur.execute("INSERT INTO registrations (child_id, week, add_friday) VALUES (?, ?, ?)", (child_id, week, add_friday))

    return redirect("/thanks")

@app.route('/thanks')
def thanks():
    return render_template('thanks.html')

@app.route('/admin')
def admin_login():
    return render_template("admin_login.html")

@app.route('/admin/dashboard', methods=["POST"])
def admin_dashboard():
    if request.form["password"] != ADMIN_PASSWORD:
        return "Access Denied"
    with sqlite3.connect(DB_FILE) as conn:
        cur = conn.cursor()
        cur.execute('''
            SELECT f.parent_name, f.email, f.phone,
                   c.name, c.age, c.emergency_contact, c.emergency_phone,
                   c.allergies, c.medical, c.camp_type,
                   r.week, r.add_friday
            FROM families f
            JOIN children c ON f.id = c.family_id
            JOIN registrations r ON c.id = r.child_id
        ''')
        records = cur.fetchall()
    return render_template("admin.html", records=records)

@app.route('/admin/export', methods=["POST"])
def export_csv():
    if request.form["password"] != ADMIN_PASSWORD:
        return "Access Denied"
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Parent", "Email", "Phone", "Camper", "Age", "Emergency Contact", "Emergency Phone", "Allergies", "Medical", "Camp Type", "Week", "Friday?"])

    with sqlite3.connect(DB_FILE) as conn:
        cur = conn.cursor()
        cur.execute('''
            SELECT f.parent_name, f.email, f.phone,
                   c.name, c.age, c.emergency_contact, c.emergency_phone,
                   c.allergies, c.medical, c.camp_type,
                   r.week, r.add_friday
            FROM families f
            JOIN children c ON f.id = c.family_id
            JOIN registrations r ON c.id = r.child_id
        ''')
        for row in cur.fetchall():
            writer.writerow(row)

    output.seek(0)
    return send_file(io.BytesIO(output.getvalue().encode()), mimetype='text/csv', as_attachment=True, download_name="campers.csv")

if __name__ == '__main__':
    init_db()
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
