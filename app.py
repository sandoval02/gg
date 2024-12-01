import os
from flask import Flask, flash, jsonify, redirect, render_template, request, session, url_for
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()  # Initialize the SQLAlchemy instance
app = Flask(__name__, static_url_path='/static', static_folder='static')



import logging

logging.basicConfig(level=logging.INFO)

@app.before_request
def log_request_info():
    app.logger.info('Request Path: %s', request.path)
    
# Define the '/index' route outside of register_routes
@app.route('/index')
def index():
    return render_template("index.html")

def create_app():
    app.secret_key = os.getenv("SECRET_KEY", os.urandom(24))  # Use secret key from environment or random
    
    # Database configuration
    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv(
        "DATABASE_URL", 
        "postgresql://kupal_user:ZgdCyVqzqUSvGCoCFiR76DX54P4UrmLp@dpg-ct2qko5svqrc738f55m0-a.oregon-postgres.render.com/kupal"
    )
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.init_app(app)

    with app.app_context():
        db.create_all()  # Ensure database tables are created

    # Register routes (other routes)
    register_routes(app)
    return app

# Models
class User(db.Model):
    __tablename__ = 'users'
    user_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)


class DiaryEntry(db.Model):
    __tablename__ = 'diary_entries'
    entry_id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    content = db.Column(db.Text, nullable=False)
    mood = db.Column(db.String(50), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    user = db.relationship('User', backref='entries')


# Routes
def register_routes(app):
    @app.route('/home')
    def home():
        if 'user_id' not in session:
            flash("Please login to access this page", "warning")
            return redirect(url_for('login'))

        entries = DiaryEntry.query.filter_by(user_id=session['user_id']).all()  # Retrieve entries more efficiently
        return render_template('home.html', entries=entries)

    @app.route('/edit_entry/<int:entry_id>', methods=['GET', 'POST'])
    def edit_entry(entry_id):
        if 'user_id' not in session:
            flash("Please log in first.", "warning")
            return redirect(url_for('login'))

        entry = DiaryEntry.query.filter_by(entry_id=entry_id, user_id=session['user_id']).first()
        if not entry:
            flash("Entry not found or you don't have permission to edit it.", "danger")
            return redirect(url_for('home'))

        if request.method == 'POST':
            entry.title = request.form['title']
            entry.content = request.form['content']
            entry.mood = request.form['mood']
            db.session.commit()
            flash("Entry updated successfully!", "success")
            return redirect(url_for('home'))

        return render_template('edit.html', entry=entry)

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if request.method == 'POST':
            email = request.form['email']
            password = request.form['password']

            user = User.query.filter_by(email=email).first()
            if user and check_password_hash(user.password_hash, password):
                session['user_id'] = user.user_id
                session['username'] = user.username
                flash("Logged in successfully!", "success")
                return redirect(url_for('home'))
            else:
                flash("Invalid email or password", "danger")

        return render_template('index.html')

    @app.route('/signup', methods=['GET', 'POST'])
    def signup():
        if request.method == 'POST':
            name = request.form['name']
            email = request.form['email']
            password = request.form['password']

            if User.query.filter_by(email=email).first():
                flash("Email already registered. Please log in.", "danger")
                return redirect(url_for('login'))

            hashed_password = generate_password_hash(password)
            new_user = User(username=name, email=email, password_hash=hashed_password)
            db.session.add(new_user)
            db.session.commit()
            flash("Account created successfully! Please log in.", "success")
            return redirect(url_for('login'))

        return render_template('index.html')

    @app.route('/logout', methods=['POST'])
    def logout():
        session.clear()
        flash("You have been logged out successfully!", "success")
        return redirect(url_for('login'))

    @app.route('/new_entry', methods=['POST'])
    def new_entry():
        mood = request.form.get('mood')
        return render_template('entry.html', title="Untitled", mood=mood)

    @app.route('/save_entry', methods=['POST'])
    def save_entry():
        if 'user_id' not in session:
            flash("Please log in first.", "warning")
            return redirect(url_for('login'))

        title = request.form['title']
        content = request.form['content']
        mood = request.form['mood']
        user_id = session['user_id']

        new_entry = DiaryEntry(title=title, content=content, mood=mood, user_id=user_id)
        db.session.add(new_entry)
        db.session.commit()
        flash("Entry saved successfully!", "success")
        return redirect(url_for('home'))


    @app.errorhandler(404)
    def page_not_found(e):
        return render_template("404.html"), 404

    @app.errorhandler(500)
    def internal_error(e):
        db.session.rollback()  # Rollback the session in case of an error
        flash("An internal server error occurred. Please try again later.", "danger")
        return render_template("500.html"), 500


if __name__ == "__main__":
    app = create_app()
    port = int(os.environ.get("PORT", 5000))  # Get the port from the environment, default to 5000
    app.run(host="0.0.0.0", port=port, debug=True)  # Bind to all IPs, use dynamic port
    
    
app.run(debug=True)