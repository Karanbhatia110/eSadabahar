# eSadabahar - Online Flower, Cake & Chocolate Shop

A full-featured e-commerce website for selling flowers, cakes, chocolates, and combo packages with same-day delivery in Zirakpur.

## Features

- Product browsing by categories (Bouquets, Cakes, Chocolates, Combos)
- Shopping cart functionality
- Checkout process with Razorpay payment integration
- Order confirmation via email and WhatsApp
- Admin dashboard for order management
- Responsive design for all devices

## Tech Stack

- **Frontend**: HTML, CSS, JavaScript, Bootstrap 5
- **Backend**: Flask (Python)
- **Database**: SQLite (SQLAlchemy ORM)
- **Payment**: Razorpay
- **Notifications**: Flask-Mail, Twilio (WhatsApp)

## Setup Instructions

### Local Development

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/esadabahar.git
   cd esadabahar
   ```

2. Create a virtual environment and activate it:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Create a `.env` file with the following variables:
   ```
   SECRET_KEY=your_secret_key
   RAZORPAY_KEY_ID=rzp_test_6yTFmQVbKqK8yw
   RAZORPAY_KEY_SECRET=your_razorpay_key_secret
   MAIL_SERVER=your_smtp_server
   MAIL_PORT=587
   MAIL_USE_TLS=True
   MAIL_USERNAME=your_email
   MAIL_PASSWORD=your_email_password
   TWILIO_ACCOUNT_SID=your_twilio_sid
   TWILIO_AUTH_TOKEN=your_twilio_token
   TWILIO_PHONE_NUMBER=your_twilio_phone
   ```

5. Run the application:
   ```
   python app.py
   ```

6. Access the website at `http://127.0.0.1:5000`

### Deployment to Vercel

1. Install Vercel CLI:
   ```
   npm install -g vercel
   ```

2. Login to Vercel:
   ```
   vercel login
   ```

3. Deploy the application:
   ```
   vercel
   ```

4. Set up environment variables in the Vercel dashboard.

## Admin Access

- URL: `/admin/login`
- Default credentials:
  - Username: kyu batau
  - Password: khud pata karle 

## License

This project is licensed under the MIT License - see the LICENSE file for details. 