from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_wtf.csrf import CSRFProtect
from config import config
from flask import jsonify
import requests
import json
import pypyodbc
import datetime
#models 
from models.ModelUser import ModelUser
from models.ModelSupplier import ModelSupplier
from models.ModelProduct import ModelProduct
from models.ModelClient import ModelClient
from models.ModelPurchaseOrder import ModelPurchaseOrder
from models.ModelOrderXproduct import ModelOrderXproduct
from models.ModelStockControl import ModelStockControl
from models.ModelExitOrder import ModelExitOrder
from models.ModelControlXoutput import ModelControlXoutput
#entities
from models.entities.Product import Product
from models.entities.Supplier import Supplier
from models.entities.User import User
from models.entities.Client import Client
from models.entities.PurchaseOrder import PurchaseOrder
from models.entities.stock_control import StockControl
from models.entities.ExitOrder import ExitOrder
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
def dashboard():
    cursor = db.cursor()
    cursor.execute('SELECT COUNT(*) FROM purchase_order')
    totalordenes = cursor.fetchone()[0]
    cursor.close()

    cursor = db.cursor()
    cursor.execute('SELECT SUM(amount) FROM orderXproducts')
    max_kilos = cursor.fetchone()[0]
    cursor.close()

    cursor = db.cursor()
    cursor.execute("SELECT SUM(total_product_price) FROM controlXoutput")
    totalventas = cursor.fetchone()[0]
    cursor.close()

    cursor = db.cursor()
    cursor.execute("""Select Top 5 PO.Id, CONCAT(A.Name, ' ', A.LastName) As 'name', PO.entrydate, PO.state
                        From purchase_order PO
                        Inner Join Account A On A.Id = PO.Account_Id
                        Order By entrydate Desc""")
    ordenes = cursor.fetchall()
    cursor.close()

    return render_template('home.html', totalordenes=totalordenes, max_kilos=max_kilos, totalventas=totalventas, ordenes=ordenes)

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



#//////////////////////////////////////

@app.route('/inventario')
@login_required
def inventario():
    cursor = db.cursor()
    cursor.execute(" SELECT sc.Id, p.Name, p.Image, q.Name as 'calidad', sc.quantity,  CONVERT(varchar(10), sc.date, 103) as 'fecha',  CONVERT(varchar(8), sc.date, 108) as 'hora',  sc.unity  FROM stock_control AS sc  JOIN Product AS p ON sc.product_id = p.id  JOIN quality AS q ON sc.quality_id = q.id")
    inventario = cursor.fetchall()
    if inventario == []:
        flash('No hay productos en el inventario, Asigna las calidades de las compras','warning')
        
    cursor.close()
    return render_template('inventory.html', inventario=inventario)


#METODOS CRUD ORDENES DE VENTA
@app.route('/ordenes_venta', methods=['GET', 'POST'])
@login_required
def orden_venta():
    if request.method == 'GET':
        orders = ModelExitOrder.get_all(db)
        client = ModelClient.get_all(db)
        products = ModelProduct.get_all(db)
        #obtener las calidades //////////////////////
        cursor = db.cursor()
        cursor.execute("SELECT * FROM Quality")
        quality = cursor.fetchall()
        cursor.close()
        #////////////////////////////////////////////
        return render_template('sellOrders.html', orders=orders, client=client, products=products, calidades=quality)

    if request.method == 'POST':
        #obtener la fecha actual
        #fecha_actual = datetime.datetime.now()
        order = ExitOrder('',request.form['account_id'], request.form['client_id'], request.form['saledate'], request.form['comments'], request.form['totalprice'], request.form['address'] )
      
        products_ids = request.form.getlist('producto_id[]')
        calidades_ids = request.form.getlist('calidades_id[]')
        cantidades = request.form.getlist('cantidad[]')
        precios = request.form.getlist('precio[]')
        print(order.id)
        print(products_ids)
        print(calidades_ids)
        print(cantidades)
        print(precios)
        peso = 'Kg'
        print(peso)
      
        if ModelExitOrder.post(db,order):
            formato = request.form['format']
            #si la lista de productos no esta vacia
            if products_ids:
                for product_ids,calidades_ids,cantidades,precios in zip(products_ids,calidades_ids,cantidades,precios):
                    ModelControlXoutput.agregar_producto_calidad_precio_orden(db, order.id , product_ids, calidades_ids, cantidades, precios, formato,peso)
                    print( "producto agregado correctamente" )
            
            flash('Orden agregada correctamente','success')
            return redirect(url_for('orden_venta'))
        else:
            flash('Error al agregar orden','danger')
            return redirect(url_for('orden_venta'))


