from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'

# Database initialization
def init_db():
    conn = sqlite3.connect('healthcare.db')
    cursor = conn.cursor()
    
    # Create users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create health details table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS health_details (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            age INTEGER,
            weight REAL,
            height REAL,
            blood_type TEXT,
            allergies TEXT,
            conditions TEXT,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    conn.commit()
    conn.close()

init_db()

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        conn = sqlite3.connect('healthcare.db')
        cursor = conn.cursor()
        cursor.execute('SELECT id, password FROM users WHERE email = ?', (email,))
        user = cursor.fetchone()
        conn.close()
        
        if user and check_password_hash(user[1], password):
            session['user_id'] = user[0]
            return redirect(url_for('home'))
        else:
            return render_template('login.html', error='Invalid credentials')
    
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        
        hashed_password = generate_password_hash(password)
        
        conn = sqlite3.connect('healthcare.db')
        cursor = conn.cursor()
        try:
            cursor.execute('INSERT INTO users (name, email, password) VALUES (?, ?, ?)', 
                          (name, email, hashed_password))
            conn.commit()
            user_id = cursor.lastrowid
            conn.close()
            
            session['user_id'] = user_id
            return redirect(url_for('health_details'))
        except sqlite3.IntegrityError:
            conn.close()
            return render_template('signup.html', error='Email already exists')
    
    return render_template('signup.html')

@app.route('/diet')
def diet():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('diet.html')

@app.route('/exercise')
def exercise():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('exercise.html')

@app.route('/health-details', methods=['GET', 'POST'])
def health_details():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user_id = session['user_id']
    
    if request.method == 'POST':
        age = request.form.get('age')
        weight = request.form.get('weight')
        height = request.form.get('height')
        blood_type = request.form.get('blood_type')
        allergies = request.form.get('allergies')
        conditions = request.form.get('conditions')
        
        conn = sqlite3.connect('healthcare.db')
        cursor = conn.cursor()
        
        # Check if health details already exist
        cursor.execute('SELECT id FROM health_details WHERE user_id = ?', (user_id,))
        existing = cursor.fetchone()
        
        if existing:
            cursor.execute('''
                UPDATE health_details SET 
                age = ?, weight = ?, height = ?, blood_type = ?, allergies = ?, conditions = ?
                WHERE user_id = ?
            ''', (age, weight, height, blood_type, allergies, conditions, user_id))
        else:
            cursor.execute('''
                INSERT INTO health_details 
                (user_id, age, weight, height, blood_type, allergies, conditions)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (user_id, age, weight, height, blood_type, allergies, conditions))
        
        conn.commit()
        conn.close()
        return redirect(url_for('home'))
    
    # GET request - load existing details
    conn = sqlite3.connect('healthcare.db')
    cursor = conn.cursor()
    cursor.execute('''
        SELECT age, weight, height, blood_type, allergies, conditions 
        FROM health_details WHERE user_id = ?
    ''', (user_id,))
    details = cursor.fetchone()
    conn.close()
    
    return render_template('health_details.html', details=details)

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)