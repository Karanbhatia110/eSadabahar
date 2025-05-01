from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, send_file, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_mail import Mail, Message
from datetime import datetime, timedelta
import razorpay
import os
from dotenv import load_dotenv
import requests
from twilio.rest import Client
from werkzeug.security import generate_password_hash, check_password_hash
import time
import pytz

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///eSadabahar.db'
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
app.config['MAIL_DEFAULT_SENDER'] = os.getenv('MAIL_USERNAME')
app.config['MAIL_MAX_EMAILS'] = 10  # Limit number of emails per connection
app.config['MAIL_ASCII_ATTACHMENTS'] = False
app.config['MAIL_DEBUG'] = True  # Enable debug mode for development
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=30)  # Session timeout

# Initialize extensions
db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'admin_login'
login_manager.login_message = 'Please log in to access this page.'
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

# Set the timezone to IST
ist = pytz.timezone('Asia/Kolkata')

# Models
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

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
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(ist))
    delivery_date = db.Column(db.Date, nullable=False)
    items = db.relationship('OrderItem', backref='order', lazy=True)

class OrderItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Float, nullable=False)
    product = db.relationship('Product', backref='order_items', lazy=True)

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
    try:
        if request.method == 'GET':
            return render_template('checkout.html')
            
        if request.is_json:
            data = request.get_json()
        else:
            data = request.form.to_dict()
            # Convert amount to float if it's a string
            if 'total_amount' in data:
                data['amount'] = float(data['total_amount'])
        
        # Validate required fields
        required_fields = ['name', 'email', 'phone', 'address', 'pincode', 'amount', 'delivery_date', 'items']
        missing_fields = [field for field in required_fields if not data.get(field)]
        if missing_fields:
            return jsonify({
                'success': False,
                'message': f'Missing required fields: {", ".join(missing_fields)}'
            }), 400
        
        # Create order in database
        order = Order(
            customer_name=data['name'],
            email=data['email'],
            phone=data['phone'],
            address=data['address'],
            pincode=data['pincode'],
            total_amount=float(data['amount']),
            status='pending',
            payment_status='pending',
            delivery_date=datetime.strptime(data['delivery_date'], '%Y-%m-%d').date()
        )
        db.session.add(order)
        db.session.commit()

        # Create order items
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
            'amount': int(float(data['amount']) * 100),  # Convert to paise
            'currency': 'INR',
            'receipt': f'order_{order.id}',
            'notes': {
                'order_id': order.id
            }
        })

        return jsonify({
            'success': True,
            'order_id': order.id,
            'razorpay_order_id': razorpay_order['id'],
            'amount': razorpay_order['amount'],
            'currency': razorpay_order['currency'],
            'name': order.customer_name,
            'email': order.email,
            'phone': order.phone,
            'razorpay_key': os.getenv('RAZORPAY_KEY_ID')
        })

    except Exception as e:
        app.logger.error(f"Checkout error: {str(e)}")
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/admin')
@login_required
def admin():
    if not current_user.is_admin:
        return redirect(url_for('home'))
    orders = Order.query.order_by(Order.created_at.desc()).all()
    # Convert order creation time to IST for display
    for order in orders:
        order.created_at = order.created_at.astimezone(ist)
    return render_template('admin/dashboard.html', orders=orders)

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        try:
            data = request.json  # Use request.json to handle JSON data
            username = data.get('username')
            password = data.get('password')
            
            if not username or not password:
                return jsonify({
                    'success': False,
                    'message': 'Username and password are required'
                }), 400
            
            # Get user from database
            user = User.query.filter_by(username=username).first()
            
            if not user or not user.check_password(password):
                return jsonify({
                    'success': False,
                    'message': 'Invalid username or password'
                }), 401
            
            if not user.is_admin:
                return jsonify({
                    'success': False,
                    'message': 'Access denied. Admin privileges required.'
                }), 403
            
            # Login successful
            login_user(user)
            return jsonify({
                'success': True,
                'redirect': url_for('admin')
            })
            
        except Exception as e:
            app.logger.error(f'Login error: {str(e)}')
            return jsonify({
                'success': False,
                'message': f'An error occurred during login: {str(e)}'
            }), 500
    
    return render_template('admin/login.html')

