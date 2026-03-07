import os
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from functools import wraps
import click

app = Flask(__name__)
app.config['SECRET_KEY'] = 'home-inventory-secret-key'
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'postgresql://user:pass@db:5432/inventory')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(20), default='user') # 'admin' or 'user'

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Location(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    items = db.relationship('Item', backref='location', lazy=True)
    boxes = db.relationship('StorageBox', backref='location', lazy=True)

class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    items = db.relationship('Item', backref='category', lazy=True)

class StorageBox(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    location_id = db.Column(db.Integer, db.ForeignKey('location.id'), nullable=False)
    items = db.relationship('Item', backref='storage_box', lazy=True)

class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    sn = db.Column(db.String(100))
    quantity = db.Column(db.Integer, default=1)
    description = db.Column(db.Text)
    geo_location = db.Column(db.String(100), default='Bangalore')
    added_at = db.Column(db.DateTime, default=datetime.utcnow)
    removed_at = db.Column(db.DateTime, nullable=True)
    
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=False)
    location_id = db.Column(db.Integer, db.ForeignKey('location.id'), nullable=False)
    storage_box_id = db.Column(db.Integer, db.ForeignKey('storage_box.id'), nullable=True)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'admin':
            flash('You do not have permission to perform this action.')
            return redirect(url_for('dashboard'))
        return f(*args, **kwargs)
    return decorated_function

@app.before_request
def create_tables():
    db.create_all()
    # Seed Admin and User
    if not User.query.filter_by(username='admin').first():
        admin = User(username='admin', role='admin')
        admin.set_password('admin123')
        db.session.add(admin)
    if not User.query.filter_by(username='user').first():
        user = User(username='user', role='user')
        user.set_password('user123')
        db.session.add(user)
    
    # Seed Locations
    if not Location.query.first():
        for loc_name in ['master_room', 'drawing_room', 'bathroom1', 'store_room']:
            db.session.add(Location(name=loc_name))
    db.session.commit()

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for('dashboard'))
        flash('Invalid username or password')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/')
@login_required
def dashboard():
    items = Item.query.all()
    categories = Category.query.all()
    locations = Location.query.all()
    boxes = StorageBox.query.all()
    return render_template('dashboard.html', items=items, categories=categories, locations=locations, boxes=boxes)

@app.route('/add', methods=['POST'])
@login_required
@admin_required
def add_item():
    name = request.form.get('name')
    sn = request.form.get('sn')
    quantity = request.form.get('quantity', 1)
    category_id = request.form.get('category_id')
    location_id = request.form.get('location_id')
    storage_box_id = request.form.get('storage_box_id')
    description = request.form.get('description')
    geo_location = request.form.get('geo_location', 'Bangalore')
    if name and category_id and location_id:
        if not storage_box_id or storage_box_id == '':
            storage_box_id = None
        new_item = Item(name=name, sn=sn, quantity=quantity, category_id=category_id, location_id=location_id, storage_box_id=storage_box_id, description=description, geo_location=geo_location)
        db.session.add(new_item)
        db.session.commit()
        flash('Item added successfully!')
    return redirect(url_for('dashboard'))

@app.route('/edit/<int:item_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_item(item_id):
    item = Item.query.get_or_404(item_id)
    if request.method == 'POST':
        item.name = request.form.get('name')
        item.sn = request.form.get('sn')
        item.quantity = request.form.get('quantity', 1)
        item.category_id = request.form.get('category_id')
        item.location_id = request.form.get('location_id')
        storage_box_id = request.form.get('storage_box_id')
        if not storage_box_id or storage_box_id == '':
            item.storage_box_id = None
        else:
            item.storage_box_id = storage_box_id
        item.description = request.form.get('description')
        item.geo_location = request.form.get('geo_location', 'Bangalore')
        db.session.commit()
        flash(f'Item "{item.name}" updated successfully!')
        return redirect(url_for('dashboard'))
    
    categories = Category.query.all()
    locations = Location.query.all()
    boxes = StorageBox.query.all()
    return render_template('edit_item.html', item=item, categories=categories, locations=locations, boxes=boxes)

@app.route('/delete/<int:item_id>', methods=['POST'])
@login_required
@admin_required
def delete_item(item_id):
    item = Item.query.get_or_404(item_id)
    name = item.name
    db.session.delete(item)
    db.session.commit()
    flash(f'Item "{name}" deleted successfully!')
    return redirect(url_for('dashboard'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)
