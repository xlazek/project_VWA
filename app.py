import os
from flask import Flask, render_template, request, redirect, url_for, session

app = Flask(__name__)
app.secret_key = "tajne_heslo"  # Klíč pro práci se session
app.config["UPLOAD_FOLDER"] = "static/uploads"
# Globální seznam uživatelů
users = [
    {
    "username": "admin",
    "email": "admin@seznam.cz",
    "password": "admin",
    "role": "admin"
},
{
        "username": "poslicek1",
        "email": "poslicek1@example.com",
        "password": "heslo123",
        "role": "courier",
        "id": 1  # Unikátní ID poslíčka
    },
    {
        "username": "poslicek2",
        "email": "poslicek2@example.com",
        "password": "heslo123",
        "role": "courier",
        "id": 2
    },
    {
        "username": "poslicek3",
        "email": "poslicek3@example.com",
        "password": "heslo123",
        "role": "courier",
        "id": 3
    }
]

# Globální seznam restaurací
restaurants = [
    {
        "name": "Pizzerie Bella",
        "description": "Tradiční italská pizza přímo k vám domů.",
        "image_url": "https://via.placeholder.com/300x200",
        "menu": [
            {"name": "Margherita", "price": 120, "image_url": "https://via.placeholder.com/150"},
            {"name": "Pepperoni", "price": 140, "image_url": "https://via.placeholder.com/150"},
            {"name": "Capricciosa", "price": 150, "image_url": "https://via.placeholder.com/150"}
        ]
    },
    {
        "name": "Sushi Sakura",
        "description": "Čerstvé sushi s nejvyšší kvalitou surovin.",
        "image_url": "https://via.placeholder.com/300x200",
        "menu": [
            {"name": "Sushi Set A", "price": 300, "image_url": "https://via.placeholder.com/150"},
            {"name": "Sushi Set B", "price": 400, "image_url": "https://via.placeholder.com/150"},
            {"name": "California Roll", "price": 200, "image_url": "https://via.placeholder.com/150"}
        ]
    }
]
orders = [
    {
        "id": 1,
        "customer": "Jan Novák",
        "food": "Pizza",
        "price": 250,
        "date": "2024-12-22",
        "status": "pending"
    },
    {
        "id": 2,
        "customer": "Eva Svobodová",
        "food": "Sushi",
        "price": 350,
        "date": "2024-12-21",
        "status": "in_progress"
    }
]



# Zajištění složky pro uploady
os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

@app.route("/")
def home():
    return render_template("index.jinja")

@app.route("/menu")
def menu():
    if not restaurants:  # Pokud není žádná restaurace
        message = "Je nám líto, žádná restaurace momentálně nerozváří :/"
        return render_template("menu.jinja", restaurants=[], message=message)

    return render_template("menu.jinja", restaurants=restaurants)

@app.route("/cart", methods=["GET", "POST"])
def cart():
    cart = session.get("cart", [])

    if request.method == "POST":
        if "update_quantity" in request.form:
            # Aktualizace množství
            item_name = request.form["item_name"]
            new_quantity = int(request.form["quantity"])
            for item in cart:
                if item["name"] == item_name:
                    item["quantity"] = new_quantity
            session["cart"] = cart

        if "remove_item" in request.form:
            # Odstranění položky
            item_to_remove = request.form["remove_item"]
            cart = [item for item in cart if item["name"] != item_to_remove]
            session["cart"] = cart

        if "address" in request.form and "phone" in request.form:
            # Simulace odeslání objednávky
            address = request.form["address"]
            phone = request.form["phone"]

            print("Objednávka vytvořena:")
            print("Adresa:", address)
            print("Telefon:", phone)
            print("Košík:", cart)

            # Vyprázdníme košík
            session["cart"] = []
            return "Děkujeme za objednávku!"

    return render_template("cart.jinja", cart=cart)

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        # Ověření uživatele
        user = next((user for user in users if user.get("email") == email), None)

        if user and user.get("password") == password:  # Kontrola hesla
            # Kontrola, zda má uživatel všechny potřebné klíče
            required_keys = {"username", "email", "password", "role"}
            if not required_keys.issubset(user.keys()):
                return "Chyba: Neúplná data uživatele.", 400

            # Uložení uživatele do session
            session["user"] = {
                "username": user["username"],
                "email": user["email"],
                "role": user["role"]
            }
            return redirect(url_for("home"))

        return render_template("login.jinja", error="Nesprávný e-mail nebo heslo.")

    return render_template("login.jinja")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        email = request.form["email"]
        password = request.form["password"]
        role = request.form["role"]

        user = {
            "username": username,
            "email": email,
            "password": password,
            "role": role
        }

        users.append(user)
        session["user"] = user  # Automaticky přihlásíme uživatele

        # Přesměrování na Add Restaurant, pokud role je restaurace
        if role == "restaurant":
            return redirect(url_for("add_restaurant"))

        return redirect(url_for("home"))

    return render_template("register.jinja")

