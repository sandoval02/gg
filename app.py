import os
from flask import Flask, flash, jsonify, redirect, render_template, request, session, url_for
import mysql.connector
from mysql.connector import Error

app = Flask(__name__)
application = app
app.secret_key = os.urandom(24)

def get_db_connection():
    try:
        conn = mysql.connector.connect(
            host="localhost",  
            user="root",       
            password="",       
            database="dairy"
        )
        print("Success")
        return conn
    except Error as e:
        print(f"Error connecting to MySQL: {e}")
        return None



@app.route('/')
def index():
    return render_template("index.html")



@app.route('/home')
def home():
    if 'user_id' not in session:
        flash("Please login to access this page", "warning")
        return redirect(url_for('login'))

    # Fetch the user's diary entries from the database
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM diary_entries WHERE user_id = %s", (session['user_id'],))
    entries = cursor.fetchall()
    conn.close()

    return render_template('home.html', entries=entries)



@app.route('/edit_entry/<int:entry_id>', methods=['GET', 'POST'])
def edit_entry(entry_id):
    # Ensure the user is logged in
    if 'user_id' not in session:
        flash("Please log in first.", "warning")
        return redirect(url_for('login'))

    # Get the entry details from the database based on entry_id
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM diary_entries WHERE entry_id = %s AND user_id = %s", (entry_id, session['user_id']))
    entry = cursor.fetchone()
    conn.close()

    if not entry:
        flash("Entry not found or you don't have permission to edit it.", "danger")
        return redirect(url_for('home'))

    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        mood = request.form['mood']

        # Update the entry in the database
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE diary_entries
            SET title = %s, content = %s, mood = %s
            WHERE entry_id = %s AND user_id = %s
        """, (title, content, mood, entry_id, session['user_id']))
        conn.commit()
        conn.close()

        flash("Entry updated successfully!", "success")
        return redirect(url_for('home'))

    return render_template('edit.html', entry=entry)




@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        # Database query
        conn = get_db_connection()
        if conn:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
            user = cursor.fetchone()
            conn.close()

            # Validate user credentials
            if user and user['password_hash'] == password:  # Directly comparing passwords
                # Set session
                session['user_id'] = user['user_id']
                session['username'] = user['username']
                flash("Logged in successfully!", "success")
                return redirect(url_for('home'))
            else:
                flash("Invalid email or password", "danger")

    return redirect(url_for('index'))



@app.route('/new_entry', methods=['POST'])
def new_entry():
    mood = request.form.get('mood')  # Get the mood value from the button
    return render_template('entry.html', title="Untitled", mood=mood)


@app.route('/save_entry', methods=['POST'])
def save_entry():
    # Ensure the user is logged in
    if 'user_id' not in session:
        flash("Please log in first.", "warning")
        return redirect(url_for('login'))

    # Get the user input and user_id from session
    title = request.form['title']
    content = request.form['content']
    mood = request.form['mood']
    user_id = session['user_id']  # Retrieve user_id from the session

    # Save the entry to the database (example using MySQL)
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # Insert diary entry with user_id
        cursor.execute("""
            INSERT INTO diary_entries (title, content, mood, user_id) 
            VALUES (%s, %s, %s, %s)
        """, (title, content, mood, user_id))
        
        conn.commit()
        flash("Entry saved successfully!", "success")
    except mysql.connector.Error as err:
        conn.rollback()  # Rollback in case of error
        flash(f"Error saving entry: {err}", "danger")
    finally:
        conn.close()

    return redirect(url_for('home'))


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']

        # Check if the email already exists
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
        existing_user = cursor.fetchone()
        conn.close()

        if existing_user:
            flash("Email already registered. Please log in.", "danger")
            return redirect(url_for('login'))  # Redirect to login if email exists

        # Directly store the password (NOT recommended for security)
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO users (username, email, password_hash)
                VALUES (%s, %s, %s)
            """, (name, email, password))  # Store plain text password (unsafe)
            conn.commit()
            flash("Account created successfully! Please log in.", "success")
            return redirect(url_for('login'))  # Redirect to login after successful signup
        except mysql.connector.Error as err:
            conn.rollback()
            flash(f"Error registering user: {err}", "danger")
        finally:
            conn.close()

    return render_template('index.html')  # Render the signup page if GET request

@app.route('/logout', methods=['POST'])
def logout():
    # Clear the session (logs the user out)
    session.clear()  # or session.pop('user_id', None) if you're tracking specific session variables
    flash("You have been logged out successfully!", "success")
    return redirect(url_for('login'))  # Redirect to login page


if __name__ == "__main__":
    app.run(debug=True)