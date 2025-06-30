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
    waiver = request.form.get("waiver") == "on"
    referral_source = request.form.get("referral_source")
    completed_by_first = request.form.get("completed_by_first")
    completed_by_last = request.form.get("completed_by_last")
    confirmation_email = request.form.get("confirmation_email")

    rows = []
    for i in range(children_count):
        prefix = f"child_{i}_"
        name = request.form.get(prefix + "name")
        address = request.form.get(prefix + "address")
        gender = request.form.get(prefix + "gender")
        birthdate = request.form.get(prefix + "birthdate")
        weeks = request.form.getlist(prefix + "weeks")
        friday = request.form.get(prefix + "friday")
        medical_number = request.form.get(prefix + "medical_number")
        immunizations = request.form.get(prefix + "immunizations")
        conditions = request.form.getlist(prefix + "conditions")
        conditions_other = request.form.get(prefix + "conditions_other")
        allergies = request.form.get(prefix + "allergies")
        support = request.form.get(prefix + "support")
        otc_permission = request.form.get(prefix + "otc_permission")
        emergency_name = request.form.get(prefix + "emergency_name")
        emergency_relationship = request.form.get(prefix + "emergency_relationship")
        emergency_phone = request.form.get(prefix + "emergency_phone")

        row = [
            parent_name, email, phone,
            name, address, gender, birthdate,
            "; ".join(weeks), friday, medical_number,
            immunizations, ", ".join(conditions), conditions_other,
            allergies, support, otc_permission,
            emergency_name, emergency_relationship, emergency_phone,
            waiver, referral_source,
            completed_by_first, completed_by_last, confirmation_email,
            datetime.now().isoformat()
        ]
        rows.append(row)

    file_exists = os.path.isfile(DATA_FILE)
    with open(DATA_FILE, "a", newline="") as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow([
                "Parent Name", "Email", "Phone",
                "Child Name", "Address", "Gender", "Birthdate",
                "Weeks", "Optional Friday", "Medical Number",
                "Immunizations", "Medical Conditions", "Other Condition Note",
                "Allergies", "Support Needs", "OTC Permission",
                "Emergency Contact", "Emergency Relationship", "Emergency Phone",
                "Waiver Signed", "Referral Source",
                "Completed By First", "Completed By Last", "Confirmation Email",
                "Timestamp"
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
    return f"<pre>{data}</pre>"

@app.route("/admin/download")
def admin_download():
    if not os.path.exists(DATA_FILE):
        return "No data."
    return send_file(DATA_FILE, as_attachment=True)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
