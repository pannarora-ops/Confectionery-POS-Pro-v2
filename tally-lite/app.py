from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tally.db'
app.config['SECRET_KEY'] = 'secret-key-for-session'
app.config['UPLOAD_FOLDER'] = 'static/products'
db = SQLAlchemy(app)

# Ensure upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# ==================== MODELS ====================

class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    hsn_code = db.Column(db.String(20))
    rate = db.Column(db.Float, default=0.0)
    gst_rate = db.Column(db.Float, default=0.0)  # GST percentage
    stock = db.Column(db.Integer, default=0)
    description = db.Column(db.Text)
    image = db.Column(db.String(200))  # Product image for online store
    is_featured = db.Column(db.Boolean, default=False)  # Show in online store
    category = db.Column(db.String(50))  # Product category
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Item {self.name}>'


class Party(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    type = db.Column(db.String(20))  # Customer, Supplier, Both
    phone = db.Column(db.String(20))
    email = db.Column(db.String(100))
    address = db.Column(db.Text)
    balance = db.Column(db.Float, default=0.0)  # Positive = Receivable, Negative = Payable
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Party {self.name}>'


class Invoice(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    invoice_number = db.Column(db.String(50), unique=True, nullable=False)
    party_id = db.Column(db.Integer, db.ForeignKey('party.id'), nullable=False)
    date = db.Column(db.Date, default=datetime.utcnow)
    total_amount = db.Column(db.Float, default=0.0)
    tax_amount = db.Column(db.Float, default=0.0)
    grand_total = db.Column(db.Float, default=0.0)
    type = db.Column(db.String(20))  # Sales, Purchase
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    party = db.relationship('Party', backref='invoices')
    items = db.relationship('InvoiceItem', backref='invoice', cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Invoice {self.invoice_number}>'


class InvoiceItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    invoice_id = db.Column(db.Integer, db.ForeignKey('invoice.id'), nullable=False)
    item_id = db.Column(db.Integer, db.ForeignKey('item.id'), nullable=False)
    quantity = db.Column(db.Integer, default=1)
    rate = db.Column(db.Float, default=0.0)
    amount = db.Column(db.Float, default=0.0)
    tax_rate = db.Column(db.Float, default=0.0)
    tax_amount = db.Column(db.Float, default=0.0)
    total = db.Column(db.Float, default=0.0)

    item = db.relationship('Item')

    def __repr__(self):
        return f'<InvoiceItem {self.item_id}>'


class JournalEntry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, default=datetime.utcnow)
    voucher_number = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    entries = db.relationship('JournalLine', backref='journal', cascade='all, delete-orphan')

    def __repr__(self):
        return f'<JournalEntry {self.voucher_number}>'


class JournalLine(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    journal_id = db.Column(db.Integer, db.ForeignKey('journal_entry.id'), nullable=False)
    account_name = db.Column(db.String(100), nullable=False)
    debit = db.Column(db.Float, default=0.0)
    credit = db.Column(db.Float, default=0.0)

    def __repr__(self):
        return f'<JournalLine {self.account_name}>'


class OnlineOrder(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_number = db.Column(db.String(50), unique=True, nullable=False)
    customer_name = db.Column(db.String(100), nullable=False)
    customer_email = db.Column(db.String(100), nullable=False)
    customer_phone = db.Column(db.String(20))
    shipping_address = db.Column(db.Text, nullable=False)
    city = db.Column(db.String(50))
    state = db.Column(db.String(50))
    pincode = db.Column(db.String(10))
    order_date = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default='Pending')  # Pending, Confirmed, Shipped, Delivered, Cancelled
    payment_method = db.Column(db.String(20))  # COD, Online, UPI
    payment_status = db.Column(db.String(20), default='Unpaid')  # Paid, Unpaid
    total_amount = db.Column(db.Float, default=0.0)
    tax_amount = db.Column(db.Float, default=0.0)
    grand_total = db.Column(db.Float, default=0.0)
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    items = db.relationship('OnlineOrderItem', backref='order', cascade='all, delete-orphan')

    def __repr__(self):
        return f'<OnlineOrder {self.order_number}>'


class OnlineOrderItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('online_order.id'), nullable=False)
    item_id = db.Column(db.Integer, db.ForeignKey('item.id'), nullable=False)
    quantity = db.Column(db.Integer, default=1)
    rate = db.Column(db.Float, default=0.0)
    amount = db.Column(db.Float, default=0.0)
    tax_rate = db.Column(db.Float, default=0.0)
    tax_amount = db.Column(db.Float, default=0.0)
    total = db.Column(db.Float, default=0.0)

    item = db.relationship('Item')

    def __repr__(self):
        return f'<OnlineOrderItem {self.item_id}>'


# ==================== ROUTES ====================

@app.route('/')
def index():
    items_count = Item.query.count()
    parties_count = Party.query.count()
    invoices_count = Invoice.query.count()
    sales = Invoice.query.filter_by(type='Sales').all()
    total_sales = sum(i.grand_total for i in sales)
    return render_template('index.html', 
                         items_count=items_count, 
                         parties_count=parties_count, 
                         invoices_count=invoices_count,
                         total_sales=total_sales)


@app.route('/items')
def items():
    all_items = Item.query.all()
    return render_template('items.html', items=all_items)


@app.route('/item/add', methods=['GET', 'POST'])
def add_item():
    if request.method == 'POST':
        name = request.form.get('name')
        hsn_code = request.form.get('hsn_code')
        rate = float(request.form.get('rate', 0))
        gst_rate = float(request.form.get('gst_rate', 0))
        stock = int(request.form.get('stock', 0))
        description = request.form.get('description', '')
        category = request.form.get('category', '')
        is_featured = True if request.form.get('is_featured') else False
        
        # Handle image upload
        image_filename = ''
        if 'image' in request.files:
            file = request.files['image']
            if file and file.filename != '':
                import uuid
                ext = file.filename.rsplit('.', 1)[1].lower() if '.' in file.filename else ''
                image_filename = f"{uuid.uuid4().hex}.{ext}" if ext else ''
                if image_filename:
                    file.save(os.path.join(app.config['UPLOAD_FOLDER'], image_filename))

        item = Item(
            name=name, 
            hsn_code=hsn_code, 
            rate=rate, 
            gst_rate=gst_rate, 
            stock=stock,
            description=description,
            category=category,
            is_featured=is_featured,
            image=image_filename
        )
        db.session.add(item)
        db.session.commit()
        flash('Item added successfully!', 'success')
        return redirect(url_for('items'))
    return render_template('add_item.html')


@app.route('/parties')
def parties():
    all_parties = Party.query.all()
    return render_template('parties.html', parties=all_parties)


@app.route('/party/add', methods=['GET', 'POST'])
def add_party():
    if request.method == 'POST':
        name = request.form.get('name')
        ptype = request.form.get('type')
        phone = request.form.get('phone')
        email = request.form.get('email')
        address = request.form.get('address')

        party = Party(name=name, type=ptype, phone=phone, email=email, address=address)
        db.session.add(party)
        db.session.commit()
        flash('Party added successfully!', 'success')
        return redirect(url_for('parties'))
    return render_template('add_party.html')


@app.route('/invoices')
def invoices():
    all_invoices = Invoice.query.order_by(Invoice.date.desc()).all()
    return render_template('invoices.html', invoices=all_invoices)


@app.route('/invoice/create', methods=['GET', 'POST'])
def create_invoice():
    if request.method == 'POST':
        invoice_number = request.form.get('invoice_number')
        party_id = int(request.form.get('party_id'))
        invoice_type = request.form.get('type')
        invoice_date = datetime.strptime(request.form.get('date'), '%Y-%m-%d').date()

        invoice = Invoice(
            invoice_number=invoice_number,
            party_id=party_id,
            date=invoice_date,
            type=invoice_type
        )
        db.session.add(invoice)
        db.session.flush()

        item_ids = request.form.getlist('item_id[]')
        quantities = request.form.getlist('quantity[]')
        rates = request.form.getlist('rate[]')
        tax_rates = request.form.getlist('tax_rate[]')

        total_amount = 0
        tax_amount = 0

        for i in range(len(item_ids)):
            item_id = int(item_ids[i])
            qty = int(quantities[i])
            rate = float(rates[i])
            tax_rate = float(tax_rates[i])

            amount = qty * rate
            tax_amt = amount * (tax_rate / 100)
            total = amount + tax_amt

            invoice_item = InvoiceItem(
                invoice_id=invoice.id,
                item_id=item_id,
                quantity=qty,
                rate=rate,
                amount=amount,
                tax_rate=tax_rate,
                tax_amount=tax_amt,
                total=total
            )
            db.session.add(invoice_item)

            total_amount += amount
            tax_amount += tax_amt

            # Update stock
            if invoice_type == 'Sales':
                item = Item.query.get(item_id)
                item.stock -= qty
            elif invoice_type == 'Purchase':
                item = Item.query.get(item_id)
                item.stock += qty

        invoice.total_amount = total_amount
        invoice.tax_amount = tax_amount
        invoice.grand_total = total_amount + tax_amount

        # Update party balance
        party = Party.query.get(party_id)
        if invoice_type == 'Sales':
            party.balance += invoice.grand_total
        else:
            party.balance -= invoice.grand_total

        db.session.commit()
        flash('Invoice created successfully!', 'success')
        return redirect(url_for('invoices'))

    items = Item.query.all()
    parties = Party.query.all()
    return render_template('create_invoice.html', items=items, parties=parties, today=datetime.now().strftime('%Y-%m-%d'))


@app.route('/accounting')
def accounting():
    journals = JournalEntry.query.order_by(JournalEntry.date.desc()).all()
    return render_template('accounting.html', journals=journals)


@app.route('/journal/add', methods=['GET', 'POST'])
def add_journal():
    if request.method == 'POST':
        voucher_number = request.form.get('voucher_number')
        date_str = request.form.get('date')
        description = request.form.get('description')
        journal_date = datetime.strptime(date_str, '%Y-%m-%d').date()

        journal = JournalEntry(voucher_number=voucher_number, date=journal_date, description=description)
        db.session.add(journal)
        db.session.flush()

        account_names = request.form.getlist('account_name[]')
        debits = request.form.getlist('debit[]')
        credits = request.form.getlist('credit[]')

        for i in range(len(account_names)):
            line = JournalLine(
                journal_id=journal.id,
                account_name=account_names[i],
                debit=float(debits[i] or 0),
                credit=float(credits[i] or 0)
            )
            db.session.add(line)

        db.session.commit()
        flash('Journal entry added successfully!', 'success')
        return redirect(url_for('accounting'))

    return render_template('add_journal.html', today=datetime.now().strftime('%Y-%m-%d'))


@app.route('/reports')
def reports():
    # Stock Summary
    items = Item.query.all()
    # Party Balance
    parties = Party.query.all()
    # Sales/Purchase Summary
    sales = Invoice.query.filter_by(type='Sales').all()
    purchases = Invoice.query.filter_by(type='Purchase').all()

    total_sales = sum(i.grand_total for i in sales)
    total_purchases = sum(i.grand_total for i in purchases)

    return render_template('reports.html', 
                         items=items, 
                         parties=parties, 
                         total_sales=total_sales, 
                         total_purchases=total_purchases)


# ==================== ONLINE STORE ROUTES ====================

@app.route('/store')
def online_store():
    """Public online store homepage"""
    featured_items = Item.query.filter_by(is_featured=True).filter(Item.stock > 0).all()
    all_products = Item.query.filter(Item.stock > 0).all()
    categories = db.session.query(Item.category).filter(Item.category != '').distinct().all()
    return render_template('store.html', 
                         featured_items=featured_items, 
                         all_products=all_products,
                         categories=categories)


@app.route('/store/product/<int:item_id>')
def product_detail(item_id):
    """Product detail page"""
    item = Item.query.get_or_404(item_id)
    related_items = Item.query.filter(Item.category == item.category, Item.id != item.id, Item.stock > 0).limit(4).all()
    return render_template('product_detail.html', item=item, related_items=related_items)


@app.route('/store/cart')
def cart():
    """Shopping cart page"""
    if 'cart' not in session:
        session['cart'] = {}
    
    cart_items = []
    total = 0
    
    for item_id, qty in session['cart'].items():
        item = Item.query.get(int(item_id))
        if item and item.stock > 0:
            item_total = item.rate * qty
            tax = item_total * (item.gst_rate / 100)
            cart_items.append({
                'item': item,
                'quantity': qty,
                'amount': item_total,
                'tax': tax,
                'total': item_total + tax
            })
            total += item_total + tax
    
    return render_template('cart.html', cart_items=cart_items, grand_total=total)


@app.route('/store/add_to_cart/<int:item_id>', methods=['POST'])
def add_to_cart(item_id):
    """Add item to cart"""
    if 'cart' not in session:
        session['cart'] = {}
    
    quantity = int(request.form.get('quantity', 1))
    item = Item.query.get(item_id)
    
    if item and item.stock >= quantity:
        item_id_str = str(item_id)
        if item_id_str in session['cart']:
            session['cart'][item_id_str] += quantity
        else:
            session['cart'][item_id_str] = quantity
        session.modified = True
        flash('Item added to cart!', 'success')
    else:
        flash('Item out of stock or invalid quantity!', 'danger')
    
    return redirect(url_for('online_store'))


@app.route('/store/update_cart/<int:item_id>', methods=['POST'])
def update_cart(item_id):
    """Update cart item quantity"""
    if 'cart' not in session:
        session['cart'] = {}
    
    quantity = int(request.form.get('quantity', 0))
    item_id_str = str(item_id)
    
    if quantity <= 0:
        session['cart'].pop(item_id_str, None)
    else:
        session['cart'][item_id_str] = quantity
    
    session.modified = True
    return redirect(url_for('cart'))


@app.route('/store/remove_from_cart/<int:item_id>')
def remove_from_cart(item_id):
    """Remove item from cart"""
    if 'cart' not in session:
        session['cart'] = {}
    
    item_id_str = str(item_id)
    session['cart'].pop(item_id_str, None)
    session.modified = True
    flash('Item removed from cart!', 'success')
    
    return redirect(url_for('cart'))


@app.route('/store/checkout', methods=['GET', 'POST'])
def checkout():
    """Checkout page"""
    if 'cart' not in session or not session['cart']:
        flash('Your cart is empty!', 'warning')
        return redirect(url_for('online_store'))
    
    if request.method == 'POST':
        # Create order
        import uuid
        order_number = f"ORD-{uuid.uuid4().hex[:8].upper()}"
        
        customer_name = request.form.get('customer_name')
        customer_email = request.form.get('customer_email')
        customer_phone = request.form.get('customer_phone')
        shipping_address = request.form.get('shipping_address')
        city = request.form.get('city')
        state = request.form.get('state')
        pincode = request.form.get('pincode')
        payment_method = request.form.get('payment_method')
        notes = request.form.get('notes', '')
        
        # Calculate totals
        total_amount = 0
        tax_amount = 0
        
        order = OnlineOrder(
            order_number=order_number,
            customer_name=customer_name,
            customer_email=customer_email,
            customer_phone=customer_phone,
            shipping_address=shipping_address,
            city=city,
            state=state,
            pincode=pincode,
            payment_method=payment_method,
            notes=notes
        )
        db.session.add(order)
        db.session.flush()
        
        for item_id, qty in session['cart'].items():
            item = Item.query.get(int(item_id))
            if item:
                amount = item.rate * qty
                tax = amount * (item.gst_rate / 100)
                total = amount + tax
                
                order_item = OnlineOrderItem(
                    order_id=order.id,
                    item_id=item.id,
                    quantity=qty,
                    rate=item.rate,
                    amount=amount,
                    tax_rate=item.gst_rate,
                    tax_amount=tax,
                    total=total
                )
                db.session.add(order_item)
                
                total_amount += amount
                tax_amount += tax
                
                # Reduce stock
                item.stock -= qty
        
        order.total_amount = total_amount
        order.tax_amount = tax_amount
        order.grand_total = total_amount + tax_amount
        
        if payment_method == 'COD':
            order.payment_status = 'Unpaid'
        else:
            order.payment_status = 'Paid'  # Assuming online payment is successful
        
        order.status = 'Confirmed'
        
        db.session.commit()
        session.pop('cart', None)
        
        flash(f'Order placed successfully! Order Number: {order_number}', 'success')
        return redirect(url_for('order_confirmation', order_number=order_number))
    
    # Calculate cart totals
    cart_items = []
    total = 0
    
    for item_id, qty in session.get('cart', {}).items():
        item = Item.query.get(int(item_id))
        if item:
            item_total = item.rate * qty
            tax = item_total * (item.gst_rate / 100)
            cart_items.append({
                'item': item,
                'quantity': qty,
                'total': item_total + tax
            })
            total += item_total + tax
    
    return render_template('checkout.html', cart_items=cart_items, grand_total=total)


@app.route('/store/order-confirmation/<order_number>')
def order_confirmation(order_number):
    """Order confirmation page"""
    order = OnlineOrder.query.filter_by(order_number=order_number).first_or_404()
    return render_template('order_confirmation.html', order=order)


@app.route('/admin/orders')
def admin_orders():
    """Admin - View all online orders"""
    orders = OnlineOrder.query.order_by(OnlineOrder.order_date.desc()).all()
    return render_template('admin_orders.html', orders=orders)


@app.route('/admin/order/<int:order_id>/update_status', methods=['POST'])
def update_order_status(order_id):
    """Admin - Update order status"""
    order = OnlineOrder.query.get_or_404(order_id)
    new_status = request.form.get('status')
    payment_status = request.form.get('payment_status')
    
    if new_status:
        order.status = new_status
    if payment_status:
        order.payment_status = payment_status
    
    db.session.commit()
    flash('Order updated successfully!', 'success')
    return redirect(url_for('admin_orders'))


@app.route('/api/cart_count')
def cart_count():
    """API - Get cart item count"""
    if 'cart' not in session:
        return jsonify({'count': 0})
    
    count = sum(session['cart'].values())
    return jsonify({'count': count})


# ==================== END ONLINE STORE ROUTES ====================


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, host='0.0.0.0', port=5000)
