from flask import Flask, render_template, request, redirect, url_for, send_file
import csv
import os
from io import StringIO
from datetime import datetime

app = Flask(__name__)

ADMIN_PASSWORD = "loftadmin"
DATA_FILE = "registrations.csv"

@app.route("/")
def index():
    return render_template("form.html")

@app.route("/submit", methods=["POST"])
def submit():
    parent_name = request.form.get("parent_name")
    email = request.form.get("email")
    phone = request.form.get("phone")
    children_count = int(request.form.get("children_count"))
    waiver = request.form.get("waiver", "") == "on"

    rows = []
    for i in range(children_count):
        prefix = f"child_{i}_"
        name = request.form.get(prefix + "name")
        age = request.form.get(prefix + "age")
        emergency_contact = request.form.get(prefix + "emergency_contact")
        emergency_phone = request.form.get(prefix + "emergency_phone")
        allergies = request.form.get(prefix + "allergies")
        medical = request.form.get(prefix + "medical")
        weeks = request.form.getlist(prefix + "weeks")
        fridays = [key for key in request.form if key.startswith(prefix + "friday_") and request.form[key] == "on"]

        row = [
            parent_name, email, phone, name, age, emergency_contact, emergency_phone,
            allergies, medical, "; ".join(weeks), "; ".join(fridays), waiver,
            datetime.now().isoformat()
        ]
        rows.append(row)

    file_exists = os.path.isfile(DATA_FILE)
    with open(DATA_FILE, "a", newline="") as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow([
                "Parent Name", "Email", "Phone", "Child Name", "Age",
                "Emergency Contact", "Emergency Phone", "Allergies", "Medical",
                "Weeks", "Fridays", "Waiver Signed", "Timestamp"
            ])
        writer.writerows(rows)

    return render_template("thanks.html")

@app.route("/admin", methods=["GET", "POST"])
def admin():
    if request.method == "POST":
        password = request.form.get("password")
        if password == ADMIN_PASSWORD:
            return redirect(url_for("admin_view"))
        return render_template("admin_login.html", error="Invalid password")
    return render_template("admin_login.html")

@app.route("/admin/view")
def admin_view():
    if not os.path.exists(DATA_FILE):
        return "No registrations yet."
    with open(DATA_FILE, "r") as f:
        data = f.read()
    return render_template("admin.html", data=data)

@app.route("/admin/download")
def admin_download():
    if not os.path.exists(DATA_FILE):
        return "No data."
    with open(DATA_FILE, "r") as f:
        return send_file(DATA_FILE, as_attachment=True)

if __name__ == "__main__":
    app.run(debug=True)
