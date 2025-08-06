// Cart Management
let cart = [];

// Initialize cart from localStorage with error handling
function initializeCart() {
    const savedCart = localStorage.getItem('cart');
    console.log('initializeCart - savedCart:', savedCart);
    
    if (savedCart) {
        try {
            cart = JSON.parse(savedCart);
            console.log('initializeCart - parsed cart:', cart);
            
            // Ensure cart is an array
            if (!Array.isArray(cart)) {
                console.log('initializeCart - cart is not array, resetting');
                cart = [];
                localStorage.setItem('cart', JSON.stringify(cart));
            } else {
                console.log('initializeCart - cart is valid array with', cart.length, 'items');
            }
        } catch (error) {
            console.error('Error parsing cart from localStorage:', error);
            cart = [];
            localStorage.setItem('cart', JSON.stringify(cart));
        }
    } else {
        console.log('initializeCart - no saved cart found');
        cart = [];
    }
    
    console.log('initializeCart - final cart:', cart);
}

// Initialize cart immediately
initializeCart();

// Test function to debug cart issues
function testCart() {
    console.log('=== CART DEBUG TEST ===');
    console.log('Cart array:', cart);
    console.log('Cart length:', cart.length);
    console.log('localStorage cart:', localStorage.getItem('cart'));
    
    if (cart.length > 0) {
        console.log('First item:', cart[0]);
        console.log('First item ID type:', typeof cart[0].id);
        console.log('First item ID value:', cart[0].id);
    }
}

// Test function to add a test item to cart
function addTestItem() {
    console.log('Adding test item to cart...');
    addToCart('test-1', 'Test Product', 100);
    console.log('Cart after adding test item:', cart);
}

function updateCartCount() {
    const cartCount = document.getElementById('cart-count');
    const floatingCartCount = document.getElementById('floatingCartCount');
    const totalItems = cart.reduce((total, item) => total + item.quantity, 0);
    
    if (cartCount) {
        cartCount.textContent = totalItems;
    }
    
    if (floatingCartCount) {
        floatingCartCount.textContent = totalItems;
    }
}

function addToCart(productId, name, price) {
    // Convert productId to string for consistent storage
    const stringProductId = String(productId);
    console.log('Adding to cart:', { productId, stringProductId, name, price });
    
    const existingItem = cart.find(item => String(item.id) === stringProductId);
    
    if (existingItem) {
        existingItem.quantity += 1;
        console.log('Updated existing item quantity:', existingItem);
    } else {
        const newItem = {
            id: stringProductId,
            name: name,
            price: price,
            quantity: 1
        };
        cart.push(newItem);
        console.log('Added new item to cart:', newItem);
    }
    
    localStorage.setItem('cart', JSON.stringify(cart));
    updateCartCount();
    updateCartDisplay();
    
    // Show notification
    showNotification(`${name} added to cart!`, 'success');
}

function removeFromCart(productId) {
    const stringProductId = String(productId);
    const item = cart.find(item => String(item.id) === stringProductId);
    const itemName = item ? item.name : 'Item';
    
    cart = cart.filter(item => String(item.id) !== stringProductId);
    localStorage.setItem('cart', JSON.stringify(cart));
    updateCartCount();
    updateCartDisplay();
    
    // Show notification
    showNotification(`${itemName} removed from cart!`, 'info');
}

function updateQuantity(productId, change) {
    console.log('updateQuantity called with:', { productId, change, cartLength: cart.length });
    
    // Convert productId to string for consistent comparison
    const stringProductId = String(productId);
    const item = cart.find(item => String(item.id) === stringProductId);
    
    console.log('Found item:', item);
    
    if (item) {
        const newQuantity = item.quantity + change;
        console.log('New quantity will be:', newQuantity);
        
        if (newQuantity <= 0) {
            // Remove the item completely
            console.log('Removing item from cart');
            cart = cart.filter(item => String(item.id) !== stringProductId);
            localStorage.setItem('cart', JSON.stringify(cart));
            updateCartCount();
            updateCartDisplay();
            
            // Show notification
            showNotification(`${item.name} removed from cart!`, 'info');
        } else {
            // Update quantity
            console.log('Updating quantity to:', newQuantity);
            const oldQuantity = item.quantity;
            item.quantity = newQuantity;
            localStorage.setItem('cart', JSON.stringify(cart));
            updateCartCount();
            updateCartDisplay();
            
            // Show notification if quantity changed
            if (oldQuantity !== item.quantity) {
                showNotification(`${item.name} quantity updated to ${item.quantity}!`, 'info');
            }
        }
    } else {
        console.log('Item not found in cart');
        console.log('Cart items:', cart);
    }
}

