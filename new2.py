from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
import datetime

app = Flask(__name__)

# Configure the SQLAlchemy part of the app
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///orders.db'  # SQLite database
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize the database
db = SQLAlchemy(app)

# Define the Order model
class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    customer = db.Column(db.String(100), nullable=False)
    date = db.Column(db.String(50), nullable=False)
    items = db.relationship('Item', backref='order', lazy=True)

    def calculate_total(self):
        total = sum([item.price * item.qty for item in self.items])
        discount = 0.1 * total
        net_total = total - discount
        tax = 0.09 * net_total
        grand_total = net_total + 2 * tax
        return total, discount, net_total, tax, grand_total

# Define the Item model
class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    item = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)
    qty = db.Column(db.Integer, nullable=False)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'), nullable=False)

# Create the database tables (run this once)
with app.app_context():
    db.create_all()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate_invoice', methods=['POST'])
def generate_invoice():
    customer = request.form['customer']
    date = datetime.date.today().strftime("%B %d, %Y")
    order = Order(customer=customer, date=date)
    
    num_items = int(request.form['numOfItems'])

    for i in range(num_items):
        item_name = request.form[f'item{i+1}']
        qty = int(request.form[f'qty{i+1}'])
        price = float(request.form[f'price{i+1}'])
        item = Item(item=item_name, price=price, qty=qty, order=order)
        db.session.add(item)

    db.session.add(order)
    db.session.commit()

    total, discount, net_total, tax, grand_total = order.calculate_total()

    return render_template('invoice.html', order=order, total=total, discount=discount,
                           net_total=net_total, tax=tax, grand_total=grand_total)

if __name__ == '__main__':
    app.run(debug=True)