@app.route("/add_restaurant", methods=["GET", "POST"])
def add_restaurant():
    # Kontrola, zda je uživatel přihlášen a má roli "restaurace"
    if "user" not in session or session["user"]["role"] != "restaurant":
        return redirect(url_for("login"))

    if request.method == "POST":
        name = request.form["name"]
        description = request.form["description"]

        restaurants.append({
            "name": name,
            "description": description
        })

        return redirect(url_for("menu"))

    return render_template("add_restaurant.jinja")
@app.route("/restaurants")
def view_restaurants():
    return render_template("restaurants.jinja", restaurants=restaurants)

@app.route("/logout")
def logout():
    session.pop("user", None)  # Odhlášení uživatele
    return redirect(url_for("home"))

@app.route("/manage_restaurant", methods=["GET", "POST"])
def manage_restaurant():
    # Kontrola, zda je uživatel přihlášen a má roli "restaurace"
    if "user" not in session or session["user"]["role"] != "restaurant":
        return redirect(url_for("login"))

    # Název restaurace
    user_restaurant_name = session["user"]["username"]

    # Filtrování jídel pro aktuální restauraci
    restaurant_items = [item for item in restaurants if item["name"] == user_restaurant_name]

    if request.method == "POST":
        # Přidání nového jídla
        if "add_item" in request.form:
            item_name = request.form["item_name"]
            item_description = request.form["item_description"]
            item_price = request.form["item_price"]
            item_image = request.files["item_image"]

            # Uložení obrázku
            if item_image:
                image_path = os.path.join(app.config["UPLOAD_FOLDER"], item_image.filename)
                item_image.save(image_path)
            else:
                image_path = None

            restaurants.append({
                "name": user_restaurant_name,
                "item_name": item_name,
                "item_description": item_description,
                "item_price": item_price,
                "item_image": image_path
            })

        # Mazání jídla
        if "delete_item" in request.form:
            item_to_delete = request.form["delete_item"]
            restaurants[:] = [item for item in restaurants if item["item_name"] != item_to_delete]

        return redirect(url_for("manage_restaurant"))

    return render_template("manage_restaurant.jinja", restaurant_items=restaurant_items)

@app.route("/restaurant/<restaurant_name>", methods=["GET", "POST"])
def view_menu(restaurant_name):
    # Najdeme restauraci podle názvu
    restaurant = next((r for r in restaurants if r["name"] == restaurant_name), None)
    if not restaurant:
        return "Restaurace nebyla nalezena.", 404

    if request.method == "POST":
        item_name = request.form["item_name"]
        item_price = int(request.form["item_price"])
        quantity = int(request.form["quantity"])

        # Získáme košík ze session
        cart = session.get("cart", [])
        # Zkontrolujeme, zda už položka existuje v košíku
        for item in cart:
            if item["name"] == item_name:
                item["quantity"] += quantity
                break
        else:
            # Přidání nové položky
            cart.append({"name": item_name, "price": item_price, "quantity": quantity})
        session["cart"] = cart
        return redirect(url_for("view_menu", restaurant_name=restaurant_name))

    return render_template("restaurant_menu.jinja", restaurant=restaurant)

