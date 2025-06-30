from flask import Flask, render_template, request, redirect, url_for, send_file
import csv
import os
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
    referral = request.form.get("referral_source")
    waiver = request.form.get("waiver") == "on"
    children_count = int(request.form.get("children_count"))

    rows = []
    for i in range(children_count):
        prefix = f"child_{i}_"
        child = {
            "Parent Name": parent_name,
            "Email": email,
            "Phone": phone,
            "Referral Source": referral,
            "Child Name": request.form.get(prefix + "name"),
            "Address": request.form.get(prefix + "address"),
            "Gender": request.form.get(prefix + "gender"),
            "Birthdate": request.form.get(prefix + "birthdate"),
            "Weeks": ", ".join(request.form.getlist(prefix + "weeks")),
            "Optional Friday": request.form.get(prefix + "friday"),
            "Medical Number": request.form.get(prefix + "medical_number"),
            "Immunizations": request.form.get(prefix + "immunizations"),
            "Medical Conditions": ", ".join(request.form.getlist(prefix + "medical_conditions")),
            "Other Condition": request.form.get(prefix + "medical_other"),
            "Allergies": request.form.get(prefix + "allergies"),
            "Support Needs": request.form.get(prefix + "support"),
            "OTC Permission": request.form.get(prefix + "otc_permission"),
            "Emergency Contact": request.form.get(prefix + "emergency_contact"),
            "Emergency Relation": request.form.get(prefix + "emergency_relation"),
            "Emergency Phone": request.form.get(prefix + "emergency_phone"),
            "Waiver Signed": waiver,
            "Timestamp": datetime.now().isoformat()
        }
        rows.append(child)

    file_exists = os.path.isfile(DATA_FILE)
    with open(DATA_FILE, "a", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        if not file_exists:
            writer.writeheader()
        writer.writerows(rows)

    return render_template("thanks.html")

@app.route("/admin", methods=["GET", "POST"])
def admin():
    if request.method == "POST":
        if request.form.get("password") == ADMIN_PASSWORD:
            return redirect(url_for("admin_view"))
        return render_template("admin_login.html", error="Invalid password")
    return render_template("admin_login.html")

@app.route("/admin/view")
def admin_view():
    if not os.path.exists(DATA_FILE):
        return "No registrations yet."
    with open(DATA_FILE, newline="") as f:
        reader = csv.reader(f)
        rows = list(reader)
    headers = rows[0]
    data = rows[1:]
    return render_template("admin.html", headers=headers, rows=data)

@app.route("/admin/download")
def admin_download():
    if not os.path.exists(DATA_FILE):
        return "No data available."
    return send_file(DATA_FILE, as_attachment=True)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