@app.route('/obtener_stock/<int:producto_id>/<int:calidad_id>', methods=['GET'])
@login_required
def obtener_stock(producto_id, calidad_id):
    cursor = db.cursor()

    # Utiliza parámetros en la consulta SQL para evitar la inyección de SQL
    #query = "SELECT quantity FROM stock_control WHERE Product_Id = %s AND Quality_Id = %s"
    cursor.execute("Select quantity FROM stock_control WHERE Product_Id = {} AND Quality_Id = {}".format(producto_id, calidad_id))

    stock = cursor.fetchone()
    cursor.close()

    if stock is not None:
        stock = stock[0]  # El resultado de fetchone es una tupla, obtén el primer elemento

        response_data = {
            'cantidad_disponible': stock
        }
    else:
        response_data = {
            'cantidad_disponible': 0  # O cualquier otro valor predeterminado que desees en caso de que no se encuentre stock
        }

    return jsonify(response_data)

#//////////////////////////////////////

@app.route('/estadisticas', methods=['GET', 'POST'])
@login_required
def analytics():
    cursor = db.cursor()
    cursor.execute("""
                        SELECT DATENAME(MONTH, EO.saledate) AS 'mes', P.Name as 'producto', Q.Name, SUM(CO.quantity) AS 'cantidad' 
                        FROM exit_order EO 
                        INNER JOIN controlXoutput CO ON CO.exit_order_Id = EO.Id 
                        INNER JOIN Product P ON P.Id = CO.StockControl_Product_Id 
                        INNER JOIN Quality Q ON Q.Id = CO.StockControl_Quality_Id 
                        GROUP BY DATENAME(MONTH, EO.saledate), P.Name, Q.Name 
                        ORDER BY DATENAME(MONTH, EO.saledate) desc; """)
    ventas = cursor.fetchall()
    cursor.close()

    return render_template('analytics.html', data=ventas)

@app.route('/obtener_respuesta', methods=['POST'])
def obtener_respuesta():
    mensaje_usuario = request.form['mensaje_usuario']
    verdura = obtener_datos_verdura()
    ventasdata = obtener_datos_ventas()
    # Obtener la respuesta de OpenAI utilizando la función
    cursor = db.cursor()
    cursor.execute("""
                        SELECT DATENAME(MONTH, EO.saledate) AS 'mes', P.Name as 'producto', Q.Name, SUM(CO.quantity) AS 'cantidad' 
                        FROM exit_order EO 
                        INNER JOIN controlXoutput CO ON CO.exit_order_Id = EO.Id 
                        INNER JOIN Product P ON P.Id = CO.StockControl_Product_Id 
                        INNER JOIN Quality Q ON Q.Id = CO.StockControl_Quality_Id 
                        GROUP BY DATENAME(MONTH, EO.saledate), P.Name, Q.Name 
                        ORDER BY DATENAME(MONTH, EO.saledate) desc; """)
    ventas = cursor.fetchall()
    cursor.close()
    respuesta_openai = obtener_respuesta_openai(mensaje_usuario, verdura,ventasdata)

    return render_template('analytics.html', mensaje_usuario=mensaje_usuario, respuesta_openai=respuesta_openai,data=ventas)


@app.route('/api/almacen')
def api_usuario():
    cursor = db.cursor()
    cursor.execute("SELECT sc.Id, p.Name, q.Name as 'calidad', sc.quantity, CONVERT(varchar(10), sc.date, 103) as 'fecha', CONVERT(varchar(8), sc.date, 108) as 'hora', sc.unity FROM stock_control AS sc JOIN Product AS p ON sc.product_id = p.id JOIN quality AS q ON sc.quality_id = q.id")
    
    ventas = cursor.fetchall()
    cursor.close()
    
    # Crear una lista de diccionarios con el nombre de la data y el valor
    data = []
    for venta in ventas:
        data.append({
            "id": venta[0],
            "producto": venta[1],
            "calidad": venta[2],
            "cantidad": venta[3],
            "fecha": venta[4],
            "hora": venta[5],
            "unidad": venta[6]
        })
    
    # Devolver la lista como una respuesta JSON
    return jsonify({"data": data})