// Cart display function for cart page
function updateCartDisplay() {
    const cartItems = document.getElementById('cart-items');
    const subtotalElement = document.getElementById('subtotal');
    const deliveryFeeElement = document.getElementById('delivery-fee');
    const totalElement = document.getElementById('total');

    // Only proceed if we're on the cart page
    if (!cartItems) {
        console.log('updateCartDisplay: Not on cart page, cartItems not found');
        return;
    }

    console.log('updateCartDisplay called, cart:', cart);
    console.log('Cart length:', cart.length);

    if (!cart || cart.length === 0) {
        cartItems.innerHTML = '<p>Your cart is empty</p>';
        if (subtotalElement) subtotalElement.textContent = '₹0.00';
        if (deliveryFeeElement) deliveryFeeElement.textContent = '₹0.00';
        if (totalElement) totalElement.textContent = '₹0.00';
        return;
    }

    let subtotal = 0;
    cartItems.innerHTML = cart.map(item => {
        subtotal += item.price * item.quantity;
        return `
            <div class="card mb-3">
                <div class="card-body">
                    <div class="d-flex justify-content-between align-items-center">
                        <div>
                            <h5 class="card-title">${item.name}</h5>
                            <p class="card-text">₹${item.price.toFixed(2)}</p>
                        </div>
                        <div class="d-flex align-items-center">
                            <button class="btn btn-sm btn-outline-secondary me-2" onclick="updateQuantity('${item.id}', -1)" data-product-id="${item.id}">-</button>
                            <span>${item.quantity}</span>
                            <button class="btn btn-sm btn-outline-secondary ms-2" onclick="updateQuantity('${item.id}', 1)" data-product-id="${item.id}">+</button>
                        </div>
                    </div>
                </div>
            </div>
        `;
    }).join('');

    const deliveryFee = subtotal > 1000 ? 0 : 50;
    const total = subtotal + deliveryFee;

    if (subtotalElement) subtotalElement.textContent = `₹${subtotal.toFixed(2)}`;
    if (deliveryFeeElement) deliveryFeeElement.textContent = `₹${deliveryFee.toFixed(2)}`;
    if (totalElement) totalElement.textContent = `₹${total.toFixed(2)}`;
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
    notification.style.minWidth = '300px';
    notification.style.maxWidth = '500px';
    notification.innerHTML = `
        <i class="fas fa-${type === 'success' ? 'check-circle' : type === 'danger' ? 'exclamation-circle' : 'info-circle'}"></i>
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
    `;

    container.insertBefore(notification, container.firstChild);

    // Auto-remove after 3 seconds
    setTimeout(() => {
        if (notification.parentNode) {
            notification.remove();
        }
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
document.addEventListener('DOMContentLoaded', function() {
    const loginForm = document.getElementById('loginForm');
    if (loginForm) {
        loginForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            if (!loginForm.checkValidity()) {
                e.stopPropagation();
                loginForm.classList.add('was-validated');
                return;
            }

            const formData = {
                username: document.getElementById('username').value,
                password: document.getElementById('password').value
            };
            
            fetch('/admin/login', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(formData)
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
});

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

// Dashboard Functions
function fetchOrders() {
    // Get filter values
    const startDate = document.getElementById('startDate').value;
    const endDate = document.getElementById('endDate').value;
    const minPrice = document.getElementById('minPrice').value;
    const maxPrice = document.getElementById('maxPrice').value;

    // Build query string
    const params = new URLSearchParams();
    if (startDate) params.append('start_date', startDate);
    if (endDate) params.append('end_date', endDate);
    if (minPrice) params.append('min_price', minPrice);
    if (maxPrice) params.append('max_price', maxPrice);

    // Fetch orders with filters
    fetch(`/admin/api/orders?${params.toString()}`)
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Update stats
                document.getElementById('totalOrders').textContent = data.total_orders;
                document.getElementById('totalRevenue').textContent = `₹${data.total_revenue.toFixed(2)}`;
                document.getElementById('pendingOrders').textContent = data.pending_orders;
                document.getElementById('deliveredOrders').textContent = data.delivered_orders;

                // Update orders table
                const tbody = document.getElementById('ordersTableBody');
                tbody.innerHTML = '';
                data.orders.forEach(order => {
                    const orderDate = new Date(order.created_at);
                    const formattedDateTime = orderDate.toLocaleString('en-IN', {
                        day: '2-digit',
                        month: '2-digit',
                        year: 'numeric',
                        hour: '2-digit',
                        minute: '2-digit',
                        hour12: true
                    });
                    
                    const row = document.createElement('tr');
                    row.innerHTML = `
                        <td>#${order.id}</td>
                        <td>${order.customer_name}</td>
                        <td>₹${order.total_amount.toFixed(2)}</td>
                        <td><span class="badge bg-${getStatusColor(order.status)}">${order.status}</span></td>
                        <td><span class="badge bg-${getPaymentStatusColor(order.payment_status)}">${order.payment_status}</span></td>
                        <td>${formattedDateTime}</td>
                        <td>${new Date(order.delivery_date).toLocaleDateString()}</td>
                        <td class="text-nowrap">
                            <button class="btn btn-sm btn-info me-1" onclick="viewOrder(${order.id})">
                                <i class="fas fa-eye"></i>
                            </button>
                            <button class="btn btn-sm btn-warning me-1" onclick="showUpdateStatusModal(${order.id})">
                                <i class="fas fa-edit"></i>
                            </button>
                            <button class="btn btn-sm btn-danger" onclick="showDeleteModal(${order.id})">
                                <i class="fas fa-trash"></i>
                            </button>
                        </td>
                    `;
                    tbody.appendChild(row);
                });
            }
        })
        .catch(error => console.error('Error:', error));
}

function applyFilters() {
    // Validate date range
    const startDate = document.getElementById('startDate').value;
    const endDate = document.getElementById('endDate').value;
    
    if (startDate && endDate && new Date(startDate) > new Date(endDate)) {
        showNotification('Start date cannot be after end date', 'warning');
        return;
    }

    // Validate price range
    const minPrice = document.getElementById('minPrice').value;
    const maxPrice = document.getElementById('maxPrice').value;
    
    if (minPrice && maxPrice && parseFloat(minPrice) > parseFloat(maxPrice)) {
        showNotification('Minimum price cannot be greater than maximum price', 'warning');
        return;
    }

    // Apply filters
    fetchOrders();
}

function getStatusColor(status) {
    switch (status) {
        case 'pending': return 'warning';
        case 'processing': return 'info';
        case 'delivered': return 'success';
        case 'cancelled': return 'danger';
        default: return 'secondary';
    }
}

function getPaymentStatusColor(status) {
    switch (status) {
        case 'pending': return 'warning';
        case 'completed': return 'success';
        case 'failed': return 'danger';
        default: return 'secondary';
    }
}

function toggleFilters() {
    const filterControls = document.getElementById('filterControls');
    if (filterControls.style.display === 'none') {
        filterControls.style.display = 'flex';
    } else {
        filterControls.style.display = 'none';
    }
}

function viewOrder(orderId) {
    fetch(`/admin/api/order/${orderId}`)
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                const order = data;
                const orderDate = new Date(order.created_at);
                const formattedDateTime = orderDate.toLocaleString('en-IN', {
                    day: '2-digit',
                    month: '2-digit',
                    year: 'numeric',
                    hour: '2-digit',
                    minute: '2-digit',
                    hour12: true
                });
                
                const details = document.getElementById('orderDetails');
                details.innerHTML = `
                    <div class="row">
                        <div class="col-md-6">
                            <h6>Customer Information</h6>
                            <p><strong>Name:</strong> ${order.customer_name}</p>
                            <p><strong>Email:</strong> ${order.email}</p>
                            <p><strong>Phone:</strong> ${order.phone}</p>
                            <p><strong>Address:</strong> ${order.address}</p>
                            <p><strong>Pincode:</strong> ${order.pincode}</p>
                            ${order.instruction ? `<p><strong>Instructions:</strong> ${order.instruction}</p>` : ''}
                        </div>
                        <div class="col-md-6">
                            <h6>Order Information</h6>
                            <p><strong>Order ID:</strong> #${order.id}</p>
                            <p><strong>Status:</strong> <span class="badge bg-${getStatusColor(order.status)}">${order.status}</span></p>
                            <p><strong>Payment Status:</strong> <span class="badge bg-${getPaymentStatusColor(order.payment_status)}">${order.payment_status}</span></p>
                            <p><strong>Order Date:</strong> ${formattedDateTime}</p>
                            <p><strong>Delivery Date:</strong> ${new Date(order.delivery_date).toLocaleDateString()}</p>
                        </div>
                    </div>
                    <div class="row mt-3">
                        <div class="col-12">
                            <h6>Order Items</h6>
                            <table class="table table-sm">
                                <thead>
                                    <tr>
                                        <th>Product</th>
                                        <th>Quantity</th>
                                        <th>Price</th>
                                        <th>Total</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    ${order.items.map(item => `
                                        <tr>
                                            <td>${item.product_name}</td>
                                            <td>${item.quantity}</td>
                                            <td>₹${item.price.toFixed(2)}</td>
                                            <td>₹${(item.quantity * item.price).toFixed(2)}</td>
                                        </tr>
                                    `).join('')}
                                </tbody>
                                <tfoot>
                                    <tr>
                                        <td colspan="3" class="text-end"><strong>Total Amount:</strong></td>
                                        <td><strong>₹${order.total_amount.toFixed(2)}</strong></td>
                                    </tr>
                                </tfoot>
                            </table>
                        </div>
                    </div>
                `;
                new bootstrap.Modal(document.getElementById('viewOrderModal')).show();
            }
        })
        .catch(error => console.error('Error:', error));
}

