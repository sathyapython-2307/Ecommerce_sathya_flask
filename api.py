from flask import Blueprint, jsonify, request
from flask_login import current_user, login_required
from models import db, Product, CartItem
from datetime import datetime
from functools import wraps

api = Blueprint('api', __name__)

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_admin:
            return jsonify({'error': 'Admin access required'}), 403
        return f(*args, **kwargs)
    return decorated_function

@api.route('/products')
def get_products():
    search = request.args.get('search', '')
    category = request.args.get('category', '')
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 6, type=int)
    
    query = Product.query
    if search:
        query = query.filter(Product.name.ilike(f'%{search}%'))
    if category:
        query = query.filter_by(category=category)
    
    products = query.paginate(page=page, per_page=per_page)
    
    products_data = [{
        'id': product.id,
        'name': product.name,
        'description': product.description,
        'price': product.price,
        'image_url': product.image_url,
        'stock': product.stock,
        'category': product.category
    } for product in products.items]
    
    return jsonify({
        'products': products_data,
        'total': products.total,
        'pages': products.pages,
        'current_page': products.page
    })

@api.route('/products', methods=['POST'])
@admin_required
def create_product():
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    required_fields = ['name', 'description', 'price', 'image_url', 'stock', 'category']
    if not all(field in data for field in required_fields):
        return jsonify({'error': 'Missing required fields'}), 400
    
    try:
        product = Product(
            name=data['name'],
            description=data['description'],
            price=float(data['price']),
            image_url=data['image_url'],
            stock=int(data['stock']),
            category=data['category'],
            created_at=datetime.utcnow()
        )
        db.session.add(product)
        db.session.commit()
        return jsonify({'message': 'Product created successfully', 'product_id': product.id}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api.route('/products/<int:product_id>', methods=['PUT'])
@admin_required
def update_product(product_id):
    product = Product.query.get_or_404(product_id)
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    try:
        if 'name' in data:
            product.name = data['name']
        if 'description' in data:
            product.description = data['description']
        if 'price' in data:
            product.price = float(data['price'])
        if 'image_url' in data:
            product.image_url = data['image_url']
        if 'stock' in data:
            product.stock = int(data['stock'])
        if 'category' in data:
            product.category = data['category']
        
        db.session.commit()
        return jsonify({'message': 'Product updated successfully'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api.route('/products/<int:product_id>', methods=['DELETE'])
@admin_required
def delete_product_api(product_id):
    product = Product.query.get_or_404(product_id)
    
    try:
        db.session.delete(product)
        db.session.commit()
        return jsonify({'message': 'Product deleted successfully'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api.route('/cart', methods=['GET', 'POST', 'DELETE'])
@login_required
def manage_cart():
    if request.method == 'GET':
        cart_items = CartItem.query.filter_by(user_id=current_user.id).all()
        cart_data = [{
            'id': item.id,
            'product_id': item.product_id,
            'product_name': item.product.name,
            'product_price': item.product.price,
            'product_image': item.product.image_url,
            'quantity': item.quantity
        } for item in cart_items]
        
        total = sum(item.product.price * item.quantity for item in cart_items)
        return jsonify({'cart_items': cart_data, 'total': total})
    
    elif request.method == 'POST':
        data = request.get_json()
        product_id = data.get('product_id')
        quantity = data.get('quantity', 1)
        
        product = Product.query.get(product_id)
        if not product:
            return jsonify({'error': 'Product not found'}), 404
        
        # Check if item already in cart
        cart_item = CartItem.query.filter_by(
            user_id=current_user.id, 
            product_id=product_id
        ).first()
        
        if cart_item:
            cart_item.quantity += quantity
        else:
            cart_item = CartItem(
                user_id=current_user.id,
                product_id=product_id,
                quantity=quantity,
                created_at=datetime.utcnow()
            )
            db.session.add(cart_item)
        
        db.session.commit()
        return jsonify({'message': 'Item added to cart'}), 201
    
    elif request.method == 'DELETE':
        data = request.get_json()
        cart_item_id = data.get('cart_item_id')
        
        cart_item = CartItem.query.filter_by(
            id=cart_item_id,
            user_id=current_user.id
        ).first()
        
        if not cart_item:
            return jsonify({'error': 'Cart item not found'}), 404
        
        db.session.delete(cart_item)
        db.session.commit()
        return jsonify({'message': 'Item removed from cart'}), 200
