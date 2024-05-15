from flask import Flask, render_template, request, redirect, url_for, session
import os
import pymysql
from werkzeug.utils import secure_filename
import fitz

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Folder to store uploaded files
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Database configuration
DB_HOST = 'localhost'
DB_USER = 'root'  # Change this if your XAMPP MySQL username is different
DB_PASSWORD = ''  # Change this if you have set a password for your XAMPP MySQL
DB_NAME = 'past_papersdb'

# Connect to the database
def connect_db():
    return pymysql.connect(host=DB_HOST, user=DB_USER, password=DB_PASSWORD, database=DB_NAME)

# Main page
@app.route('/main')
def main():
    if 'email' in session:  # Check if 'email' is in session
        # Retrieve user details from session
        user_email = session['email']
        db = connect_db()
        cursor = db.cursor()
        cursor.execute("SELECT name, email FROM users WHERE email = %s", (user_email,))
        user = cursor.fetchone()
        
        # Fetch papers uploaded by the user
        cursor.execute("SELECT * FROM papers WHERE uploaded_by = %s", (user_email,))
        papers = cursor.fetchall()
        
        db.close()

        if user:
            # Pass user details and papers to 'main.html'
            return render_template('main.html', user=user, papers=papers)
        else:
            return render_template('main.html', error='User not found')
    else:
        return redirect(url_for('login'))

# Login
@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        db = connect_db()
        cursor = db.cursor()
        cursor.execute("SELECT name, email FROM users WHERE email = %s AND password = %s", (email, password))
        user = cursor.fetchone()
        db.close()

        if user:
            # Store user's email and name in session
            session['email'] = user[1]  # Email is stored at index 1
            session['name'] = user[0]   # Name is stored at index 0
            return redirect(url_for('main'))  # Redirect to 'main' route after successful login
        else:
            return render_template('index.html', error='Invalid email or password')
    return render_template('index.html')

# Logout
@app.route('/logout')
def logout():
    session.pop('email', None)
    session.pop('name', None)
    return redirect(url_for('login'))

# Register user
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        name = request.form['name']
        phone = request.form['phone']
        email = request.form['email']
        password = request.form['password']

        db = connect_db()
        cursor = db.cursor()
        cursor.execute("INSERT INTO users (name, phone, email, password) VALUES (%s, %s, %s, %s)",
                       (name, phone, email, password))
        db.commit()
        db.close()

        return redirect(url_for('login'))
    return render_template('signup.html')

#Upload route
@app.route('/upload', methods=['POST'])
def upload_file():
    if 'email' in session:  # Check if user is logged in
        uploaded_file = request.files['file']
        if uploaded_file.filename != '':
            filename = secure_filename(uploaded_file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            uploaded_file.save(filepath)
            
            # Check if the uploaded file is a PDF
            # if not filename.lower().endswith('.pdf'):
                # os.remove(filepath)  # Remove the uploaded file
                # return render_template('main.html', error='Only PDF files are allowed')
            
            # Get additional form data
            unitCode = request.form['unitCode']
            unit_name = request.form['unitName']
            school = request.form['school']
            year = request.form['year']
            description = request.form['description']
            user_email = session['email']
            
            # Save file details in the database
            db = connect_db()
            cursor = db.cursor()
            cursor.execute("INSERT INTO papers (unitCode, unit_name, school, year, description, file_path, uploaded_by) VALUES (%s, %s, %s, %s, %s, %s, %s)",
                           (unitCode, unit_name, school, year, description, filepath, user_email))
            db.commit()
            db.close()
            
            return redirect(url_for('main'))
        else:
            return render_template('main.html', error='No file selected')
    else:
        return redirect(url_for('login'))
    
#Display Papers as cards in main.html
@app.route('/display_papers')
# from the paper data base get the file path





if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
