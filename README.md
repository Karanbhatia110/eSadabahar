# eSadabahar - Online Flower Shop

An e-commerce platform for selling flowers, cakes, chocolates, and combos.

## Features

- User-friendly interface
- Responsive design for all devices
- Admin panel for order management
- Email and WhatsApp notifications
- Razorpay payment integration
- Order tracking system
- Time-based order confirmation (10:00 AM - 11:59 PM)

## Setup Instructions

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
Create a `.env` file with the following variables:
```
FLASK_APP=app.py
FLASK_ENV=development
SECRET_KEY=your-secret-key
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-email-password
RAZORPAY_KEY_ID=your-razorpay-key
RAZORPAY_KEY_SECRET=your-razorpay-secret
TWILIO_ACCOUNT_SID=your-twilio-sid
TWILIO_AUTH_TOKEN=your-twilio-token
```

4. Run the application:
```bash
flask run
```

## Admin Panel

Access the admin panel at `/admin` with your credentials to:
- View all orders
- Track order status
- Manage inventory
- View revenue reports

## Order Process

1. Users can place orders between 10:00 AM and 11:59 PM
2. Orders require:
   - Name
   - Email
   - Phone number
   - Delivery address
   - Pincode
3. Payment processing through Razorpay
4. Email and WhatsApp notifications for order confirmation and delivery

## Note

- Cake designs may vary based on location
- No refund policy for cancelled orders
- Orders placed after 11:59 PM will be held for review 