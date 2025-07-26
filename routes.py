from flask import Blueprint, render_template, redirect, url_for, flash, request, abort, jsonify
from flask_login import login_user, logout_user, current_user, login_required
from models import db, User, Product, CartItem
from forms import LoginForm, RegistrationForm, ProductForm
from werkzeug.security import generate_password_hash
from datetime import datetime
import os
from functools import wraps

main = Blueprint('main', __name__)

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_admin:
            abort(403)
        return f(*args, **kwargs)
    return decorated_function

@main.route('/')
def home():
    if current_user.is_authenticated:
        page = request.args.get('page', 1, type=int)
        per_page = 6
        products = Product.query.paginate(page=page, per_page=per_page)
        return render_template('home.html', products=products)
    else:
        return redirect(url_for('main.login'))

@main.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            next_page = request.args.get('next')
            return redirect(next_page or url_for('main.home'))
        flash('Invalid email or password', 'danger')
    return render_template('login.html', form=form)

@main.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(
            email=form.email.data,
            password=generate_password_hash(form.password.data),
            name=form.name.data,
            created_at=datetime.utcnow()
        )
        db.session.add(user)
        db.session.commit()
        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('main.login'))
    return render_template('register.html', form=form)

@main.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.login'))

@main.route('/products')
@login_required
def product_list():
    search = request.args.get('search', '')
    category = request.args.get('category', '')
    page = request.args.get('page', 1, type=int)
    per_page = 6
    
    query = Product.query
    if search:
        query = query.filter(Product.name.ilike(f'%{search}%'))
    if category:
        query = query.filter_by(category=category)
    
    products = query.paginate(page=page, per_page=per_page)
    return render_template('products/list.html', 
                         products=products, 
                         search=search, 
                         category=category)

@main.route('/products/<int:product_id>')
@login_required
def product_detail(product_id):
    product = Product.query.get_or_404(product_id)
    return render_template('products/detail.html', product=product)

@main.route('/admin/products')
@login_required
@admin_required
def admin_products():
    page = request.args.get('page', 1, type=int)
    per_page = 10  # Different pagination for admin view
    
    products = Product.query.paginate(page=page, per_page=per_page)
    return render_template('products/list.html', 
                         products=products,
                         admin=True)

@main.route('/admin/products/add', methods=['GET', 'POST'])
@login_required
@admin_required
def add_product():
    form = ProductForm()
    if form.validate_on_submit():
        product = Product(
            name=form.name.data,
            description=form.description.data,
            price=form.price.data,
            image_url=form.image_url.data,
            stock=form.stock.data,
            category=form.category.data,
            created_at=datetime.utcnow()
        )
        db.session.add(product)
        db.session.commit()
        flash('Product added successfully!', 'success')
        return redirect(url_for('main.admin_products'))
    return render_template('products/add.html', form=form)

@main.route('/admin/products/<int:product_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_product(product_id):
    product = Product.query.get_or_404(product_id)
    form = ProductForm(obj=product)
    if form.validate_on_submit():
        product.name = form.name.data
        product.description = form.description.data
        product.price = form.price.data
        product.image_url = form.image_url.data
        product.stock = form.stock.data
        product.category = form.category.data
        db.session.commit()
        flash('Product updated successfully!', 'success')
        return redirect(url_for('main.admin_products'))
    return render_template('products/edit.html', form=form, product=product)

@main.route('/admin/products/<int:product_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_product(product_id):
    product = Product.query.get_or_404(product_id)
    db.session.delete(product)
    db.session.commit()
    flash('Product deleted successfully!', 'success')
    return redirect(url_for('main.admin_products'))

@main.route('/cart')
@login_required
def view_cart():
    cart_items = CartItem.query.filter_by(user_id=current_user.id).all()
    total = sum(item.product.price * item.quantity for item in cart_items)
    return render_template('products/cart.html', 
                         cart_items=cart_items, 
                         total=total)

@main.route('/checkout')
@login_required
def checkout():
    cart_items = CartItem.query.filter_by(user_id=current_user.id).all()
    if not cart_items:
        flash('Your cart is empty', 'warning')
        return redirect(url_for('main.view_cart'))
    
    total = sum(item.product.price * item.quantity for item in cart_items)
    return render_template('products/checkout.html', total=total)

@main.route('/checkout/complete', methods=['POST'])
@login_required
def checkout_complete():
    cart_items = CartItem.query.filter_by(user_id=current_user.id).all()
    if not cart_items:
        return redirect(url_for('main.view_cart'))
    
    # In a real application, you would process payment here
    # For this demo, we'll just clear the cart
    for item in cart_items:
        db.session.delete(item)
    db.session.commit()
    
    flash('Order placed successfully! Thank you for your purchase.', 'success')
    return redirect(url_for('main.home'))

@main.route('/admin')
@login_required
@admin_required
def admin_dashboard():
    products_count = Product.query.count()
    users_count = User.query.count()
    orders_count = CartItem.query.count()
    
    return render_template('admin/dashboard.html',
                         products_count=products_count,
                         users_count=users_count,
                         orders_count=orders_count)