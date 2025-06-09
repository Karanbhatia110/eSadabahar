document.addEventListener('DOMContentLoaded', function() {
    // Initial fetch of orders
    fetchOrders();

    // Handle delete orders
    const deleteButtons = document.querySelectorAll('.delete-btn');
    deleteButtons.forEach(button => {
        button.addEventListener('click', function() {
            const orderId = this.dataset.orderId;
            
            if (confirm('Are you sure you want to delete this order? This action cannot be undone.')) {
                deleteOrder(orderId);
            }
        });
    });
});

function fetchOrders() {
    fetch('/admin/api/orders')
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
                    const row = document.createElement('tr');
                    row.innerHTML = `
                        <td>#${order.id}</td>
                        <td>${order.customer_name}</td>
                        <td>₹${order.total_amount.toFixed(2)}</td>
                        <td><span class="badge bg-${getStatusColor(order.status)}">${order.status}</span></td>
                        <td><span class="badge bg-${getPaymentStatusColor(order.payment_status)}">${order.payment_status}</span></td>
                        <td>${new Date(order.created_at).toLocaleString()}</td>
                        <td>${new Date(order.delivery_date).toLocaleDateString()}</td>
                        <td>
                            <div class="btn-group">
                                <button type="button" class="btn btn-sm btn-info me-1" onclick="viewOrder('${order.id}')">
                                    <i class="fas fa-eye"></i>
                                </button>
                                <button type="button" class="btn btn-sm btn-primary me-1" onclick="showUpdateStatusModal('${order.id}', '${order.status}')">
                                    <i class="fas fa-edit"></i> Update Status
                                </button>
                                <button class="btn btn-sm btn-danger delete-btn" data-order-id="${order.id}">
                                    <i class="fas fa-trash"></i>
                                </button>
                            </div>
                        </td>
                    `;
                    tbody.appendChild(row);
                });

                // Reattach event listeners
                attachEventListeners();
            }
        })
        .catch(error => console.error('Error:', error));
}

function showUpdateStatusModal(orderId, currentStatus) {
    // Store the order ID in the hidden input
    document.getElementById('updateOrderId').value = orderId;
    // Set the current status in the select dropdown
    const statusSelect = document.getElementById('status');
    statusSelect.value = currentStatus;
    // Show the modal
    new bootstrap.Modal(document.getElementById('updateStatusModal')).show();
}

function submitStatusUpdate() {
    const orderId = document.getElementById('updateOrderId').value;
    const status = document.getElementById('status').value;
    
    if (!orderId || !status) {
        alert('Please select a status');
        return;
    }

    updateOrderStatus(orderId, status);
}

function updateOrderStatus(orderId, status) {
    // Log the values being sent
    console.log('Updating order:', orderId, 'to status:', status);
    
    fetch(`/admin/api/order/${orderId}/status`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ status: status })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Close the modal
            bootstrap.Modal.getInstance(document.getElementById('updateStatusModal')).hide();
            // Show success message
            alert('Order status updated successfully!');
            // Refresh the orders list
            fetchOrders();
        } else {
            alert('Error updating order status: ' + (data.error || 'Unknown error'));
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Error updating order status. Please try again.');
    });
}

