from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_wtf.csrf import CSRFProtect
from config import config
import pypyodbc
#models 
from models.ModelUser import ModelUser
from models.ModelSupplier import ModelSupplier
from models.ModelProduct import ModelProduct
from models.ModelClient import ModelClient
#entities
from models.entities.Product import Product
from models.entities.Supplier import Supplier
from models.entities.User import User
from models.entities.Client import Client
from models.entities.LastOrders import LastOrders

app = Flask(__name__)

csrf = CSRFProtect(app)

db = pypyodbc.connect(config['development'].connection_string)
print(db)

app.config.from_object(config['development'])


login_manager_app = LoginManager(app)

@login_manager_app.user_loader
def load_user(id):
    return ModelUser.get_by_id(db, id)


@app.route('/')
def index():
    logged_user = current_user
    if logged_user.is_authenticated:
        return redirect(url_for('search_data'))
    else:
        return redirect(url_for('login'))    


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = User(0, '', '', '', request.form['email'], request.form['password'], '')
        logged_user = ModelUser.login(db, user)

        if logged_user is not None:
            if logged_user.password:
                login_user(logged_user)
                return redirect(url_for('dashboard'))
            else:
                flash('Contraseña invalida...')
                return render_template('auth/login.html')
        else:
            flash('Usuario o contraseña Incorrecta')
            return render_template('auth/login.html')
    else:
        return render_template('auth/login.html')

#@app.route('/inicio')
#@login_required
#def dashboard():
#    return render_template('home.html')

@app.route('/inicio', methods=['GET', 'POST'])
@login_required
def search_data():
    user_id = current_user.id
    if request.method == "GET":       
        query = "EXEC dbo.SEL_TOTAL_ORDERS @AccountId = ?"
        cursor = db.cursor()
        cursor.execute(query, (user_id,))
        dato1 = cursor.fetchone()
        cursor.close()
        print(dato1)
    
        query2 = "EXEC dbo.SEL_TOTAL_AMOUNT_MONEY_ORDERS @AccountId = ?"
        cursor2 = db.cursor()
        cursor2.execute(query2, (user_id,))
        dato2 = cursor2.fetchone()
        cursor2.close()
        print(dato2)
    
        query3 = "EXEC dbo.SEL_TOTAL_AMOUNT_KGS_ORDERS @AccountId = ?"
        cursor3 = db.cursor()
        cursor3.execute(query3, (user_id,))
        dato3 = cursor3.fetchone()
        cursor3.close()
        print(dato3)
    
        query4 = "EXEC dbo.SEL_RECENT_PURCHASE_ORDERS @AccountId = ?"
        cursor4 = db.cursor()
        cursor4.execute(query4, (user_id,))
        rows = cursor4.fetchall()
        lastorders = []
        for row in rows:
            lastorder = LastOrders(row[0], row[1], row[2], row [3])
            lastorders.append(lastorder)
        print(lastorders)
        cursor4.close()
        return render_template('home.html', dato1=dato1, dato2=dato2, dato3=dato3, lastorders=lastorders)

@app.route('/proveedores', methods=['GET', 'POST']) 
@login_required
def proveedores():
   #request method GET y POST
    if request.method == 'GET':
        suppliers = ModelSupplier.get_all(db)
        return render_template('supplier.html', suppliers=suppliers)
    if request.method == 'POST':
        supplier = Supplier(0, request.form['ruc'], request.form['name'], request.form['lastname'], request.form['email'], request.form['cellphone'])
        if ModelSupplier.post(db, supplier):
            flash('Proveedor agregado correctamente','success')
            return redirect(url_for('proveedores'))
        else:
            flash('Error al agregar proveedor','danger')
            return redirect(url_for('proveedores'))
        
@app.route('/clientes', methods=['GET', 'POST']) 
@login_required
def clientes():
   #request method GET y POST
    if request.method == 'GET':
        clients = ModelClient.get_all(db)
        return render_template('client.html', clients=clients)
    if request.method == 'POST':
        client = Client(0, request.form['ruc'], request.form['name'], request.form['lastname'], request.form['address'], request.form['email'], request.form['cellphone'])
        if ModelClient.post(db, client):
            flash('Cliente agregado correctamente','success')
            return redirect(url_for('clientes'))
        else:
            flash('Error al agregar cliente','danger')
            return redirect(url_for('clientes'))
        
#metodos crud productos
@app.route('/productos')
@login_required
def productos():
    if request.method == 'GET':
        products = ModelProduct.get_all(db)
        return render_template('products.html', products=products)
    if request.method == 'POST':
        product = Product(0, request.form['name'], request.form['description'], request.form['image'])
        if ModelProduct.post(db, product):
            flash('Producto agregado correctamente','success')
            return redirect(url_for('productos'))
        else:
            flash('Error al agregar producto','danger')
            return redirect(url_for('productos'))






#METODOS CRUD ORDENES DE COMPRA
@app.route('/ordenes_compra')
@login_required
def ver_ord_comp():
    return render_template('BuyOrders.html')

@app.route('/realizar_compra')
@login_required
def realizar_compra():
    return render_template('doBuy.html')


#//////////////////////////////////////

@app.route('/inventario')
@login_required
def inventario():
    return render_template('inventory.html')

@app.route('/estadisticas')
@login_required
def analytics():
    return render_template('analytics.html')


#METODOS CRUD ORDENES DE VENTA
@app.route('/ordenes_venta')
@login_required
def ver_ord_ven():
    return render_template('SellOrders.html')

@app.route('/realizar_venta')
@login_required
def realizar_venta():
    return render_template('doSell.html')

#//////////////////////////////////////
#ruta para ver api de usuario
@app.route('/api/almacen')
def api_usuario():
    return 0

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))

def status_401(error):
    return "<h1> ERROR 401 </h1> ", 401

def status_404(error):
    return "<h1> ERROR 404 </h1> ", 404

if __name__ == '__main__':
    app.config.from_object(config['development'])
    #csrf.init_app(app)
    app.register_error_handler(401, status_401)
    app.register_error_handler(404, status_404)
    app.run(debug=True, port=4000,host="0.0.0.0")

