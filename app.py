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
        return redirect(url_for('dashboard'))
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


@app.route('/inicio')
@login_required
def dashboard():
    return render_template('home.html')

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
      

#MEOTODS PARA LA ASGINACION DE CALIDAD DE LAS ORDENES DE COMPRA
@app.route('/orden/<string:id>', methods=['GET', 'POST'])
@login_required
def orden_compra_detalle(id):
    if request.method == 'GET':
        cursor = db.cursor()
        cursor.execute(" SELECT p.Name , p.Image, op.amount, op.state, p.id FROM Product AS p JOIN orderXproducts AS op ON p.id = op.or_Product_Id WHERE op.purchase_order_Id =  '{}' and  CAST(op.state AS VARCHAR(255)) = 'pendiente'  ".format(id) )
        products = cursor.fetchall()
        cursor.execute("SELECT id, name FROM quality")
        calidades = cursor.fetchall()
        if products == []:
            cursor.execute("UPDATE purchase_order SET state = 'Asignado' WHERE id = '{}'".format(id))
            flash('Esta orden de compra no tiene productos por asignar','warning')
            cursor.commit()
            cursor.close()
            return redirect(url_for('orden_compra'))
        cursor.close()
        return render_template('order.html', products=products, calidades=calidades, id = id)
    if request.method == 'POST':
        cursor = db.cursor()
        producto_id = request.form['producto_id']
        orden_id = request.form['orden_id']
        fecha_actual = datetime.datetime.now()
        print("producto_id: ", producto_id )
        calidad_ids = request.form.getlist('calidad_id[]')
        cantidades = request.form.getlist('cantidad[]')
        print("calidad_ids: ", calidad_ids )
        print("cantidades: ", cantidades )
        try:
            for calidad_id, cantidad in zip(calidad_ids, cantidades):
                data = StockControl(0, producto_id, calidad_id, cantidad, fecha_actual, 0)
                ModelStockControl.post(db, data)
                if ModelStockControl.post(db, data):
                    cursor.execute("UPDATE orderXproducts SET state = 'completado' WHERE purchase_order_Id = '{}' AND or_Product_Id = {}".format(orden_id, producto_id))
                    flash('Producto agregado correctamente','success')
                print("producto agregado correctamente" )
            db.commit()
        except Exception as e:
            db.rollback()
            flash('Error al procesar la orden: {}'.format(str(e)), 'danger')
        finally:
            cursor.close()
        return redirect(url_for('orden_compra_detalle', id=orden_id))



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