function viewOrder(orderId) {
    fetch(`/admin/api/order/${orderId}`)
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                const order = data;
                const details = document.getElementById('orderDetails');
                details.innerHTML = `
                    <div class="row">
                        <div class="col-md-6">
                            <h6>Customer Information</h6>
                            <p><strong>Name:</strong> ${order.customer_name}</p>
                            <p><strong>Email:</strong> ${order.email}</p>
                            <p><strong>Phone:</strong> ${order.phone}</p>
                        </div>
                        <div class="col-md-6">
                            <h6>Order Information</h6>
                            <p><strong>Order ID:</strong> #${order.id}</p>
                            <p><strong>Status:</strong> <span class="badge bg-${getStatusColor(order.status)}">${order.status}</span></p>
                            <p><strong>Payment Status:</strong> <span class="badge bg-${getPaymentStatusColor(order.payment_status)}">${order.payment_status}</span></p>
                            <p><strong>Order Date:</strong> ${new Date(order.created_at).toLocaleString()}</p>
                            <p><strong>Delivery Date:</strong> ${new Date(order.delivery_date).toLocaleDateString()}</p>
                        </div>
                    </div>
                    <div class="row mt-3">
                        <div class="col-12">
                            <h6>Delivery Address</h6>
                            <p>${order.address}</p>
                            <p><strong>Pincode:</strong> ${order.pincode}</p>
                        </div>
                    </div>
                    ${order.instruction ? `
                    <div class="row mt-3">
                        <div class="col-12">
                            <h6>Special Instructions</h6>
                            <div class="alert alert-info">
                                <i class="fas fa-info-circle me-2"></i>
                                ${order.instruction}
                            </div>
                        </div>
                    </div>
                    ` : ''}
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

function deleteOrder(orderId) {
    fetch(`/admin/api/order/${orderId}`, {
        method: 'DELETE'
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert('Order deleted successfully!');
            fetchOrders(); // Refresh the orders list
        } else {
            alert('Error deleting order: ' + data.error);
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Error deleting order. Please try again.');
    });
}

function getStatusColor(status) {
    switch (status.toLowerCase()) {
        case 'pending': return 'warning';
        case 'processing': return 'info';
        case 'out_for_delivery': return 'primary';
        case 'delivered': return 'success';
        case 'cancelled': return 'danger';
        default: return 'secondary';
    }
}

function getPaymentStatusColor(status) {
    switch (status.toLowerCase()) {
        case 'completed': return 'success';
        case 'pending': return 'warning';
        case 'failed': return 'danger';
        default: return 'secondary';
    }
}

function toggleFilters() {
    const filterControls = document.getElementById('filterControls');
    filterControls.style.display = filterControls.style.display === 'none' ? 'flex' : 'none';
}

function applyFilters() {
    const startDate = document.getElementById('startDate').value;
    const endDate = document.getElementById('endDate').value;
    const minPrice = document.getElementById('minPrice').value;
    const maxPrice = document.getElementById('maxPrice').value;

    let url = '/admin/api/orders?';
    if (startDate) url += `start_date=${startDate}&`;
    if (endDate) url += `end_date=${endDate}&`;
    if (minPrice) url += `min_price=${minPrice}&`;
    if (maxPrice) url += `max_price=${maxPrice}`;

    fetch(url)
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Update stats and table as in fetchOrders()
                document.getElementById('totalOrders').textContent = data.total_orders;
                document.getElementById('totalRevenue').textContent = `₹${data.total_revenue.toFixed(2)}`;
                document.getElementById('pendingOrders').textContent = data.pending_orders;
                document.getElementById('deliveredOrders').textContent = data.delivered_orders;

                const tbody = document.getElementById('ordersTableBody');
                tbody.innerHTML = '';
                data.orders.forEach(order => {
                    const row = document.createElement('tr');
                    row.innerHTML = `
                        <td>#${order.id}</td>
                        <td>${order.customer_name}</td>
                        <td>₹${order.total_amount.toFixed(2)}</td>
                        <td><span class="badge bg-${getStatusColor(order.status)}">${order.status}</span></td>
                        <td><span class="badge bg-${getPaymentStatusColor(order.payment_status)}">${order.payment_status}</span></td>
                        <td>${new Date(order.created_at).toLocaleString()}</td>
                        <td>${new Date(order.delivery_date).toLocaleDateString()}</td>
                        <td>
                            <div class="btn-group">
                                <button type="button" class="btn btn-sm btn-info me-1" onclick="viewOrder('${order.id}')">
                                    <i class="fas fa-eye"></i>
                                </button>
                                <button type="button" class="btn btn-sm btn-primary me-1" onclick="showUpdateStatusModal('${order.id}', '${order.status}')">
                                    <i class="fas fa-edit"></i> Update Status
                                </button>
                                <button class="btn btn-sm btn-danger delete-btn" data-order-id="${order.id}">
                                    <i class="fas fa-trash"></i>
                                </button>
                            </div>
                        </td>
                    `;
                    tbody.appendChild(row);
                });

                // Reattach event listeners
                attachEventListeners();
            }
        })
        .catch(error => console.error('Error:', error));
}

function attachEventListeners() {
    // Reattach event listeners for delete buttons
    document.querySelectorAll('.delete-btn').forEach(button => {
        button.addEventListener('click', function() {
            const orderId = this.dataset.orderId;
            
            if (confirm('Are you sure you want to delete this order? This action cannot be undone.')) {
                deleteOrder(orderId);
            }
        });
    });
} 