from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_wtf.csrf import CSRFProtect
from config import config
import pypyodbc
import datetime
#models 
from models.ModelUser import ModelUser
from models.ModelSupplier import ModelSupplier
from models.ModelProduct import ModelProduct
from models.ModelClient import ModelClient
from models.ModelPurchaseOrder import ModelPurchaseOrder
from models.ModelOrderXproduct import ModelOrderXproduct
#entities
from models.entities.Product import Product
from models.entities.Supplier import Supplier
from models.entities.User import User
from models.entities.Client import Client
from models.entities.PurchaseOrder import PurchaseOrder
from models.entities.LastOrders import LastOrders
from models.entities.ProductxCategory import ProductxCategory

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
                return redirect(url_for('search_data'))
            else:
                flash('Contraseña invalida...')
                return render_template('auth/login.html')
        else:
            flash('Usuario o contraseña Incorrecta')
            return render_template('auth/login.html')
    else:
        return render_template('auth/login.html')


@app.route('/inicio', methods=['GET', 'POST'])
@login_required
def search_data():
    user_id = current_user.id
    if request.method == "GET":
        def execute_query(query):
            cursor = db.cursor()
            cursor.execute(query, (user_id,))
            result = cursor.fetchone()
            cursor.close()
            return result[0] if result is not None else None

        dato1 = execute_query("EXEC dbo.SEL_TOTAL_ORDERS @AccountId = ?")
        dato2 = execute_query("EXEC dbo.SEL_TOTAL_AMOUNT_MONEY_ORDERS @AccountId = ?")
        dato3 = execute_query("EXEC dbo.SEL_TOTAL_AMOUNT_KGS_ORDERS @AccountId = ?")
    
        query4 = "EXEC dbo.SEL_RECENT_PURCHASE_ORDERS @AccountId = ?"
        cursor4 = db.cursor()
        cursor4.execute(query4, (user_id,))
        rows = cursor4.fetchall()
        lastorders = []
        for row in rows:
            lastorder = LastOrders(row[0], row[1], row[2], row [3])
            lastorders.append(lastorder)
        #print(lastorders)
        cursor4.close()
        
        query5 = "EXEC dbo.SEL_PRODUCTS_SELLED @AccountId = ?"
        cursor5 = db.cursor()
        cursor5.execute(query5, (user_id,))
        rows2 = cursor5.fetchall()
        productsxcategory = []
        for row in rows2:
            productsxcategory2 = ProductxCategory(row[0], row[1], row[2])
            productsxcategory.append(productsxcategory2)
        cursor5.close()
        
        return render_template('home.html', dato1=dato1, dato2=dato2, dato3=dato3, lastorders=lastorders, productsxcategory=productsxcategory)


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

        
@app.route('/cambiar_estado_proveedor', methods=['POST'])
@login_required
def cambiar_estado_proveedor():
    suppliers_id = request.form['suppliers_id']
    if ModelSupplier.updatesupplier(db, suppliers_id):
        flash('Proveeor actualizado correctamente', 'success')
    else:
        flash('Error al actualizar proveedor', 'danger')
    
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

        
@app.route('/cambiar_estado_cliente', methods=['POST'])
@login_required
def cambiar_estado_cliente():
    cliente_id = request.form['cliente_id']
    if ModelClient.updateclient(db, cliente_id):
        flash('Cliente actualizado correctamente', 'success')
    else:
        flash('Error al actualizar cliente', 'danger')
    
    return redirect(url_for('clientes'))

        
#metodos crud productos
@app.route('/productos', methods=['GET', 'POST'])
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
        
@app.route('/cambiar_estado_producto', methods=['POST'])
@login_required
def cambiar_estado_producto():
    producto_id = request.form['product_id']
    if ModelProduct.updateproduct(db, producto_id):
        flash('Producto actualizado correctamente', 'success')
    else:
        flash('Error al actualizar producto', 'danger')
    
    return redirect(url_for('productos'))






#METODOS CRUD ORDENES DE COMPRA
@app.route('/ordenes_compra', methods=['GET', 'POST'])
@login_required
def orden_compra():
    if request.method == 'GET':
        products = ModelProduct.get_all(db)
        orders = ModelPurchaseOrder.get_all(db)
        supplier = ModelSupplier.get_all(db)
        return render_template('BuyOrders.html', products=products, orders=orders, supplier=supplier)
    if request.method == 'POST':
        #obtener la fecha actual
        #fecha_actual = datetime.datetime.now()
        order = PurchaseOrder('',request.form['entrydate'], request.form['format'], request.form['totalquantity'], request.form['comments'], request.form['quantitylost'], request.form['account_id'], 'Pendiente', request.form['supplier_id'])
        products_ids = request.form.getlist('producto_id[]')
        cantidades = request.form.getlist('cantidad[]')
        print(order.id)
        if ModelPurchaseOrder.post(db,order):
            #si la lista de productos no esta vacia
            if products_ids:
                for producto_id, cantidad in zip(products_ids, cantidades):
                    ModelOrderXproduct.agregar_producto_a_orden(db, order.id , producto_id, cantidad)
                    print( "producto agregado correctamente" )
            
            flash('Orden agregada correctamente','success')
            return redirect(url_for('orden_compra'))
        else:
            flash('Error al agregar orden','danger')
            return redirect(url_for('orden_compra'))
      




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

