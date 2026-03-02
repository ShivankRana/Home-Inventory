import os
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import click

app = Flask(__name__)
app.config['SECRET_KEY'] = 'home-inventory-secret-key'
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'postgresql://user:pass@db:5432/inventory')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

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

@app.before_request
def create_tables():
    db.create_all()
    # Seed Locations
    if not Location.query.first():
        for loc_name in ['master_room', 'drawing_room', 'bathroom1', 'store_room']:
            db.session.add(Location(name=loc_name))
        db.session.commit()
    
    # Seed New Locations (Guest, Master, Small rooms with balcony/cupboard/bathroom)
    rooms = ['Guest_room', 'master_room', 'Small_room']
    subs = ['balcony', 'cupboard', 'bathroom']
    for room in rooms:
        if not Location.query.filter_by(name=room).first():
            db.session.add(Location(name=room))
        for sub in subs:
            name = f'{room}_{sub}'
            if not Location.query.filter_by(name=name).first():
                db.session.add(Location(name=name))
    db.session.commit()

    # Seed Categories
    if not Category.query.filter_by(name='Storage').first():
        for cat_name in ['Kitchen', 'Electronics', 'Tools', 'Storage', 'Other']:
            if not Category.query.filter_by(name=cat_name).first():
                db.session.add(Category(name=cat_name))
        db.session.commit()

@app.cli.command('add-item')
@click.argument('name')
@click.option('--sn', help='Serial Number')
@click.option('--qty', default=1, type=int, help='Quantity')
@click.option('--cat', required=True, help='Category Name')
@click.option('--loc', required=True, help='Location Name')
@click.option('--box', help='Storage Box Name')
@click.option('--desc', help='Description')
@click.option('--geo', default='Bangalore', help='Geo Location')
def add_item_cli(name, sn, qty, cat, loc, box, desc, geo):
    """Add an item via CLI."""
    category = Category.query.filter_by(name=cat).first()
    location = Location.query.filter_by(name=loc).first()
    if not category:
        click.echo(f'Error: Category "{cat}" not found.')
        return
    if not location:
        click.echo(f'Error: Location "{loc}" not found.')
        return
    storage_box_id = None
    if box:
        storage_box = StorageBox.query.filter_by(name=box).first()
        if not storage_box:
            click.echo(f'Error: Storage Box "{box}" not found.')
            return
        storage_box_id = storage_box.id
    new_item = Item(
        name=name, sn=sn, quantity=qty, 
        category_id=category.id, location_id=location.id,
        storage_box_id=storage_box_id, description=desc, geo_location=geo
    )
    db.session.add(new_item)
    db.session.commit()
    click.echo(f'Successfully added "{name}" to inventory!')

@app.route('/')
def dashboard():
    items = Item.query.all()
    categories = Category.query.all()
    locations = Location.query.all()
    boxes = StorageBox.query.all()
    return render_template('dashboard.html', items=items, categories=categories, locations=locations, boxes=boxes)

@app.route('/add', methods=['POST'])
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

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)
