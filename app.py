import mysql.connector
import xlsxwriter
from flask import Flask, render_template, redirect, url_for, flash, request, session, send_file
from werkzeug.security import generate_password_hash, check_password_hash
import pandas as pd
import io

app = Flask(__name__)

# Secret key for session management
app.config['SECRET_KEY'] = 'your_secret_key'

# Connect to MySQL
def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="bakery_user",
        password="your_password",
        database="bakery_db"
    )

# Index route
@app.route('/')
def index():
    if 'username' in session:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM orders")
        orders = cursor.fetchall()
        cursor.close()
        conn.close()
        return render_template('index.html', orders=orders)
    return redirect(url_for('login'))

# Login route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
        user = cursor.fetchone()
        cursor.close()
        conn.close()

        if user and check_password_hash(user['password'], password):
            session['username'] = user['username']
            flash('Login successful!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Invalid username or password', 'danger')

    return render_template('login.html')

# Registration route
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = generate_password_hash(request.form['password'])

        conn = get_db_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, password))
            conn.commit()
            flash('Registration successful! Please log in.', 'success')
            return redirect(url_for('login'))
        except mysql.connector.IntegrityError:
            flash('Username already exists', 'danger')

        cursor.close()
        conn.close()

    return render_template('register.html')

# Logout route
@app.route('/logout')
def logout():
    session.pop('username', None)
    flash('You have been logged out.', 'success')
    return redirect(url_for('login'))

# Add order route
@app.route('/add_order', methods=['GET', 'POST'])
def add_order():
    if 'username' in session:
        if request.method == 'POST':
            customer_name = request.form['customer_name']
            item = request.form['item']
            quantity = request.form['quantity']
            price = request.form['price']

            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("INSERT INTO orders (customer_name, item, quantity, price) VALUES (%s, %s, %s, %s)", (customer_name, item, quantity, price))
            conn.commit()
            cursor.close()
            conn.close()

            flash('Order added successfully!', 'success')
            return redirect(url_for('index'))

        return render_template('add_order.html')
    return redirect(url_for('login'))

# Edit order route
@app.route('/edit_order/<int:order_id>', methods=['GET', 'POST'])
def edit_order(order_id):
    if 'username' in session:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        if request.method == 'POST':
            customer_name = request.form['customer_name']
            item = request.form['item']
            quantity = request.form['quantity']
            price = request.form['price']

            cursor.execute("UPDATE orders SET customer_name=%s, item=%s, quantity=%s, price=%s WHERE id=%s", (customer_name, item, quantity, price, order_id))
            conn.commit()
            cursor.close()
            conn.close()

            flash('Order updated successfully!', 'success')
            return redirect(url_for('index'))

        cursor.execute("SELECT * FROM orders WHERE id=%s", (order_id,))
        order = cursor.fetchone()
        cursor.close()
        conn.close()

        return render_template('edit_order.html', order=order)
    return redirect(url_for('login'))

# Delete order route
@app.route('/delete_order/<int:order_id>', methods=['POST'])
def delete_order(order_id):
    if 'username' in session:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("DELETE FROM orders WHERE id = %s", (order_id,))
        conn.commit()
        cursor.close()
        conn.close()

        flash('Order deleted successfully!', 'success')
        return redirect(url_for('index'))
    return redirect(url_for('login'))




# Export to Excel route
@app.route('/export')
def export():
    if 'username' in session:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM orders")
        orders = cursor.fetchall()

        # Create a DataFrame for orders
        df = pd.DataFrame(orders)

        # Convert DataFrame to Excel format
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df.to_excel(writer, sheet_name='Orders', index=False)

        output.seek(0)
        return send_file(output, as_attachment=True, download_name='orders.xlsx', mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')

    return redirect(url_for('login'))

# Run the app
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

