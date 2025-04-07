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
function showNotification(message, type = 'info') {
    const container = document.getElementById('notification-container');
    if (!container) {
        console.warn('Notification container not found');
        return;
    }

    const notification = document.createElement('div');
    notification.className = `alert alert-${type} alert-dismissible fade show`;
    notification.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
    `;

    container.insertBefore(notification, container.firstChild);

    // Auto-remove after 5 seconds
    setTimeout(() => {
        notification.remove();
    }, 5000);
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
async function initializeRazorpay(orderData) {
    try {
        // Get Razorpay key from backend
        const response = await fetch('/get-razorpay-key');
        const data = await response.json();
        
        const options = {
            key: data.key,
            amount: orderData.amount,
            currency: orderData.currency,
            order_id: orderData.razorpay_order_id,
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
    } catch (error) {
        console.error('Error initializing Razorpay:', error);
        showNotification('Failed to initialize payment. Please try again.', 'danger');
    }
}

async function handlePaymentSuccess(response) {
    try {
        // Get the current order data
        const currentOrder = JSON.parse(localStorage.getItem('currentOrder'));
        
        // Add order details to the verification request
        const verificationData = {
            razorpay_payment_id: response.razorpay_payment_id,
            razorpay_order_id: response.razorpay_order_id,
            razorpay_signature: response.razorpay_signature,
            order_id: currentOrder.order_id,
            order_data: currentOrder
        };

        const result = await fetch('/verify-payment', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCSRFToken()
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
            
            // Redirect to order confirmed page
            window.location.href = '/order-confirmed';
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

// Admin Login Functionality
function handleAdminLogin() {
    const loginForm = document.getElementById('loginForm');
    if (!loginForm) return;

    const errorAlert = document.getElementById('errorAlert');
    const errorMessage = document.getElementById('errorMessage');

    loginForm.addEventListener('submit', function(e) {
        e.preventDefault();
        
        if (!loginForm.checkValidity()) {
            e.stopPropagation();
            loginForm.classList.add('was-validated');
            return;
        }

        const formData = new FormData(loginForm);
        
        fetch('/admin/login', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
            },
            body: new URLSearchParams(formData)
        })
        .then(response => {
            if (!response.ok) {
                return response.json().then(err => Promise.reject(err));
            }
            return response.json();
        })
        .then(data => {
            if (data.success) {
                window.location.href = data.redirect;
            } else {
                errorMessage.textContent = data.message;
                errorAlert.classList.remove('d-none');
            }
        })
        .catch(error => {
            errorMessage.textContent = error.message || 'Login failed. Please check your credentials.';
            errorAlert.classList.remove('d-none');
            console.error('Login error:', error);
        });
    });
}

// Admin Order Management
function handleOrderDeletion() {
    const deleteButtons = document.querySelectorAll('.delete-order');
    const deleteModal = document.getElementById('deleteOrderModal');
    const confirmDeleteBtn = document.getElementById('confirmDelete');
    const cancelDeleteBtn = document.getElementById('cancelDelete');
    const orderIdInput = document.getElementById('orderIdToDelete');
    const errorAlert = document.getElementById('errorAlert');
    const errorMessage = document.getElementById('errorMessage');

    // Only proceed if we're on the admin dashboard
    if (!deleteModal || !confirmDeleteBtn || !orderIdInput) {
        return;
    }

    deleteButtons.forEach(button => {
        button.addEventListener('click', function() {
            const orderId = this.getAttribute('data-order-id');
            orderIdInput.value = orderId;
        });
    });

    confirmDeleteBtn.addEventListener('click', async function() {
        const orderId = orderIdInput.value;
        if (!orderId) return;

        try {
            const response = await fetch(`/admin/api/order/${orderId}`, {
                method: 'DELETE',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCSRFToken()
                }
            });

            const data = await response.json();
            
            if (data.success) {
                // Remove the order row from the table
                const orderRow = document.querySelector(`tr[data-order-id="${orderId}"]`);
                if (orderRow) {
                    orderRow.remove();
                }
                // Close the modal
                const modal = bootstrap.Modal.getInstance(deleteModal);
                modal.hide();
                showNotification('Order deleted successfully', 'success');
            } else {
                if (errorAlert && errorMessage) {
                    errorMessage.textContent = data.error || 'Failed to delete order';
                    errorAlert.classList.remove('d-none');
                }
            }
        } catch (error) {
            console.error('Error deleting order:', error);
            if (errorAlert && errorMessage) {
                errorMessage.textContent = 'An error occurred while deleting the order';
                errorAlert.classList.remove('d-none');
            }
        }
    });

    if (cancelDeleteBtn) {
        cancelDeleteBtn.addEventListener('click', function() {
            if (errorAlert) {
                errorAlert.classList.add('d-none');
            }
        });
    }
}

// Initialize
document.addEventListener('DOMContentLoaded', function() {
    updateCartCount();

    // Initialize admin login if on login page
    handleAdminLogin();

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

    handleOrderDeletion();
});

document.getElementById('checkout-form').addEventListener('submit', async function(e) {
    e.preventDefault();
    
    const formData = {
        name: document.getElementById('name').value,
        email: document.getElementById('email').value,
        phone: document.getElementById('phone').value,
        address: document.getElementById('address').value,
        pincode: document.getElementById('pincode').value,
        amount: parseFloat(document.getElementById('total_amount').value),
        items: JSON.parse(localStorage.getItem('cart')) || []
    };

    try {
        const response = await fetch('/checkout', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            },
            body: JSON.stringify(formData)
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.message || 'Checkout failed');
        }

        const data = await response.json();
        if (data.success) {
            // Store current order data for payment verification
            formData.order_id = data.order_id;  // Add the order_id to the form data
            localStorage.setItem('currentOrder', JSON.stringify(formData));
            
            // Check if Razorpay is loaded, if not load it
            if (typeof Razorpay === 'undefined') {
                const script = document.createElement('script');
                script.src = 'https://checkout.razorpay.com/v1/checkout.js';
                script.onload = function() {
                    initializeRazorpay(data);
                };
                document.head.appendChild(script);
            } else {
                initializeRazorpay(data);
            }
        }
    } catch (error) {
        console.error('Checkout error:', error);
        alert(error.message || 'An error occurred during checkout');
    }
});

function getCSRFToken() {
    const token = document.querySelector('meta[name="csrf-token"]');
    return token ? token.getAttribute('content') : '';
} 