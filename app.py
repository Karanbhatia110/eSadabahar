from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, send_file
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_mail import Mail, Message
from datetime import datetime
import razorpay
import os
from dotenv import load_dotenv
import requests
from twilio.rest import Client

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///eSadabahar.db'
app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER')
app.config['MAIL_PORT'] = int(os.getenv('MAIL_PORT'))
app.config['MAIL_USE_TLS'] = os.getenv('MAIL_USE_TLS') == 'True'
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')

# Initialize extensions
db = SQLAlchemy(app)
login_manager = LoginManager(app)
mail = Mail(app)

# Razorpay client
razorpay_client = razorpay.Client(
    auth=(os.getenv('RAZORPAY_KEY_ID'), os.getenv('RAZORPAY_KEY_SECRET'))
)

# Twilio client
twilio_client = Client(
    os.getenv('TWILIO_ACCOUNT_SID'),
    os.getenv('TWILIO_AUTH_TOKEN')
)

# Models
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    price = db.Column(db.Float, nullable=False)
    description = db.Column(db.Text)
    image_url = db.Column(db.String(200))
    stock = db.Column(db.Integer, default=0)


class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    customer_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    address = db.Column(db.Text, nullable=False)
    pincode = db.Column(db.String(10), nullable=False)
    total_amount = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), default='pending')
    payment_status = db.Column(db.String(20), default='pending')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    items = db.relationship('OrderItem', backref='order', lazy=True)

class OrderItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Float, nullable=False)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Routes
@app.route('/')
def home():
    products = Product.query.all()
    return render_template('index.html', products=products)

@app.route('/cart')
def cart():
    return render_template('cart.html')

@app.route('/checkout', methods=['GET', 'POST'])
def checkout():
    if request.method == 'POST':
        try:
            data = request.get_json()
            
            # Create order
            order = Order(
                customer_name=data['name'],
                email=data['email'],
                phone=data['phone'],
                address=data['address'],
                pincode=data['pincode'],
                total_amount=float(data['total_amount'])
            )
            db.session.add(order)
            db.session.commit()

            # Add order items
            for item in data['items']:
                order_item = OrderItem(
                    order_id=order.id,
                    product_id=item['id'],
                    quantity=item['quantity'],
                    price=item['price']
                )
                db.session.add(order_item)
            db.session.commit()

            # Create Razorpay order
            razorpay_order = razorpay_client.order.create({
                'amount': int(order.total_amount * 100),  # Amount in paise
                'currency': 'INR',
                'receipt': f'order_{order.id}'
            })

            # Send email confirmation
            email_body = f"""
            Dear {order.customer_name},

            Thank you for your order! Your order has been received and is being processed.

            Order Details:
            Order ID: {order.id}
            Total Amount: ₹{order.total_amount}
            Delivery Address: {order.address}
            Pincode: {order.pincode}

            We will send you another email once your order is shipped.

            Best regards,
            eSadabahar Team
            """
            send_email(order.email, 'Order Confirmation - eSadabahar', email_body)

            # Send WhatsApp notification
            whatsapp_message = f"""
            🎉 Order Confirmation 🎉

            Dear {order.customer_name},

            Thank you for your order! Your order has been received and is being processed.

            Order Details:
            Order ID: {order.id}
            Total Amount: ₹{order.total_amount}
            Delivery Address: {order.address}
            Pincode: {order.pincode}

            We will keep you updated on your order status.

            Best regards,
            eSadabahar Team
            """
            send_whatsapp(order.phone, whatsapp_message)

            return jsonify({
                'order_id': razorpay_order['id'],
                'amount': razorpay_order['amount'],
                'currency': razorpay_order['currency'],
                'name': order.customer_name,
                'email': order.email,
                'phone': order.phone
            })
        except Exception as e:
            return jsonify({'error': str(e)}), 400

    # For GET requests, serve the static HTML file
    return send_file('templates/checkout.html')

@app.route('/admin')
@login_required
def admin():
    if not current_user.is_admin:
        return redirect(url_for('home'))
    orders = Order.query.order_by(Order.created_at.desc()).all()
    return render_template('admin/dashboard.html', orders=orders)

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        user = User.query.filter_by(username=request.form['username']).first()
        if user and user.password == request.form['password']:  # In production, use proper password hashing
            login_user(user)
            return redirect(url_for('admin'))
        flash('Invalid credentials')
    return render_template('admin/login.html')

@app.route('/admin/logout')
@login_required
def admin_logout():
    logout_user()
    return redirect(url_for('home'))

def send_email(to, subject, body):
    msg = Message(subject, sender=app.config['MAIL_USERNAME'], recipients=[to])
    msg.body = body
    mail.send(msg)

def send_whatsapp(to, message):
    twilio_client.messages.create(
        from_=f'whatsapp:{os.getenv("TWILIO_PHONE_NUMBER")}',
        body=message,
        to=f'whatsapp:{to}'
    )

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True) 