@app.route('/api/ventas')
def api_ventas():
    cursor = db.cursor()
    cursor.execute("""SELECT EO.Id, EO.saledate , SUM(CO.quantity) As 'cantidadtotal', SUM(CO.total_product_price) As 'preciototal', 
                            EO.comments, CONCAT(A.Name, ' ', A.LastName) As 'responsable', CONCAT(C.Name, ' ', C.LastName) As 'cliente' 
                            FROM exit_order EO INNER JOIN controlXoutput CO 
                            On CO.exit_order_Id = EO.Id INNER JOIN Account A 
                            On A.Id = EO.Account_Id INNER JOIN Client C 
                            On C.Id = EO.Client_Id 
                            GROUP BY EO.Id, EO.saledate, EO.comments, CONCAT(A.Name, ' ', A.LastName), CONCAT(C.Name, ' ', C.LastName) order by eo.saledate desc
                            """)
    ventas = cursor.fetchall()
    cursor.close()
    
    # Crear una lista de diccionarios con el nombre de la data y el valor
    data = []
    for venta in ventas:
        data.append({
            "id": venta[0],
            "fecha": venta[1],
            "cantidadtotal": venta[2],
            "preciototal": venta[3],
            "comentarios": venta[4],
            "responsable": venta[5],
            "cliente": venta[6]
        })
    
    # Devolver la lista como una respuesta JSON
    return jsonify({"data": data})

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))

def status_401(error):
    return "<h1> ERROR 401 </h1> ", 401

def status_404(error):
    return "<h1> ERROR 404 </h1> ", 404

API_KEY = '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'  # Reemplaza 'tu_api_key_aqui' con tu clave de API de OpenAI
API_URL = 'https://api.openai.com/v1/chat/completions'

# Función para obtener una respuesta de OpenAI
def obtener_respuesta_openai(mensaje_usuario, verdura,ventas):
    # Definir los parámetros para la conversación con OpenAI
    conversacion = [
        {"role": "system", "content": "Tú eres un asistente de chat de un sistema agropecuario y consumes datos de un API de datos abiertos, tu objetivo es devolver respuestas concretas sobre la siguiente data que te muestro a continuación, tienes esta data de inventario: " + json.dumps(verdura) + " y esta data de ventas: " + json.dumps(ventas) + ""},
        {"role": "user", "content": mensaje_usuario}
    ]

    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {API_KEY}'
    }

    data = {
        'model': 'gpt-4',  # Reemplaza con el modelo que desees utilizar
        'messages': conversacion
    }

    response = requests.post(API_URL, headers=headers, json=data)

    if response.status_code == 200:
        respuesta = response.json()['choices'][0]['message']['content']
        return respuesta
    else:
        print("Error al comunicarse con la API de OpenAI. Código de estado:", response.status_code)
        print(response.text)
        return None

# Consumir la API local de almacenamiento de verduras
def obtener_datos_verdura():
    url_local_api = 'http://192.168.1.15:4000/api/almacen'
    try:
        response = requests.get(url_local_api)
        response.raise_for_status()  # Lanzar una excepción en caso de error HTTP
        verdura = response.json()
    except requests.exceptions.RequestException as e:
        print("Error al comunicarse con la API local:", e)
        verdura = {}
    
    return verdura

def obtener_datos_ventas():
    url_local_api = 'http://192.168.1.15:4000/api/ventas'
    try:
        response = requests.get(url_local_api)
        response.raise_for_status()  # Lanzar una excepción en caso de error HTTP
        ventas = response.json()
    except requests.exceptions.RequestException as e:
        print("Error al comunicarse con la API local:", e)
        ventas = {}
    
    return ventas


if __name__ == '__main__':
    app.config.from_object(config['development'])
    #csrf.init_app(app)
    app.register_error_handler(401, status_401)
    app.register_error_handler(404, status_404)
    app.run(debug=True, port=4000,host="0.0.0.0")

