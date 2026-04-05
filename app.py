from flask import Flask, render_template, request, redirect, session, url_for, flash
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
import base64
from datetime import datetime
from predict_logic import predict_image # Import the function
import pandas as pd

df = pd.read_csv('indian_food.csv')
app = Flask(__name__)
app.secret_key = "secret_food_key"

# Database Connection Helper
def get_db():
    conn = sqlite3.connect('food_app.db')
    conn.row_factory = sqlite3.Row
    return conn

# Database Table Setup
def init_db():
    with app.app_context():
        db = get_db()

        # Users table
        db.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                email TEXT NOT NULL,
                password TEXT NOT NULL
            )
        ''')

        # History table  ✅ ADD THIS
        db.execute('''
            CREATE TABLE IF NOT EXISTS history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL,
                dish_name TEXT NOT NULL,
                date TEXT NOT NULL,
                image_data TEXT
            )
        ''')

        db.commit()


@app.route('/')
def home():
    if 'username' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

# --- REGISTER ---
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = generate_password_hash(request.form['password'])

        try:
            db = get_db()
            db.execute('INSERT INTO users (username, email, password) VALUES (?, ?, ?)',
                       (username, email, password))
            db.commit()
            flash("Registration Successful! Please Login.", "success")
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            flash("Username already exists!", "danger")
            
    return render_template('register.html')

# --- LOGIN ---
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        db = get_db()
        user = db.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()

        if user and check_password_hash(user['password'], password):
            session['username'] = user['username']
            return redirect(url_for('dashboard'))
        else:
            flash("Invalid Username or Password", "danger")

    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if 'username' not in session:
        return redirect(url_for('login'))
    return render_template('dashboard.html', username=session['username'])

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))



@app.route('/history')
def history():
    if 'username' not in session: return redirect(url_for('login'))
    db = get_db()
    user_history = db.execute('SELECT * FROM history WHERE username = ? ORDER BY date DESC', (session['username'],)).fetchall()
    return render_template('history.html', history=user_history)


@app.route('/profile')
def profile():
    if 'username' not in session: return redirect(url_for('login'))
    return render_template('profile.html')

@app.route('/update_profile', methods=['POST'])
def update_profile():
    if 'username' not in session: return redirect(url_for('login'))
    
    new_password = request.form.get('new_password')
    if new_password:
        hashed_pw = generate_password_hash(new_password)
        db = get_db()
        db.execute('UPDATE users SET password = ? WHERE username = ?', (hashed_pw, session['username']))
        db.commit()
        flash("Password updated successfully!", "success")
    
    return redirect(url_for('profile'))

@app.route('/predict', methods=['POST'])
def predict():
    if 'username' not in session: return redirect(url_for('login'))
    
    img_bytes = None
    img_base64 = None

    if 'image_data' in request.form and request.form['image_data']:
        img_base64 = request.form['image_data']
        img_bytes = base64.b64decode(img_base64.split(",")[1])
    elif 'file' in request.files:
        file = request.files['file']
        if file.filename != '':
            img_bytes = file.read()
            img_base64 = "data:image/jpeg;base64," + base64.b64encode(img_bytes).decode('utf-8')

    if img_bytes:
        # 5 items return ho rahe hain
        dish, ingredients, desc, acc, nut_dict = predict_image(img_bytes)
        
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        db = get_db()
        db.execute(
    'INSERT INTO history (username, dish_name, date, image_data) VALUES (?, ?, ?, ?)', 
    (session['username'], dish, now, img_base64)
)

        db.commit()

        return render_template('result.html', 
                               dish=dish, 
                               ingredients=ingredients, 
                               desc=desc, 
                               accuracy=acc, 
                               nut=nut_dict, 
                               img_url=img_base64)
    
    return redirect(url_for('dashboard'))


@app.route('/view_result/<int:history_id>')
def view_result(history_id):
    if 'username' not in session:
        return redirect('/login')

    conn = get_db()
    record = conn.execute(
        "SELECT * FROM history WHERE id = ? AND username = ?",
        (history_id, session['username'])
    ).fetchone()
    conn.close()

    if record is None:
        return "Record not found", 404

    dish_name = record['dish_name']

    dish_row = df[df['name'] == dish_name]
    if dish_row.empty:
        return "Dish data not found in CSV", 404

    dish_data = dish_row.iloc[0]

    return render_template(
        'result.html',
        dish=dish_name,
        img_url=record['image_data'],
        accuracy="Saved",
        ingredients=dish_data['ingredients'],
        desc=dish_data.get('description', 'No description available'),
        nut={
            'calories': dish_data['calories_kcal'],
            'protein': dish_data['protein_g'],
            'carbs': dish_data['carbs_g'],
            'fat': dish_data['fat_g'],
            'sugar': dish_data['sugar_g'],
            'calcium': dish_data['calcium_mg'],
            'iron': dish_data['iron_mg'],
            'fiber': dish_data['fiber_g']
        }
    )


@app.route('/delete_account', methods=['POST'])
def delete_account():
    if 'username' in session:
        user = session['username']
        
        # 1. Database se user aur uski history delete karein
        # db.execute("DELETE FROM users WHERE username = ?", (user,))
        # db.execute("DELETE FROM history WHERE username = ?", (user,))
        
        # 2. Session clear karein
        session.clear()
        
        # 3. Message dikhayein aur home page par bhej dein
        flash("Your account has been successfully deleted.", "info")
        return redirect('/register')
    return redirect('/login')

if __name__ == '__main__':
    init_db()
    app.run(debug=True)