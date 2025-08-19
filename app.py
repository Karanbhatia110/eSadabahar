from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, send_file, session
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_mail import Mail, Message
from datetime import datetime, timedelta
import razorpay
import os
from dotenv import load_dotenv
import requests
from twilio.rest import Client
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from io import BytesIO
import gridfs
import time
import uuid
import pytz
from pymongo import MongoClient
from bson import ObjectId

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
app.config['MAIL_DEFAULT_SENDER'] = os.getenv('MAIL_USERNAME')
app.config['MAIL_MAX_EMAILS'] = 10
app.config['MAIL_ASCII_ATTACHMENTS'] = False
app.config['MAIL_DEBUG'] = True
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=30)
app.config['UPLOAD_FOLDER'] = os.path.join('static', 'uploads')
app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024  # 10 MB

ALLOWED_IMAGE_EXTENSIONS = {'.png', '.jpg', '.jpeg', '.webp', '.gif'}

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Initialize MongoDB client
mongo_client = MongoClient('mongodb+srv://karanbhatia9780:QNqkytgMgiNFZ6oO@esadabahar.gj3hixi.mongodb.net/?tls=true')
db = mongo_client['esadabahar']
users_collection = db['users']
products_collection = db['products']
orders_collection = db['orders']
order_items_collection = db['order_items']
categories_collection = db['categories']
grid_fs = gridfs.GridFS(db)

# Initialize extensions
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

# Add favicon routes
@app.route('/favicon.ico')
def favicon():
    return send_file('static/images/Real Logo.png', mimetype='image/png')

@app.route('/static/images/Real Logo.png')
def serve_logo():
    return send_file('static/images/Real Logo.png', mimetype='image/png')

# Models
class User(UserMixin):
    def __init__(self, user_data):
        self.id = str(user_data['_id'])
        self.username = user_data['username']
        self.password_hash = user_data['password_hash']
        self.is_admin = user_data.get('is_admin', False)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password, method='pbkdf2:sha256')
        
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

@login_manager.user_loader
def load_user(user_id):
    user_data = users_collection.find_one({'_id': ObjectId(user_id)})
    if user_data:
        return User(user_data)
    return None

# Routes
@app.route('/')
def home():
    try:
        products = list(products_collection.find())
        app.logger.info(f"Found {len(products)} products in database")
        if not products:
            app.logger.warning("No products found in database. Please run init_db.py to initialize the database.")
        return render_template('index.html', products=products)
    except Exception as e:
        app.logger.error(f"Error loading products: {str(e)}")
        return render_template('index.html', products=[])

@app.route('/cart')
def cart():
    return render_template('cart.html')

@app.route('/product/<product_id>')
def product_detail(product_id):
    try:
        product = products_collection.find_one({'_id': ObjectId(product_id)})
        if not product:
            return redirect(url_for('home'))

        # Normalize fields for template
        product_ctx = {
            'id': str(product.get('_id')),
            'name': product.get('name', ''),
            'category': product.get('category', ''),
            'price': float(product.get('price', 0)),
            'description': product.get('description', ''),
            'image_url': product.get('image_url', ''),
            'stock': int(product.get('stock', 0)),
            'colors': product.get('colors', []),
            'variants': product.get('variants', []),  # list of {color, image_url}
        }
        return render_template('product.html', product=product_ctx)
    except Exception as e:
        app.logger.error(f"Error loading product {product_id}: {str(e)}")
        return redirect(url_for('home'))

