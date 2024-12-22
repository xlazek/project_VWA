from flask import Flask
from flask_sqlalchemy import SQLAlchemy

# Inicializace aplikace Flask a konfigurace databáze
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///food_delivery.db'  # SQLite databáze
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Definice modelu pro uživatele
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(50), nullable=False)  # customer, courier, restaurant

# Definice modelu pro restaurace
class Restaurant(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    image = db.Column(db.String(200))  # Cesta k obrázku
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)  # Vlastník restaurace

# Definice modelu pro jídla
class Meal(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    price = db.Column(db.Float, nullable=False)
    image = db.Column(db.String(200))  # Cesta k obrázku
    restaurant_id = db.Column(db.Integer, db.ForeignKey('restaurant.id'), nullable=False)

# Definice modelu pro objednávky
class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    address = db.Column(db.String(200), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    status = db.Column(db.String(50), default='pending')  # pending, completed, cancelled
    items = db.Column(db.Text, nullable=False)  # JSON string obsahující objednané položky

# Inicializace databáze při prvním spuštění
@app.before_first_request
def create_tables():
    db.create_all()

if __name__ == "__main__":
    app.run(debug=True)