function showUpdateStatusModal(orderId) {
    document.getElementById('updateOrderId').value = orderId;
    const modal = new bootstrap.Modal(document.getElementById('updateStatusModal'));
    modal.show();
}

function submitStatusUpdate() {
    const orderId = document.getElementById('updateOrderId').value;
    const status = document.getElementById('status').value;

    fetch(`/admin/api/order/${orderId}/status`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ status })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showNotification('Order status updated successfully', 'success');
            fetchOrders();
            bootstrap.Modal.getInstance(document.getElementById('updateStatusModal')).hide();
        } else {
            showNotification(data.error || 'Failed to update status', 'danger');
        }
    })
    .catch(error => {
        console.error('Error updating order status:', error);
        showNotification('Failed to update order status', 'danger');
    });
}

function showDeleteModal(orderId) {
    document.getElementById('orderIdToDelete').value = orderId;
    const modal = new bootstrap.Modal(document.getElementById('deleteOrderModal'));
    modal.show();
}

function deleteOrder() {
    const orderId = document.getElementById('orderIdToDelete').value;
    console.log('Attempting to delete order with ID:', orderId); // Debugging log

    fetch(`/admin/api/order/${orderId}`, {
        method: 'DELETE'
    })
    .then(response => {
        console.log('Delete response status:', response.status); // Debugging log
        return response.json();
    })
    .then(data => {
        console.log('Delete response data:', data); // Debugging log
        if (data.success) {
            showNotification('Order deleted successfully', 'success');
            fetchOrders();
            bootstrap.Modal.getInstance(document.getElementById('deleteOrderModal')).hide();
        } else {
            showNotification(data.message || 'Failed to delete order', 'danger');
        }
    })
    .catch(error => {
        console.error('Error deleting order:', error);
        showNotification('Failed to delete order', 'danger');
    });
}

// Initialize
document.addEventListener('DOMContentLoaded', function() {
    console.log('DOMContentLoaded - Initializing cart...');
    console.log('Current cart before initialization:', cart);
    
    // Test cart functionality
    testCart();
    
    updateCartCount();
    updateCartDisplay(); // Add this line to initialize cart display
    
    console.log('Cart after initialization:', cart);

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

    const checkoutForm = document.getElementById('checkout-form');
    if (checkoutForm) {
        checkoutForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const formData = {
                name: document.getElementById('name').value,
                email: document.getElementById('email').value,
                phone: document.getElementById('phone').value,
                address: document.getElementById('address').value,
                pincode: document.getElementById('pincode').value,
                amount: parseFloat(document.getElementById('total_amount').value),
                delivery_date: document.getElementById('delivery_date').value,
                instruction: document.getElementById('instruction').value,
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
    }

    fetchOrders();
});

function getCSRFToken() {
    const token = document.querySelector('meta[name="csrf-token"]');
    return token ? token.getAttribute('content') : '';
} 