@app.route('/checkout', methods=['GET', 'POST'])
def checkout():
    try:
        if request.method == 'GET':
            return render_template('checkout.html')
            
        if request.is_json:
            data = request.get_json()
        else:
            data = request.form.to_dict()
            if 'total_amount' in data:
                data['amount'] = float(data['total_amount'])
        
        required_fields = ['name', 'email', 'phone', 'address', 'pincode', 'amount', 'delivery_date', 'items']
        missing_fields = [field for field in required_fields if not data.get(field)]
        if missing_fields:
            return jsonify({
                'success': False,
                'message': f'Missing required fields: {", ".join(missing_fields)}'
            }), 400
        
        # Convert delivery_date string to datetime object
        delivery_date = datetime.strptime(data['delivery_date'], '%Y-%m-%d')
        delivery_date = datetime.combine(delivery_date.date(), datetime.min.time())
        delivery_date = ist.localize(delivery_date)
        
        # Create order in database
        order_data = {
            'customer_name': data['name'],
            'email': data['email'],
            'phone': data['phone'],
            'address': data['address'],
            'pincode': data['pincode'],
            'total_amount': float(data['amount']),
            'status': 'pending',
            'payment_status': 'pending',
            'created_at': datetime.now(ist),
            'delivery_date': delivery_date,
            'instruction': data.get('instruction', '')
        }
        order_result = orders_collection.insert_one(order_data)
        order_id = order_result.inserted_id

        # Create order items
        for item in data['items']:
            try:
                # Convert product_id to string if it's not already
                product_id = str(item['id'])
                order_item = {
                    'order_id': order_id,
                    'product_id': ObjectId(product_id),
                    'quantity': int(item['quantity']),
                    'price': float(item['price'])
                }
                order_items_collection.insert_one(order_item)
            except Exception as e:
                app.logger.error(f"Error creating order item: {str(e)}")
                # Continue with other items even if one fails
                continue

        # Create Razorpay order
        razorpay_order = razorpay_client.order.create({
            'amount': int(float(data['amount']) * 100),
            'currency': 'INR',
            'receipt': f'order_{order_id}',
            'notes': {
                'order_id': str(order_id)
            }
        })

        return jsonify({
            'success': True,
            'order_id': str(order_id),
            'razorpay_order_id': razorpay_order['id'],
            'amount': razorpay_order['amount'],
            'currency': razorpay_order['currency'],
            'name': order_data['customer_name'],
            'email': order_data['email'],
            'phone': order_data['phone'],
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
    orders = list(orders_collection.find().sort('created_at', -1))
    for order in orders:
        order['created_at'] = order['created_at'].astimezone(ist)
    return render_template('admin/dashboard.html', orders=orders)

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        try:
            data = request.json
            username = data.get('username')
            password = data.get('password')
            
            if not username or not password:
                return jsonify({
                    'success': False,
                    'message': 'Username and password are required'
                }), 400
            
            user_data = users_collection.find_one({'username': username})
            if not user_data:
                return jsonify({
                    'success': False,
                    'message': 'Invalid username or password'
                }), 401
            
            user = User(user_data)
            if not user.check_password(password):
                return jsonify({
                    'success': False,
                    'message': 'Invalid username or password'
                }), 401
            
            if not user.is_admin:
                return jsonify({
                    'success': False,
                    'message': 'Access denied. Admin privileges required.'
                }), 403
            
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
    products = list(products_collection.find())
    return jsonify([{
        'id': str(product['_id']),
        'name': product['name'],
        'category': product['category'],
        'price': product['price'],
        'description': product['description'],
        'image_url': product['image_url'],
        'stock': product['stock'],
        'colors': product.get('colors', []),
        'variants': product.get('variants', []),
    } for product in products])

@app.route('/api/categories')
def get_public_categories():
    try:
        product_categories = products_collection.distinct('category')
        stored = [c.get('name') for c in categories_collection.find({}, {'name': 1})]
        names = sorted({*(c for c in product_categories if c), *(n for n in stored if n)})
        return jsonify({'success': True, 'categories': names})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/bestsellers')
def get_bestsellers():
    try:
        # Get ALL products from MongoDB for featured section
        all_products = list(products_collection.find())
        
        # Shuffle the products to get random order
        import random
        random.shuffle(all_products)
        
        # Return all products (they will be displayed in horizontal scroll)
        return jsonify([{
            'id': str(p['_id']),
            'name': p.get('name'),
            'category': p.get('category'),
            'price': float(p.get('price', 0)),
            'description': p.get('description', ''),
            'image_url': p.get('image_url', ''),
            'stock': int(p.get('stock', 0)),
            'colors': p.get('colors', []),
            'variants': p.get('variants', [])
        } for p in all_products])
    except Exception as e:
        app.logger.error(f"Featured products error: {str(e)}")
        return jsonify({'success': False, 'error': 'Failed to load featured products'}), 500

# -------------------- Admin: Product & Category Management --------------------
def ensure_admin_access():
    if not current_user.is_authenticated or not getattr(current_user, 'is_admin', False):
        return jsonify({'success': False, 'error': 'Admin access required'}), 403
    return None

@app.route('/admin/api/categories', methods=['GET', 'POST'])
@login_required
def admin_categories():
    access_error = ensure_admin_access()
    if access_error:
        return access_error

    if request.method == 'GET':
        categories = list(categories_collection.find())
        product_categories = products_collection.distinct('category')
        # Build unique names combining both sources
        name_set = {c['name'] for c in categories if c.get('name')}
        name_set.update({c for c in product_categories if c})
        merged = sorted(name_set)
        return jsonify({'success': True, 'categories': [
            {'id': None, 'name': name} for name in merged
        ]})

    # POST - create category
    data = request.get_json() or {}
    name = (data.get('name') or '').strip()
    if not name:
        return jsonify({'success': False, 'error': 'Category name is required'}), 400

    # Ensure uniqueness (case-insensitive)
    existing = categories_collection.find_one({'name': {'$regex': f'^{name}$', '$options': 'i'}})
    if existing:
        return jsonify({'success': False, 'error': 'Category already exists'}), 409

    result = categories_collection.insert_one({'name': name})
    return jsonify({'success': True, 'id': str(result.inserted_id), 'name': name})

@app.route('/admin/api/categories/<category_id>', methods=['PUT', 'DELETE'])
@login_required
def admin_update_delete_category(category_id):
    access_error = ensure_admin_access()
    if access_error:
        return access_error

    try:
        object_id = ObjectId(category_id)
    except Exception:
        return jsonify({'success': False, 'error': 'Invalid category ID'}), 400

    if request.method == 'DELETE':
        categories_collection.delete_one({'_id': object_id})
        return jsonify({'success': True})

    # PUT - update category name
    data = request.get_json() or {}
    name = (data.get('name') or '').strip()
    if not name:
        return jsonify({'success': False, 'error': 'Category name is required'}), 400
    categories_collection.update_one({'_id': object_id}, {'$set': {'name': name}})
    return jsonify({'success': True})

@app.route('/admin/api/products', methods=['GET', 'POST'])
@login_required
def admin_products():
    access_error = ensure_admin_access()
    if access_error:
        return access_error

    if request.method == 'GET':
        products = list(products_collection.find().sort('name', 1))
        return jsonify({'success': True, 'products': [{
            'id': str(p['_id']),
            'name': p.get('name'),
            'category': p.get('category'),
            'price': float(p.get('price', 0)),
            'description': p.get('description', ''),
            'image_url': p.get('image_url', ''),
            'stock': int(p.get('stock', 0)),
            'colors': p.get('colors', []),
            'variants': p.get('variants', [])
        } for p in products]})

    # POST - create product
    data = request.get_json() or {}
    required = ['name', 'category', 'price', 'description', 'image_url']
    missing = [f for f in required if not data.get(f)]
    if missing:
        return jsonify({'success': False, 'error': f"Missing fields: {', '.join(missing)}"}), 400

    product = {
        'name': data['name'],
        'category': data['category'],  # store as string
        'price': float(data['price']),
        'description': data['description'],
        'image_url': data['image_url'],
        'stock': int(data.get('stock', 0)),
        'colors': data.get('colors', []),
        'variants': data.get('variants', []),
    }
    result = products_collection.insert_one(product)
    return jsonify({'success': True, 'id': str(result.inserted_id)})

@app.route('/admin/api/products/<product_id>', methods=['PUT', 'DELETE'])
@login_required
def admin_update_delete_product(product_id):
    access_error = ensure_admin_access()
    if access_error:
        return access_error

    try:
        object_id = ObjectId(product_id)
    except Exception:
        return jsonify({'success': False, 'error': 'Invalid product ID'}), 400

    if request.method == 'DELETE':
        products_collection.delete_one({'_id': object_id})
        # Also remove any order_items referencing this product (optional cleanup)
        order_items_collection.delete_many({'product_id': object_id})
        return jsonify({'success': True})

    # PUT - update one or more fields
    data = request.get_json() or {}
    updatable_fields = {'name', 'category', 'price', 'description', 'image_url', 'stock', 'colors', 'variants'}
    update_data = {k: data[k] for k in updatable_fields if k in data}
    if 'price' in update_data:
        update_data['price'] = float(update_data['price'])
    if 'stock' in update_data:
        update_data['stock'] = int(update_data['stock'])

    if not update_data:
        return jsonify({'success': False, 'error': 'No valid fields to update'}), 400

    products_collection.update_one({'_id': object_id}, {'$set': update_data})
    return jsonify({'success': True})

def _allowed_image(filename: str) -> bool:
    ext = os.path.splitext(filename)[1].lower()
    return ext in ALLOWED_IMAGE_EXTENSIONS

@app.route('/admin/api/upload', methods=['POST'])
@login_required
def admin_upload_image():
    access_error = ensure_admin_access()
    if access_error:
        return access_error

    if 'file' not in request.files:
        return jsonify({'success': False, 'error': 'No file part'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'success': False, 'error': 'No file selected'}), 400
    filename = secure_filename(file.filename)
    if not _allowed_image(filename):
        return jsonify({'success': False, 'error': 'Invalid file type'}), 400
    ext = os.path.splitext(filename)[1].lower()
    unique_name = f"{uuid.uuid4().hex}{ext}"
    save_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_name)
    try:
        # Save to disk for local development
        file.save(save_path)

        # Also save to GridFS for persistence across hosts
        try:
            # Reset stream and read bytes
            try:
                file.stream.seek(0)
            except Exception:
                pass
            content = file.read()
            if not content:
                with open(save_path, 'rb') as f:
                    content = f.read()
            grid_id = grid_fs.put(
                content,
                filename=unique_name,
                contentType=getattr(file, 'mimetype', None) or 'application/octet-stream'
            )
            media_url = f"/media/{str(grid_id)}"
        except Exception:
            media_url = None

        url = media_url or f"/static/uploads/{unique_name}"
        return jsonify({'success': True, 'url': url, 'local_url': f"/static/uploads/{unique_name}"})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

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
        
        razorpay_client.utility.verify_payment_signature({
            'razorpay_order_id': data['razorpay_order_id'],
            'razorpay_payment_id': data['razorpay_payment_id'],
            'razorpay_signature': data['razorpay_signature']
        })
        
        order = orders_collection.find_one({'_id': ObjectId(data['order_id'])})
        if order:
            orders_collection.update_one(
                {'_id': ObjectId(data['order_id'])},
                {'$set': {
                    'payment_status': 'completed',
                    'status': 'processing'
                }}
            )
            
            order_items = list(order_items_collection.find({'order_id': ObjectId(data['order_id'])}))
            product_details = []
            for item in order_items:
                product = products_collection.find_one({'_id': item['product_id']})
                if product:
                    product_details.append(f"{product['name']} (Qty: {item['quantity']})")
            
            # Send email confirmation to customer
            customer_email_body = f"""
            Dear {order['customer_name']},

            Your payment has been successfully processed, and your order is now confirmed.

            Order Details:
            Order ID: {str(order['_id'])}
            Products: {', '.join(product_details) if product_details else 'No products found'}
            Total Amount: ₹{order['total_amount']}
            Delivery Address: {order['address']}
            Pincode: {order['pincode']}
            Delivery Date: {order['delivery_date'].strftime('%d-%m-%Y')}

            Thank you for shopping with us!

            Best regards,
            eSadabahar Team
            """
            send_email(order['email'], 'Order Confirmation - eSadabahar', customer_email_body)
            
            # Send email notification to admin
            admin_email_body = f"""
            New Order Received:

            Order Details:
            Order ID: {str(order['_id'])}
            Customer Name: {order['customer_name']}
            Email: {order['email']}
            Phone: {order['phone']}
            Products: {', '.join(product_details) if product_details else 'No products found'}
            Total Amount: ₹{order['total_amount']}
            Delivery Address: {order['address']}
            Pincode: {order['pincode']}
            Delivery Date: {order['delivery_date'].strftime('%d-%m-%Y')}

            Best regards,
            eSadabahar System
            """
            send_email('esadabaharorders@gmail.com', f'New Order #{str(order["_id"])} - eSadabahar', admin_email_body)
        
        return jsonify({
           'success': True,
           'redirect_url': url_for('order_confirmed', order_id=str(order['_id']), _external=True)
            })

        
    except razorpay.errors.SignatureVerificationError:
        return jsonify({'success': False, 'message': 'Invalid signature'}), 400
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/webhook', methods=['POST'])
def webhook():
    try:
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
                orders_collection.update_one(
                    {'_id': ObjectId(order_id)},
                    {'$set': {
                        'payment_status': 'completed',
                        'status': 'processing'
                    }}
                )
        
        return jsonify({'status': 'success'}), 200
        
    except Exception as e:
        app.logger.error(f"Webhook error: {str(e)}")
        return jsonify({'error': str(e)}), 400

@app.route('/order-confirmed/<order_id>')
def order_confirmed(order_id):
    order = orders_collection.find_one({'_id': ObjectId(order_id)})

    if not order or order.get("payment_status") != "completed":
        return redirect(url_for("home"))

    return render_template("order-confirmed.html", order=order)


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
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        min_price = request.args.get('min_price', type=float)
        max_price = request.args.get('max_price', type=float)

        query = {}
        
        if start_date:
            start_date = datetime.strptime(start_date, '%Y-%m-%d')
            query['created_at'] = {'$gte': start_date}
        if end_date:
            end_date = datetime.strptime(end_date, '%Y-%m-%d')
            end_date = end_date + timedelta(days=1)
            query['created_at'] = {'$lt': end_date}
        if min_price is not None:
            query['total_amount'] = {'$gte': min_price}
        if max_price is not None:
            query['total_amount'] = {'$lte': max_price}

        orders = list(orders_collection.find(query).sort('created_at', -1))
        
        total_orders = len(orders)
        total_revenue = sum(order['total_amount'] for order in orders if order['status'] == 'delivered')
        pending_orders = len([order for order in orders if order['status'] == 'pending'])
        delivered_orders = len([order for order in orders if order['status'] == 'delivered'])

        return jsonify({
            'success': True,
            'total_orders': total_orders,
            'total_revenue': total_revenue,
            'pending_orders': pending_orders,
            'delivered_orders': delivered_orders,
            'orders': [{
                'id': str(order['_id']),
                'customer_name': order['customer_name'],
                'total_amount': order['total_amount'],
                'status': order['status'],
                'payment_status': order['payment_status'],
                'created_at': order['created_at'].isoformat(),
                'delivery_date': order['delivery_date'].strftime('%Y-%m-%d')
            } for order in orders]
        })
    except Exception as e:
        app.logger.error(f"Error fetching orders: {str(e)}")
        return jsonify({'success': False, 'error': 'Failed to fetch orders'}), 500

@app.route('/admin/api/order/<order_id>')
@login_required
def get_order(order_id):
    try:
        order = orders_collection.find_one({'_id': ObjectId(order_id)})
        if not order:
            return jsonify({'success': False, 'error': 'Order not found'}), 404
            
        order_items = list(order_items_collection.find({'order_id': ObjectId(order_id)}))
        items_details = []
        
        for item in order_items:
            product = products_collection.find_one({'_id': item['product_id']})
            if product:
                items_details.append({
                    'product_name': product['name'],
                    'quantity': item['quantity'],
                    'price': item['price'],
                    'total': item['quantity'] * item['price']
                })
        
        return jsonify({
            'success': True,
            'id': str(order['_id']),
            'customer_name': order['customer_name'],
            'email': order['email'],
            'phone': order['phone'],
            'address': order['address'],
            'pincode': order['pincode'],
            'total_amount': order['total_amount'],
            'status': order['status'],
            'payment_status': order['payment_status'],
            'created_at': order['created_at'].isoformat(),
            'delivery_date': order['delivery_date'].strftime('%Y-%m-%d'),
            'instruction': order['instruction'],
            'items': items_details
        })
    except Exception as e:
        app.logger.error(f"Error fetching order {order_id}: {str(e)}")
        return jsonify({'success': False, 'error': 'Failed to fetch order details'}), 500

@app.route('/admin/api/order/<order_id>/status', methods=['POST'])
@login_required
def update_order_status(order_id):
    try:
        app.logger.info(f"Attempting to update order status for order ID: {order_id}")
        
        data = request.get_json()
        if not data or 'status' not in data:
            app.logger.error("Status not provided in request data")
            return jsonify({'success': False, 'error': 'Status is required'}), 400

        # Convert order_id to ObjectId
        try:
            order_object_id = ObjectId(order_id)
        except Exception as e:
            app.logger.error(f"Invalid order ID format: {order_id}")
            return jsonify({'success': False, 'error': 'Invalid order ID format'}), 400

        # Check if order exists
        order = orders_collection.find_one({'_id': order_object_id})
        if not order:
            app.logger.error(f"Order not found with ID: {order_id}")
            return jsonify({'success': False, 'error': 'Order not found'}), 404

        # Update order status
        result = orders_collection.update_one(
            {'_id': order_object_id},
            {'$set': {'status': data['status']}}
        )
        
        if result.modified_count == 0:
            app.logger.error(f"No changes made to order {order_id}")
            return jsonify({'success': False, 'error': 'No changes made to order'}), 400

        app.logger.info(f"Successfully updated order {order_id} status to {data['status']}")
        
        # Get updated order
        updated_order = orders_collection.find_one({'_id': order_object_id})
        
        # Send email notification to customer
        email_body = f"""
        Dear {updated_order['customer_name']},

        Your order status has been updated to: {data['status']}

        Order Details:
        Order ID: {str(updated_order['_id'])}
        Total Amount: ₹{updated_order['total_amount']}
        Delivery Address: {updated_order['address']}
        Pincode: {updated_order['pincode']}
        Delivery Date: {updated_order['delivery_date'].strftime('%d-%m-%Y')}

        Thank you for shopping with us!

        Best regards,
        eSadabahar Team
        """
        send_email(updated_order['email'], f'Order Status Update - eSadabahar', email_body)

        return jsonify({'success': True, 'message': 'Order status updated successfully'})
    except Exception as e:
        app.logger.error(f"Error updating order status: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/admin/api/order/<order_id>', methods=['DELETE'])
@login_required
def delete_order(order_id):
    try:
        # Get order details before deletion
        order = orders_collection.find_one({'_id': ObjectId(order_id)})
        if not order:
            return jsonify({'success': False, 'error': 'Order not found'}), 404

        # Delete order items first
        order_items_collection.delete_many({'order_id': ObjectId(order_id)})
        
        # Delete the order
        orders_collection.delete_one({'_id': ObjectId(order_id)})

        # Send cancellation email to customer
        email_body = f"""
        Dear {order['customer_name']},

        Your order has been cancelled.

        Order Details:
        Order ID: {str(order['_id'])}
        Total Amount: ₹{order['total_amount']}
        Delivery Address: {order['address']}
        Pincode: {order['pincode']}
        Delivery Date: {order['delivery_date'].strftime('%d-%m-%Y')}

        If you have any questions, please contact us.

        Best regards,
        eSadabahar Team
        """
        send_email(order['email'], 'Order Cancelled - eSadabahar', email_body)

        return jsonify({'success': True, 'message': 'Order deleted successfully'})
    except Exception as e:
        app.logger.error(f"Error deleting order: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/get-razorpay-key')
def get_razorpay_key():
    return jsonify({
        'key': os.getenv('RAZORPAY_KEY_ID')
    })

@app.route('/media/<file_id>')
def serve_media(file_id):
    try:
        gridout = grid_fs.get(ObjectId(file_id))
        data = gridout.read()
        mimetype = getattr(gridout, 'contentType', None) or 'application/octet-stream'
        return send_file(BytesIO(data), mimetype=mimetype, download_name=getattr(gridout, 'filename', 'file'))
    except Exception:
        return jsonify({'success': False, 'error': 'File not found'}), 404

@app.route('/setup')
def setup():
    try:
        # Check if admin user already exists
        admin = users_collection.find_one({'username': 'admin'})
        if admin:
            return 'Admin user already exists!'
        
        # Create admin user
        admin_user = {
            'username': 'admin',
            'password_hash': generate_password_hash('admin123', method='pbkdf2:sha256'),
            'is_admin': True
        }
        users_collection.insert_one(admin_user)
        
        return 'Admin user created successfully! Username: admin, Password: admin123'
    except Exception as e:
        return f'Error creating admin user: {str(e)}'

@app.route('/debug/products')
def debug_products():
    try:
        products = list(products_collection.find())
        return jsonify({
            'count': len(products),
            'products': [{
                'id': str(p['_id']),
                'name': p['name'],
                'category': p['category'],
                'price': p['price']
            } for p in products]
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True) 