@app.route('/admin/logout')
@login_required
def admin_logout():
    logout_user()
    return redirect(url_for('home'))

@app.route('/api/products')
def get_products():
    products = Product.query.all()
    return jsonify([{
        'id': product.id,
        'name': product.name,
        'category': product.category,
        'price': product.price,
        'description': product.description,
        'image_url': product.image_url,
        'stock': product.stock
    } for product in products])

def get_email_template(template_name, **kwargs):
    templates = {
        'order_confirmation': """
        <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                    <h2 style="color: #4a90e2;">Order Confirmation - eSadabahar</h2>
                    <p>Dear {customer_name},</p>
                    <p>Thank you for your order! Your order has been received and is being processed.</p>
                    
                    <div style="background-color: #f9f9f9; padding: 15px; border-radius: 5px; margin: 20px 0;">
                        <h3 style="color: #4a90e2;">Order Details:</h3>
                        <p><strong>Order ID:</strong> {order_id}</p>
                        <p><strong>Total Amount:</strong> ₹{total_amount}</p>
                        <p><strong>Delivery Address:</strong> {address}</p>
                        <p><strong>Pincode:</strong> {pincode}</p>
                        <p><strong>Delivery Date:</strong> {delivery_date}</p>
                    </div>
                    
                    <p>We will keep you updated on your order status.</p>
                    <p>Best regards,<br>eSadabahar Team</p>
                </div>
            </body>
        </html>
        """,
        'order_cancellation': """
        <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                    <h2 style="color: #e24a4a;">Order Cancelled - eSadabahar</h2>
                    <p>Dear {customer_name},</p>
                    <p>Your order #{order_id} has been cancelled.</p>
                    
                    <div style="background-color: #f9f9f9; padding: 15px; border-radius: 5px; margin: 20px 0;">
                        <h3 style="color: #e24a4a;">Order Details:</h3>
                        <p><strong>Products:</strong> {products}</p>
                        <p><strong>Total Amount:</strong> ₹{total_amount}</p>
                        <p><strong>Delivery Address:</strong> {address}</p>
                        <p><strong>Pincode:</strong> {pincode}</p>
                        <p><strong>Delivery Date:</strong> {delivery_date}</p>
                    </div>
                    
                    <p>If you have any questions, please contact us.</p>
                    <p>Best regards,<br>eSadabahar Team</p>
                </div>
            </body>
        </html>
        """
    }
    return templates.get(template_name, '').format(**kwargs)

