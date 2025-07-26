document.addEventListener('DOMContentLoaded', function() {
    // Add to cart functionality
    document.querySelectorAll('.add-to-cart').forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            const productId = this.dataset.productId;
            
            fetch('/api/cart', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-Requested-With': 'XMLHttpRequest'
                },
                body: JSON.stringify({
                    product_id: productId,
                    quantity: 1
                })
            })
            .then(response => response.json())
            .then(data => {
                if (data.message) {
                    showAlert('Product added to cart!', 'success');
                    updateCartCount();
                } else {
                    showAlert('Error adding product to cart', 'danger');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                showAlert('An error occurred', 'danger');
            });
        });
    });
    
    // Remove from cart functionality
    document.querySelectorAll('.remove-from-cart').forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            const cartItemId = this.dataset.cartItemId;
            
            if (confirm('Are you sure you want to remove this item from your cart?')) {
                fetch('/api/cart', {
                    method: 'DELETE',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-Requested-With': 'XMLHttpRequest'
                    },
                    body: JSON.stringify({
                        cart_item_id: cartItemId
                    })
                })
                .then(response => response.json())
                .then(data => {
                    if (data.message) {
                        showAlert('Item removed from cart', 'success');
                        location.reload();
                    } else {
                        showAlert('Error removing item from cart', 'danger');
                    }
                })
                .catch(error => {
                    console.error('Error:', error);
                    showAlert('An error occurred', 'danger');
                });
            }
        });
    });
    
    // Update cart count on page load
    updateCartCount();
    
    // Search form submission
    const searchForm = document.querySelector('#search-form');
    if (searchForm) {
        searchForm.addEventListener('submit', function(e) {
            e.preventDefault();
            const searchInput = this.querySelector('input[name="search"]');
            const categorySelect = this.querySelector('select[name="category"]');
            
            let url = '/products?';
            if (searchInput.value) {
                url += `search=${encodeURIComponent(searchInput.value)}&`;
            }
            if (categorySelect.value) {
                url += `category=${encodeURIComponent(categorySelect.value)}`;
            }
            
            window.location.href = url;
        });
    }
    
    function updateCartCount() {
        fetch('/api/cart')
            .then(response => response.json())
            .then(data => {
                const cartCount = data.cart_items.reduce((total, item) => total + item.quantity, 0);
                const cartBadge = document.querySelector('.cart-count');
                if (cartBadge) {
                    cartBadge.textContent = cartCount;
                    cartBadge.style.display = cartCount > 0 ? 'inline-block' : 'none';
                }
            })
            .catch(error => {
                console.error('Error fetching cart:', error);
            });
    }
    
    function showAlert(message, type) {
        const alertDiv = document.createElement('div');
        alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
        alertDiv.role = 'alert';
        alertDiv.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        const container = document.querySelector('main.container') || document.querySelector('main');
        if (container) {
            container.prepend(alertDiv);
            
            // Auto dismiss after 3 seconds
            setTimeout(() => {
                alertDiv.classList.remove('show');
                setTimeout(() => alertDiv.remove(), 150);
            }, 3000);
        }
    }
});
