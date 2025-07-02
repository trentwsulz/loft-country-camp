@app.route('/')
def home():
    return render_template('home.html')  # Home page with the registration link

@app.route('/form', methods=['GET', 'POST'])
def form():
    if request.method == 'POST':
        camper_name = request.form['camper_name']
        camp_type = request.form['camp_type']
        add_camper(camper_name, camp_type)
        return redirect(url_for('thanks'))  # Redirect to thanks page after form submission
    return render_template('form.html')  # Show the registration form

@app.route('/thanks')
def thanks():
    return render_template('thanks.html')  # Show the thank you page after submission