def send_email(to, subject, body, html=None):
    """
    Send an email with retry mechanism and detailed logging.
    
    Args:
        to (str): Recipient email address
        subject (str): Email subject
        body (str): Email body text
        html (str, optional): HTML content for the email
    
    Returns:
        bool: True if email was sent successfully, False otherwise
    """
    max_retries = 3
    retry_delay = 2  # seconds
    
    # Validate email configuration
    if not app.config['MAIL_USERNAME'] or not app.config['MAIL_PASSWORD']:
        app.logger.error("Email configuration is incomplete. MAIL_USERNAME and MAIL_PASSWORD must be set.")
        return False
    
    for attempt in range(max_retries):
        try:
            msg = Message(
                subject=subject,
                recipients=[to],
                body=body,
                html=html,
                sender=app.config['MAIL_DEFAULT_SENDER']
            )
            
            app.logger.info(f"Attempting to send email to {to} (attempt {attempt + 1}/{max_retries})")
            mail.send(msg)
            
            app.logger.info(f"Email sent successfully to {to}")
            app.logger.debug(f"Email details - Subject: {subject}, Recipient: {to}")
            return True
            
        except Exception as e:
            error_msg = f"Failed to send email to {to} (attempt {attempt + 1}/{max_retries}): {str(e)}"
            app.logger.error(error_msg)
            
            if attempt < max_retries - 1:
                app.logger.info(f"Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
            else:
                app.logger.error(f"All {max_retries} attempts to send email to {to} failed")
                return False
    
    return False

def send_whatsapp(to, message):
    twilio_client.messages.create(
        from_=f'whatsapp:{os.getenv("TWILIO_PHONE_NUMBER")}',
        body=message,
        to=f'whatsapp:{to}'
    )

@app.route('/verify-payment', methods=['POST'])
def verify_payment():
    try:
        data = request.get_json()
        
        # Verify payment signature
        razorpay_client.utility.verify_payment_signature({
            'razorpay_order_id': data['razorpay_order_id'],
            'razorpay_payment_id': data['razorpay_payment_id'],
            'razorpay_signature': data['razorpay_signature']
        })
        
        # Update order status
        order = Order.query.filter_by(id=data['order_id']).first()
        if order:
            order.payment_status = 'completed'
            order.status = 'processing'
            db.session.commit()
            
            # Get order items for email
            order_items = OrderItem.query.filter_by(order_id=order.id).all()
            product_details = []
            for item in order_items:
                product = Product.query.get(item.product_id)
                if product:
                    product_details.append(f"{product.name} (Qty: {item.quantity})")
            
            # Send email confirmation to customer
            customer_email_body = f"""
            Dear {order.customer_name},

            Your payment has been successfully processed, and your order is now confirmed.

            Order Details:
            Order ID: {order.id}
            Products: {', '.join(product_details) if product_details else 'No products found'}
            Total Amount: ₹{order.total_amount}
            Delivery Address: {order.address}
            Pincode: {order.pincode}
            Delivery Date: {order.delivery_date.strftime('%d-%m-%Y')}

            Thank you for shopping with us!

            Best regards,
            eSadabahar Team
            """
            send_email(order.email, 'Order Confirmation - eSadabahar', customer_email_body)
            
            # Send email notification to admin
            admin_email_body = f"""
            New Order Received:

            Order Details:
            Order ID: {order.id}
            Customer Name: {order.customer_name}
            Email: {order.email}
            Phone: {order.phone}
            Products: {', '.join(product_details) if product_details else 'No products found'}
            Total Amount: ₹{order.total_amount}
            Delivery Address: {order.address}
            Pincode: {order.pincode}
            Delivery Date: {order.delivery_date.strftime('%d-%m-%Y')}

            Best regards,
            eSadabahar System
            """
            send_email('esadabaharorders@gmail.com', f'New Order #{order.id} - eSadabahar', admin_email_body)
        
        return jsonify({
            'success': True, 
            'message': 'Payment verified'
        })
        
    except razorpay.errors.SignatureVerificationError:
        return jsonify({'success': False, 'message': 'Invalid signature'}), 400
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        # Verify webhook signature
        webhook_secret = os.getenv('RAZORPAY_WEBHOOK_SECRET')
        received_signature = request.headers.get('X-Razorpay-Signature')
        
        razorpay_client.utility.verify_webhook_signature(
            request.data.decode('utf-8'),
            received_signature,
            webhook_secret
        )
        
        payload = request.get_json()
        if payload['event'] == 'payment.captured':
            payment = payload['payload']['payment']['entity']
            order_id = payment['notes'].get('order_id') if payment.get('notes') else None
            
            if order_id:
                order = Order.query.get(order_id)
                if order:
                    order.payment_status = 'completed'
                    order.status = 'processing'
                    db.session.commit()
        
        return jsonify({'status': 'success'}), 200
        
    except Exception as e:
        app.logger.error(f"Webhook error: {str(e)}")
        return jsonify({'error': str(e)}), 400

@app.route('/order-confirmed')
def order_confirmed():
    return render_template('order-confirmed.html')

@app.route('/test-email')
def test_email():
    try:
        send_email('esadabaharindia@gmail.com', 'Test Email', 'This is a test email from eSadabahar.')
        return 'Test email sent successfully! Check your inbox.', 200
    except Exception as e:
        app.logger.error(f"Test email error: {str(e)}")
        return f'Failed to send test email: {str(e)}', 500

@app.route('/request-refund', methods=['POST'])
def request_refund():
    try:
        data = request.get_json()
        order_id = data.get('order_id')
        customer_name = data.get('customer_name')

        # Send refund request email to admin
        refund_email_body = f"""
        Refund Request Received:

        Customer Name: {customer_name}
        Order ID: {order_id}

        Please review the refund request at your earliest convenience.

        Best regards,
        eSadabahar System
        """
        send_email('esadabaharorders@gmail.com', f'Refund Request for Order ID {order_id}', refund_email_body)

        return jsonify({'success': True, 'message': 'Refund request sent'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/admin/api/orders')
@login_required
def get_orders():
    try:
        orders = Order.query.order_by(Order.created_at.desc()).all()
        total_orders = len(orders)
        total_revenue = sum(order.total_amount for order in orders)
        pending_orders = len([order for order in orders if order.status == 'pending'])
        delivered_orders = len([order for order in orders if order.status == 'delivered'])

        return jsonify({
            'success': True,
            'total_orders': total_orders,
            'total_revenue': total_revenue,
            'pending_orders': pending_orders,
            'delivered_orders': delivered_orders,
            'orders': [{
                'id': order.id,
                'customer_name': order.customer_name,
                'total_amount': order.total_amount,
                'status': order.status,
                'payment_status': order.payment_status,
                'created_at': order.created_at.isoformat(),
                'delivery_date': order.delivery_date.strftime('%Y-%m-%d')
            } for order in orders]
        })
    except Exception as e:
        app.logger.error(f"Error fetching orders: {str(e)}")
        return jsonify({'success': False, 'error': 'Failed to fetch orders'}), 500

@app.route('/admin/api/order/<int:order_id>')
@login_required
def get_order(order_id):
    try:
        order = Order.query.get_or_404(order_id)
        order_items = OrderItem.query.filter_by(order_id=order_id).all()
        items_details = []
        
        for item in order_items:
            product = Product.query.get(item.product_id)
            if product:
                items_details.append({
                    'product_name': product.name,
                    'quantity': item.quantity,
                    'price': item.price,
                    'total': item.quantity * item.price
                })
        
        return jsonify({
            'success': True,
            'id': order.id,
            'customer_name': order.customer_name,
            'email': order.email,
            'phone': order.phone,
            'address': order.address,
            'pincode': order.pincode,
            'total_amount': order.total_amount,
            'status': order.status,
            'payment_status': order.payment_status,
            'created_at': order.created_at.isoformat(),
            'delivery_date': order.delivery_date.strftime('%Y-%m-%d'),
            'items': items_details
        })
    except Exception as e:
        app.logger.error(f"Error fetching order {order_id}: {str(e)}")
        return jsonify({'success': False, 'error': 'Failed to fetch order details'}), 500

@app.route('/admin/api/order/<int:order_id>/status', methods=['POST'])
@login_required
def update_order_status(order_id):
    try:
        data = request.json
        if not data or 'status' not in data:
            return jsonify({'success': False, 'error': 'Status is required'}), 400

        order = Order.query.get_or_404(order_id)
        order.status = data['status']
        db.session.commit()

        return jsonify({'success': True})
    except Exception as e:
        app.logger.error(f"Error updating order {order_id} status: {str(e)}")
        return jsonify({'success': False, 'error': 'Failed to update order status'}), 500

@app.route('/admin/api/order/<int:order_id>', methods=['DELETE'])
@login_required
def delete_order(order_id):
    try:
        order = Order.query.get_or_404(order_id)
        
        # Get order details for email
        order_items = OrderItem.query.filter_by(order_id=order_id).all()
        product_names = [item.product.name for item in order_items]
        
        # Send email to customer
        customer_email_body = f"""
        Dear {order.customer_name},

        Your order #{order.id} has been cancelled.

        Order Details:
        Order ID: {order.id}
        Products: {', '.join(product_names)}
        Total Amount: ₹{order.total_amount}
        Delivery Address: {order.address}
        Pincode: {order.pincode}

        If you have any questions, please contact us.

        Best regards,
        eSadabahar Team
        """
        try:
            send_email(order.email, 'Order Cancelled - eSadabahar', customer_email_body)
            app.logger.info(f"Sent cancellation email to customer {order.email}")
        except Exception as e:
            app.logger.error(f"Failed to send customer email: {str(e)}")
        
        # Send email to admin
        admin_email_body = f"""
        Order #{order.id} has been deleted.

        Order Details:
        Customer Name: {order.customer_name}
        Email: {order.email}
        Phone: {order.phone}
        Products: {', '.join(product_names)}
        Total Amount: ₹{order.total_amount}
        Delivery Address: {order.address}
        Pincode: {order.pincode}

        Best regards,
        eSadabahar System
        """
        try:
            send_email('esadabaharorders@gmail.com', f'Order #{order.id} Deleted', admin_email_body)
            app.logger.info("Sent deletion notification to admin")
        except Exception as e:
            app.logger.error(f"Failed to send admin email: {str(e)}")
        
        # Delete order items first (due to foreign key constraint)
        for item in order_items:
            db.session.delete(item)
            app.logger.info(f"Deleted order item {item.id}")
        
        # Delete the order
        db.session.delete(order)
        db.session.commit()
        app.logger.info(f"Successfully deleted order {order_id}")
        
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"Error deleting order {order_id}: {str(e)}")
        return jsonify({'success': False, 'message': 'Failed to delete order'}), 500

@app.route('/get-razorpay-key')
def get_razorpay_key():
    return jsonify({
        'key': os.getenv('RAZORPAY_KEY_ID')
    })

@app.route('/setup')
def setup():
    try:
        # Check if admin user already exists
        admin = User.query.filter_by(username='admin').first()
        if admin:
            return 'Admin user already exists!'
        
        # Create admin user
        admin = User(username='admin', is_admin=True)
        admin.set_password('admin123')  # You should change this password
        db.session.add(admin)
        db.session.commit()
        
        return 'Admin user created successfully! Username: admin, Password: admin123'
    except Exception as e:
        return f'Error creating admin user: {str(e)}'

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        
        # Seed the database with sample products if none exist
        if Product.query.count() == 0:
            sample_products = [
                Product(name='Red Rose Bouquet', category='bouquet', price=599.00, 
                       description='Beautiful bouquet of 12 red roses', 
                       image_url='https://images.pexels.com/photos/931177/pexels-photo-931177.jpeg',
                       stock=20),
                Product(name='Mixed Flower Bouquet', category='bouquet', price=799.00, 
                       description='Colorful bouquet with various flowers', 
                       image_url='https://images.pexels.com/photos/931154/pexels-photo-931154.jpeg',
                       stock=15),
                Product(name='Chocolate Cake', category='cake_500g', price=699.00, 
                       description='Delicious chocolate cake with frosting', 
                       image_url='https://images.pexels.com/photos/291528/pexels-photo-291528.jpeg',
                       stock=10),
                Product(name='Vanilla Cake', category='cake_500g', price=599.00, 
                       description='Classic vanilla cake with buttercream', 
                       image_url='https://images.pexels.com/photos/2144112/pexels-photo-2144112.jpeg',
                       stock=10),
                Product(name='Chocolate Truffles', category='chocolate', price=399.00, 
                       description='Assorted chocolate truffles', 
                       image_url='https://images.pexels.com/photos/65882/chocolate-dark-coffee-confiserie-65882.jpeg',
                       stock=25),
                Product(name='Dark Chocolate Box', category='chocolate', price=499.00, 
                       description='Premium dark chocolate assortment', 
                       image_url='https://images.pexels.com/photos/65882/chocolate-dark-coffee-confiserie-65882.jpeg',
                       stock=20),
                Product(name='Flower & Cake Combo', category='combo', price=1299.00, 
                       description='Bouquet of roses with a chocolate cake', 
                       image_url='https://images.pexels.com/photos/931154/pexels-photo-931154.jpeg',
                       stock=5),
                Product(name='Chocolate & Flowers', category='combo', price=999.00, 
                       description='Chocolate box with a small flower arrangement', 
                       image_url='https://images.pexels.com/photos/65882/chocolate-dark-coffee-confiserie-65882.jpeg',
                       stock=8)
            ]
            
            for product in sample_products:
                db.session.add(product)
            
            db.session.commit()
            print("Sample products added to the database.")




    
    app.run(debug=True) 