@app.route("/update_cart/<item_id>", methods=["POST"])
def update_cart(item_id):
    # Získání košíku ze session
    cart = session.get("cart", [])
    for item in cart:
        if item["name"] == item_id:
            new_quantity = int(request.form.get("quantity", 1))
            if new_quantity <= 0:
                cart.remove(item)  # Pokud je množství 0 nebo méně, položku odstraníme
            else:
                item["quantity"] = new_quantity
            break
    session["cart"] = cart
    return redirect(url_for("cart"))

@app.route("/admin", methods=["GET", "POST"])
def admin_dashboard():
    if "user" not in session or session["user"].get("role") != "admin":
        return redirect(url_for("login"))

    # Seznam restaurací ke schválení
    pending_restaurants = [r for r in restaurants if not r.get("approved", False)]

    # Seznam poslíčků
    couriers = [u for u in users if u.get("role") == "courier"]

    if request.method == "POST":
        # Debug výstup
        print("Request Form Data:", request.form)

        # Schválení restaurace
        if "approve_restaurant" in request.form:
            restaurant_name = request.form["approve_restaurant"]
            for restaurant in restaurants:
                if restaurant["name"] == restaurant_name:
                    restaurant["approved"] = True
                    print(f"Restaurace {restaurant_name} byla schválena.")

        # Odmítnutí restaurace
        elif "reject_restaurant" in request.form:
            restaurant_name = request.form["reject_restaurant"]
            restaurants[:] = [r for r in restaurants if r["name"] != restaurant_name]
            print(f"Restaurace {restaurant_name} byla odmítnuta.")

        return redirect(url_for("admin_dashboard"))

    return render_template("admin_dashboard.jinja", pending_restaurants=pending_restaurants, couriers=couriers)

@app.route("/admin/couriers", methods=["GET", "POST"])
def manage_couriers():
    if "user" not in session or session["user"]["role"] != "admin":
        return redirect(url_for("login"))
    
    global users

    if request.method == "POST":
        # Debug výstup
        print("Request Form Data:", request.form)

        if "add_courier" in request.form:
            # Přidání nového poslíčka
            username = request.form["username"]
            email = request.form["email"]
            password = request.form["password"]
            new_courier = {
                "id": max([u.get("id", 0) for u in users] or [0]) + 1,
                "username": username,
                "email": email,
                "password": password,
                "role": "courier"
            }
            users.append(new_courier)
            print(f"Nový poslíček přidán: {new_courier}")

        elif "delete_courier" in request.form:
            if "courier_id" in request.form:
                courier_id = int(request.form["courier_id"])
                # Filtrujte jen záznamy, které mají klíč 'id'
                users = [user for user in users if user.get("id") != courier_id]
                print(f"Poslíček s ID {courier_id} byl smazán.")
            else:
                print("Chyba: ID poslíčka nebylo poskytnuto.")
                return "Chyba: ID poslíčka nebylo poskytnuto.", 400

    # Filtrování poslíčků
    couriers = [user for user in users if user.get("role") == "courier"]
    return render_template("admin_couriers.jinja", couriers=couriers)

@app.route("/admin/orders", methods=["GET", "POST"])
def manage_orders():
    if "user" not in session or session["user"].get("role") != "admin":
        return redirect(url_for("login"))
    
    global orders  # Pracujeme s globální proměnnou

    if request.method == "POST":
        if "status" in request.form:
            order_id = int(request.form["order_id"])
            new_status = request.form["status"]
            for order in orders:
                if order["id"] == order_id:
                    order["status"] = new_status

        elif "delete_order" in request.form:
            order_id = int(request.form["order_id"])
            orders = [order for order in orders if order["id"] != order_id]

    # Odesíláme objednávky do šablony
    return render_template("admin_orders.jinja", orders=orders)



if __name__ == "__main__":
    app.run(debug=True)
