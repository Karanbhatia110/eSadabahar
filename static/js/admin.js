document.addEventListener('DOMContentLoaded', function() {
    // Initial fetch of orders
    fetchOrders();

    // Load products and categories for product management
    fetchAdminProducts();
    fetchCategoriesAndPopulate();

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

// ---------------- Product & Category Management ----------------
let productModalInstance = null;
let categoryModalInstance = null;

function openAddProductModal() {
    document.getElementById('productForm').reset();
    document.getElementById('productId').value = '';
    document.getElementById('productModalTitle').textContent = 'Add Product';
    fetchCategoriesAndPopulate();
    setupImageInputs();
    if (!productModalInstance) {
        productModalInstance = new bootstrap.Modal(document.getElementById('productModal'));
    }
    productModalInstance.show();
}

function openEditProductModal(product) {
    document.getElementById('productId').value = product.id;
    document.getElementById('productName').value = product.name || '';
    document.getElementById('productPrice').value = product.price || 0;
    document.getElementById('productDescription').value = product.description || '';
    document.getElementById('productImageUrl').value = product.image_url || '';
    document.getElementById('productStock').value = product.stock || 0;
    document.getElementById('productModalTitle').textContent = 'Edit Product';
    fetchCategoriesAndPopulate(product.category);
    setupImageInputs(product.image_url || '');
    if (!productModalInstance) {
        productModalInstance = new bootstrap.Modal(document.getElementById('productModal'));
    }
    productModalInstance.show();
}

function submitProductForm() {
    const id = document.getElementById('productId').value;
    const payload = {
        name: document.getElementById('productName').value.trim(),
        category: document.getElementById('productCategory').value,
        price: parseFloat(document.getElementById('productPrice').value),
        description: document.getElementById('productDescription').value.trim(),
        image_url: document.getElementById('productImageUrl').value.trim(),
        stock: parseInt(document.getElementById('productStock').value || '0', 10)
    };

    if (!payload.name || !payload.category || isNaN(payload.price) || !payload.description || !payload.image_url) {
        alert('Please fill all required fields');
        return;
    }

    const url = id ? `/admin/api/products/${id}` : '/admin/api/products';
    const method = id ? 'PUT' : 'POST';

    fetch(url, {
        method,
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
    })
    .then(r => r.json())
    .then(data => {
        if (data.success) {
            if (productModalInstance) bootstrap.Modal.getInstance(document.getElementById('productModal')).hide();
            fetchAdminProducts();
        } else {
            alert(data.error || 'Failed to save product');
        }
    })
    .catch(err => alert('Failed to save product'));
}

function fetchAdminProducts() {
    fetch('/admin/api/products')
        .then(r => r.json())
        .then(data => {
            if (!data.success) return;
            // Desktop table
            const tbody = document.getElementById('productsTableBody');
            if (tbody) {
                tbody.innerHTML = '';
                data.products.forEach(p => {
                    const tr = document.createElement('tr');
                    const stockBadge = p.stock > 0 ? '<span class="badge bg-success">In Stock</span>' : '<span class="badge bg-secondary">Out of Stock</span>';
                    tr.innerHTML = `
                        <td>${p.name}</td>
                        <td>${p.category}</td>
                        <td>₹${p.price.toFixed(2)}</td>
                        <td>${stockBadge} <span class="ms-2 text-muted">(${p.stock})</span></td>
                        <td class="text-nowrap">
                            <button class="btn btn-sm btn-primary me-1" data-action="edit"><i class="fas fa-edit"></i></button>
                            <button class="btn btn-sm btn-${p.stock > 0 ? 'warning' : 'success'} me-1" data-action="toggle-stock">
                                <i class="fas fa-${p.stock > 0 ? 'ban' : 'check'}"></i> ${p.stock > 0 ? 'Mark OOS' : 'Mark In-Stock'}
                            </button>
                            <button class="btn btn-sm btn-danger" data-action="delete"><i class="fas fa-trash"></i></button>
                        </td>
                    `;
                    tr.querySelector('[data-action="edit"]').addEventListener('click', () => openEditProductModal(p));
                    tr.querySelector('[data-action="toggle-stock"]').addEventListener('click', () => toggleStock(p));
                    tr.querySelector('[data-action="delete"]').addEventListener('click', () => deleteProduct(p));
                    tbody.appendChild(tr);
                });
            }

            // Mobile cards
            const listMobile = document.getElementById('productsListMobile');
            if (listMobile) {
                listMobile.innerHTML = '';
                data.products.forEach(p => {
                    const card = document.createElement('div');
                    card.className = 'card mb-3';
                    const stockBadge = p.stock > 0 ? '<span class="badge bg-success">In Stock</span>' : '<span class="badge bg-secondary">Out of Stock</span>';
                    card.innerHTML = `
                        <div class="card-body">
                            <div class="d-flex align-items-start justify-content-between">
                                <div class="flex-grow-1 me-3">
                                    <h6 class="mb-1">${p.name}</h6>
                                    <div class="text-muted small mb-1">${p.category}</div>
                                    <div class="fw-semibold mb-2">₹${p.price.toFixed(2)}</div>
                                    <div>${stockBadge} <span class="ms-2 text-muted">(${p.stock})</span></div>
                                </div>
                                <img src="${p.image_url || ''}" alt="${p.name}" class="rounded" style="width:72px;height:72px;object-fit:cover" onerror="this.style.display='none'">
                            </div>
                            <div class="mt-3 d-flex gap-2">
                                <button class="btn btn-sm btn-primary flex-fill" data-action="edit"><i class="fas fa-edit me-1"></i>Edit</button>
                                <button class="btn btn-sm btn-${p.stock > 0 ? 'warning' : 'success'} flex-fill" data-action="toggle-stock">
                                    <i class="fas fa-${p.stock > 0 ? 'ban' : 'check'} me-1"></i>${p.stock > 0 ? 'Mark OOS' : 'Mark In-Stock'}
                                </button>
                                <button class="btn btn-sm btn-danger flex-fill" data-action="delete"><i class="fas fa-trash me-1"></i>Delete</button>
                            </div>
                        </div>
                    `;
                    card.querySelector('[data-action="edit"]').addEventListener('click', () => openEditProductModal(p));
                    card.querySelector('[data-action="toggle-stock"]').addEventListener('click', () => toggleStock(p));
                    card.querySelector('[data-action="delete"]').addEventListener('click', () => deleteProduct(p));
                    listMobile.appendChild(card);
                });
            }
        })
        .catch(() => {});
}

function toggleStock(p) {
    const newStock = p.stock > 0 ? 0 : 1;
    fetch(`/admin/api/products/${p.id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ stock: newStock })
    })
    .then(r => r.json())
    .then(data => {
        if (data.success) fetchAdminProducts();
        else alert(data.error || 'Failed to update stock');
    })
    .catch(() => alert('Failed to update stock'));
}

function deleteProduct(p) {
    if (!confirm('Delete this product?')) return;
    fetch(`/admin/api/products/${p.id}`, { method: 'DELETE' })
        .then(r => r.json())
        .then(data => {
            if (data.success) fetchAdminProducts();
            else alert(data.error || 'Failed to delete product');
        })
        .catch(() => alert('Failed to delete product'));
}

function openAddCategoryModal() {
    document.getElementById('categoryForm').reset();
    if (!categoryModalInstance) {
        categoryModalInstance = new bootstrap.Modal(document.getElementById('categoryModal'));
    }
    categoryModalInstance.show();
}

function submitCategoryForm() {
    const name = document.getElementById('categoryName').value.trim();
    if (!name) return alert('Category name required');
    fetch('/admin/api/categories', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name })
    })
    .then(r => r.json())
    .then(data => {
        if (data.success) {
            bootstrap.Modal.getInstance(document.getElementById('categoryModal')).hide();
            fetchCategoriesAndPopulate();
        } else {
            alert(data.error || 'Failed to create category');
        }
    })
    .catch(() => alert('Failed to create category'));
}

function fetchCategoriesAndPopulate(selected = '') {
    fetch('/admin/api/categories')
        .then(r => r.json())
        .then(data => {
            if (!data.success) return;
            const select = document.getElementById('productCategory');
            if (!select) return;
            const previous = select.value;
            select.innerHTML = '';
            // merge categories from backend (already includes products + stored)
            const categories = (data.categories || []).map(c => typeof c === 'string' ? c : c.name);
            // Fallback to default if empty
            const finalList = categories && categories.length ? categories : ['bouquet', 'cake_500g', 'cake_1kg', 'chocolate', 'plant', 'combo'];
            finalList.forEach(name => {
                const opt = document.createElement('option');
                opt.value = name;
                opt.textContent = name;
                select.appendChild(opt);
            });
            if (selected) select.value = selected;
            else if (previous) select.value = previous;
        })
        .catch(() => {
            // Populate with default set on error
            const select = document.getElementById('productCategory');
            if (!select) return;
            const defaultCategories = ['bouquet', 'cake_500g', 'cake_1kg', 'chocolate', 'plant', 'combo'];
            select.innerHTML = defaultCategories.map(c => `<option value="${c}">${c}</option>`).join('');
            if (selected) select.value = selected;
        });
}

function setupImageInputs(initialUrl = '') {
    const urlInput = document.getElementById('productImageUrl');
    const fileInput = document.getElementById('productImageFile');
    const preview = document.getElementById('productImagePreview');
    if (!urlInput || !fileInput || !preview) return;

    function showPreview(src) {
        if (src) {
            preview.src = src;
            preview.style.display = 'block';
        } else {
            preview.src = '';
            preview.style.display = 'none';
        }
    }

    // initialize preview from provided url
    showPreview(initialUrl || urlInput.value);

    urlInput.addEventListener('input', () => {
        showPreview(urlInput.value.trim());
    });

    fileInput.onchange = async () => {
        const file = fileInput.files && fileInput.files[0];
        if (!file) return;
        const form = new FormData();
        form.append('file', file);
        try {
            const res = await fetch('/admin/api/upload', { method: 'POST', body: form });
            const data = await res.json();
            if (data.success) {
                // Prefer persistent media URL (GridFS) if available
                urlInput.value = data.url;
                showPreview(data.url);
            } else {
                alert(data.error || 'Upload failed');
            }
        } catch (e) {
            alert('Upload failed');
        }
    };
}
