from flask import Flask, render_template, request, redirect, url_for, send_file
import csv, os
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

    file_exists = os.path.exists(DATA_FILE)
    with open(DATA_FILE, "a", newline="") as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow([
                "Timestamp", "Parent Name", "Email", "Phone", "Referral Source", "Waiver",
                "Child Name", "Address", "Gender", "Birthdate", "Weeks", "Friday",
                "Medical Number", "Immunizations", "Medical Conditions", "Medical Other",
                "Allergies", "Support", "OTC Permission",
                "Emergency Contact", "Relationship", "Emergency Phone"
            ])
        for i in range(children_count):
            prefix = f"child_{i}_"
            row = [
                datetime.now().isoformat(), parent_name, email, phone, referral, waiver,
                request.form.get(prefix + "name"),
                request.form.get(prefix + "address"),
                request.form.get(prefix + "gender"),
                request.form.get(prefix + "birthdate"),
                "; ".join(request.form.getlist(prefix + "weeks")),
                request.form.get(prefix + "friday"),
                request.form.get(prefix + "medical_number"),
                request.form.get(prefix + "immunizations"),
                "; ".join(request.form.getlist(prefix + "medical_conditions")),
                request.form.get(prefix + "medical_other"),
                request.form.get(prefix + "allergies"),
                request.form.get(prefix + "support"),
                request.form.get(prefix + "otc_permission"),
                request.form.get(prefix + "emergency_contact"),
                request.form.get(prefix + "emergency_relation"),
                request.form.get(prefix + "emergency_phone")
            ]
            writer.writerow(row)
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
    with open(DATA_FILE, "r") as f:
        lines = list(csv.reader(f))
    return render_template("admin.html", headers=lines[0], rows=lines[1:])

@app.route("/admin/download")
def admin_download():
    if not os.path.exists(DATA_FILE):
        return "No data."
    return send_file(DATA_FILE, as_attachment=True)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
