from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Configure the SQLite database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///bakery.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Define User and Order models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), nullable=False, unique=True)
    password = db.Column(db.String(150), nullable=False)

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    customer_name = db.Column(db.String(150), nullable=False)
    order_item = db.Column(db.String(200), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String(50), nullable=False)

# Initialize the database
with app.app_context():
    db.create_all()

# Add the root route to redirect to login
@app.route('/')
def index():
    # If the user is already logged in, redirect to the order management page
    if 'user_id' in session:
        return redirect(url_for('order_management'))
    else:
        # If not logged in, redirect to the login page
        return redirect(url_for('login'))




# Routes for user registration
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = generate_password_hash(request.form['password'], method='sha256')
        
        new_user = User(username=username, password=password)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('register.html')

# Routes for user login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            return redirect(url_for('order_management'))
        return 'Invalid username or password'
    return render_template('login.html')

# Route for logging out
@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('login'))

# Route for managing orders
@app.route('/orders', methods=['GET', 'POST'])
def order_management():
    if 'user_id' in session:
        orders = Order.query.all()
        return render_template('orders.html', orders=orders)
    return redirect(url_for('login'))

# Route for adding a new order
@app.route('/add_order', methods=['GET', 'POST'])
def add_order():
    if 'user_id' not in session:
        return redirect(url_for('login'))
        
    if request.method == 'POST':
        customer_name = request.form['customer_name']
        order_item = request.form['order_item']
        quantity = request.form['quantity']
        status = request.form['status']
        
        new_order = Order(customer_name=customer_name, order_item=order_item, quantity=quantity, status=status)
        db.session.add(new_order)
        db.session.commit()
        return redirect(url_for('order_management'))
    return render_template('add_order.html')

# Route for editing an order
@app.route('/edit_order/<int:id>', methods=['GET', 'POST'])
def edit_order(id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
        
    order = Order.query.get_or_404(id)
    if request.method == 'POST':
        order.customer_name = request.form['customer_name']
        order.order_item = request.form['order_item']
        order.quantity = request.form['quantity']
        order.status = request.form['status']
        
        db.session.commit()
        return redirect(url_for('order_management'))
    return render_template('edit_order.html', order=order)

# Route for deleting an order
@app.route('/delete_order/<int:id>', methods=['POST'])
def delete_order(id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
        
    order = Order.query.get_or_404(id)
    db.session.delete(order)
    db.session.commit()
    return redirect(url_for('order_management'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

