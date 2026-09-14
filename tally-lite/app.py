from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tally.db'
app.config['SECRET_KEY'] = 'secret-key-for-session'
db = SQLAlchemy(app)

# ==================== MODELS ====================

class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    hsn_code = db.Column(db.String(20))
    rate = db.Column(db.Float, default=0.0)
    gst_rate = db.Column(db.Float, default=0.0)  # GST percentage
    stock = db.Column(db.Integer, default=0)
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

        item = Item(name=name, hsn_code=hsn_code, rate=rate, gst_rate=gst_rate, stock=stock)
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


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, host='0.0.0.0', port=5000)
