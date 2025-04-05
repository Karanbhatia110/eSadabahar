// Cart Management
let cart = JSON.parse(localStorage.getItem('cart')) || [];

function updateCartCount() {
    const cartCount = document.getElementById('cart-count');
    if (cartCount) {
        cartCount.textContent = cart.reduce((total, item) => total + item.quantity, 0);
    }
}

function addToCart(productId, name, price) {
    const existingItem = cart.find(item => item.id === productId);
    
    if (existingItem) {
        existingItem.quantity += 1;
    } else {
        cart.push({
            id: productId,
            name: name,
            price: price,
            quantity: 1
        });
    }
    
    localStorage.setItem('cart', JSON.stringify(cart));
    updateCartCount();
    showNotification('Item added to cart!');
}

function removeFromCart(productId) {
    cart = cart.filter(item => item.id !== productId);
    localStorage.setItem('cart', JSON.stringify(cart));
    updateCartCount();
    showNotification('Item removed from cart!');
}

function updateQuantity(productId, change) {
    const item = cart.find(item => item.id === productId);
    if (item) {
        item.quantity = Math.max(1, item.quantity + change);
        localStorage.setItem('cart', JSON.stringify(cart));
        updateCartCount();
    }
}

// Notifications
function showNotification(message, type = 'success') {
    const alert = document.createElement('div');
    alert.className = `alert alert-${type} alert-dismissible fade show`;
    alert.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    document.querySelector('main').insertBefore(alert, document.querySelector('main').firstChild);
    
    // Auto dismiss after 3 seconds
    setTimeout(() => {
        alert.remove();
    }, 3000);
}

// Order Time Validation
function validateOrderTime() {
    const now = new Date();
    const hours = now.getHours();
    const minutes = now.getMinutes();
    
    if (hours < 10 || (hours === 23 && minutes > 59)) {
        showNotification('Orders are only accepted between 10:00 AM and 11:59 PM', 'warning');
        return false;
    }
    return true;
}

// Razorpay Integration
function initializeRazorpay(orderData) {
    const options = {
        key: 'rzp_test_6yTFmQVbKqK8yw',
        amount: orderData.amount,
        currency: orderData.currency,
        order_id: orderData.order_id,
        handler: function(response) {
            handlePaymentSuccess(response);
        },
        prefill: {
            name: orderData.name,
            email: orderData.email,
            contact: orderData.phone
        },
        theme: {
            color: '#4a90e2'
        }
    };

    const rzp = new Razorpay(options);
    rzp.open();
}

async function handlePaymentSuccess(response) {
    try {
        // Add order details to the verification request
        const verificationData = {
            razorpay_payment_id: response.razorpay_payment_id,
            razorpay_order_id: response.razorpay_order_id,
            razorpay_signature: response.razorpay_signature,
            order_data: JSON.parse(localStorage.getItem('currentOrder')) // Store this during checkout
        };

        const result = await fetch('/verify-payment', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCSRFToken() // Add if using CSRF
            },
            body: JSON.stringify(verificationData)
        });

        if (!result.ok) {
            throw new Error(await result.text());
        }

        const data = await result.json();
        
        if (data.success) {
            // Clear cart only after successful verification
            localStorage.removeItem('cart');
            localStorage.removeItem('currentOrder');
            
            // Redirect with order ID for confirmation page
            window.location.href = `/order-confirmed?order_id=${data.order_id}`;
        } else {
            showNotification(data.message || 'Payment verification failed', 'danger');
            // Optionally reopen payment if verification fails
            if (data.retry_allowed) {
                initializeRazorpay(verificationData.order_data);
            }
        }
    } catch (error) {
        console.error('Payment verification error:', error);
        showNotification('Payment processing failed. Please contact support with payment ID: ' + 
                        response.razorpay_payment_id, 'danger');
        // Log error to your error tracking system
        logError(error);
    }
}

// Form Validation
function validateForm(formId) {
    const form = document.getElementById(formId);
    if (!form) return true;

    let isValid = true;
    const requiredFields = form.querySelectorAll('[required]');

    requiredFields.forEach(field => {
        if (!field.value.trim()) {
            field.classList.add('is-invalid');
            isValid = false;
        } else {
            field.classList.remove('is-invalid');
        }
    });

    return isValid;
}

// Initialize
document.addEventListener('DOMContentLoaded', function() {
    updateCartCount();

    // Add to cart buttons
    document.querySelectorAll('.add-to-cart').forEach(button => {
        button.addEventListener('click', function() {
            if (!validateOrderTime()) return;
            
            const productId = this.dataset.productId;
            const name = this.dataset.name;
            const price = parseFloat(this.dataset.price);
            
            addToCart(productId, name, price);
        });
    });

    // Form validation
    document.querySelectorAll('form').forEach(form => {
        form.addEventListener('submit', function(e) {
            if (!validateForm(this.id)) {
                e.preventDefault();
                showNotification('Please fill in all required fields.', 'warning');
            }
        });
    });
}); 