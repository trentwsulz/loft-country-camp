from flask import Flask, render_template, request, redirect, url_for
import pandas as pd
from fpdf import FPDF
import os

app = Flask(__name__)

# Path to the CSV file where registration data is stored
REGISTRATION_FILE = 'registrations.csv'

# Admin Login Route
@app.route('/admin', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        # Simple check for username and password (for demo purposes)
        if username == "admin" and password == "admin":
            return redirect(url_for('admin_panel'))
        else:
            return "Invalid credentials, please try again.", 403
    return render_template('admin_login.html')

# Admin Panel Route
@app.route('/admin/panel', methods=['GET', 'POST'])
def admin_panel():
    if request.method == 'POST':
        camper_name = request.form.get('camper_name')
        camp_type = request.form.get('camp_type')
        add_camper(camper_name, camp_type)
        return redirect(url_for('admin_panel'))

    # Display the current registrations in the admin panel
    registrations = pd.read_csv(REGISTRATION_FILE)
    return render_template('admin.html', registrations=registrations)

# Function to Add Camper
def add_camper(camper_name, camp_type):
    new_entry = pd.DataFrame({'camper_name': [camper_name], 'camp_type': [camp_type]})
    new_entry.to_csv(REGISTRATION_FILE, mode='a', header=False, index=False)

# Function to Generate PDF of Registrations
@app.route('/admin/generate_pdf', methods=['GET'])
def generate_pdf():
    registrations = pd.read_csv(REGISTRATION_FILE)
    pdf = FPDF()
    pdf.add_page()

    # Add title
    pdf.set_font('Arial', 'B', 16)
    pdf.cell(200, 10, txt="Camp Registrations", ln=True, align='C')

    # Add registration data
    pdf.set_font('Arial', '', 12)
    for index, row in registrations.iterrows():
        pdf.cell(200, 10, txt=f"{row['camper_name']} - {row['camp_type']}", ln=True)

    # Save PDF to a file
    pdf_output = 'registrations_report.pdf'
    pdf.output(pdf_output)

    return f"PDF Generated: <a href='{pdf_output}' download>Click here to download the PDF</a>"

# Run the app with correct host and port for deployment on Render
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
