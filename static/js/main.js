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
        key: 'YOUR_RAZORPAY_KEY_ID',
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

function handlePaymentSuccess(response) {
    // Send payment verification to server
    fetch('/verify-payment', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(response)
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showNotification('Payment successful! Your order has been placed.');
            localStorage.removeItem('cart');
            window.location.href = '/';
        } else {
            showNotification('Payment verification failed. Please contact support.', 'danger');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showNotification('An error occurred. Please try again.', 'danger');
    });
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