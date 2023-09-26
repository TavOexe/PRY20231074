from .entities.PurchaseOrder import PurchaseOrder

class ModelPurchaseOrder():
    @classmethod
    def get_all(self,db):
        try:
            cursor = db.cursor()
            cursor.execute("Select po.id, po.entrydate, po.format, po.totalquantity, po.comments, po.quantitylost, a.name, po.state, s.name from purchase_order po inner join account a on po.account_id = a.id inner join supplier s on po.supplier_id = s.id ")
            rows = cursor.fetchall()
            purchaseorders = []
            for row in rows:
                purchaseorder = PurchaseOrder(row[0], row[1], row[2], row[3], row[4], row[5], row[6],row[7],row[8])
                purchaseorders.append(purchaseorder)
            return purchaseorders
        except Exception as e:
            print(e)

    @classmethod
    def generate_new_order_id(cls, db):
        try:
            cursor = db.cursor()
            cursor.execute("SELECT MAX(id) FROM purchase_order")
            result = cursor.fetchone()
            max_id = result[0]

            if max_id is not None:
                # Extrae el número actual de la cadena y conviértelo a int
                current_number = int(max_id.split("-")[1])
                # Incrementa el número
                new_number = current_number + 1
            else:
                # Si no hay registros existentes, comienza desde 1
                new_number = 1

            # Crea el nuevo ID en el formato deseado con tres dígitos
            new_id = f"ORD-{new_number:05}"
            return new_id
        except Exception as e:
            print(e)
            print("Error while generating new order ID")

    @classmethod
    def post(cls, db, purchaseorder):
        try:
            if purchaseorder.entrydate != '' and purchaseorder.format != '' and purchaseorder.totalquantity != '' and purchaseorder.comments != '' and purchaseorder.quantitylost != '' and purchaseorder.account_id != '' and purchaseorder.state != '' and purchaseorder.supplier_id != '':  
                cursor = db.cursor()
                
                # Genera un nuevo ID de orden
                new_order_id = cls.generate_new_order_id(db)
                purchaseorder.id = new_order_id
                print(new_order_id)
                # Utiliza marcadores de posición en la consulta SQL
                cursor.execute("INSERT INTO purchase_order (id, entrydate, format, totalquantity, comments, quantitylost, account_id, state, supplier_id) VALUES ('{}','{}','{}','{}','{}','{}','{}','{}','{}')".format( purchaseorder.id , purchaseorder.entrydate, purchaseorder.format, purchaseorder.totalquantity, purchaseorder.comments, purchaseorder.quantitylost, purchaseorder.account_id, purchaseorder.state, purchaseorder.supplier_id))
                db.commit()
                return True
        except Exception as e:
            db.rollback()
            print(e)
            return False
    """
     @classmethod
    def post(self,db,purchaseorder):
        try:
            if purchaseorder.entrydate != '' and purchaseorder.format != '' and purchaseorder.totalquantity != '' and purchaseorder.comments != '' and purchaseorder.quantitylost != '' and purchaseorder.account_id != '' and purchaseorder.state != '' and purchaseorder.supplier_id != '':  
                cursor = db.cursor()
                #cursor.execute("INSERT INTO purchase_order (entrydate,format,totalquantity,comments,quantitylost,account_id,state,supplier_id) VALUES ('{}','{}','{}','{}','{}','{}','{}','{}')".format(purchaseorder.entrydate,purchaseorder.format,purchaseorder.totalquantity,purchaseorder.comments,purchaseorder.quantitylost,purchaseorder.account_id,purchaseorder.state,purchaseorder.supplier_id))
                cursor.execute("INSERT INTO purchase_order (id,entrydate,format,totalquantity,comments,quantitylost,account_id,state,supplier_id) VALUES ('{}','{}','{}','{}','{}','{}','{}','{}','{}')".format(purchaseorder.id ,purchaseorder.entrydate,purchaseorder.format,purchaseorder.totalquantity,purchaseorder.comments,purchaseorder.quantitylost,purchaseorder.account_id,purchaseorder.state,purchaseorder.supplier_id))
                db.commit()
                return True
        except Exception as e:
            db.rollback()
            print(e)
            return False 
    
    """
      