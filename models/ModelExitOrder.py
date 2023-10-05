from .entities.ExitOrder import ExitOrder
class ModelExitOrder():
    @classmethod
    def generate_new_order_id(cls, db):
        try:
            cursor = db.cursor()
            cursor.execute("SELECT MAX(id) FROM exit_order")
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
    def post(cls, db, exitorder):
        try:
            if exitorder.saledate != '' and exitorder.comments != '' and exitorder.totalprice != '' and exitorder.address != '' and exitorder.account_id != '' and exitorder.client_id != '' :  
                cursor = db.cursor()
                #fecha de hoy
                #date = datetime.datetime.now()
                # Genera un nuevo ID de orden
                new_order_id = cls.generate_new_order_id(db)
                exitorder.id = new_order_id
                print(new_order_id)
                # Utiliza marcadores de posición en la consulta SQL
                cursor.execute("INSERT INTO exit_order (id, saledate, comments, totalprice, address, account_id, client_id) VALUES ('{}','{}','{}','{}','{}','{}','{}')".format( exitorder.id , exitorder.saledate, exitorder.comments, exitorder.totalprice, exitorder.address, exitorder.account_id, exitorder.client_id))
                db.commit()
                return True
        except Exception as e:
            db.rollback()
            print(e)
            return False
    
    @classmethod
    def get_all(cls,db):
        try:
            cursor = db.cursor()
            cursor.execute(""" 
                            SELECT EO.Id, EO.saledate , SUM(CO.quantity) As 'cantidadtotal', SUM(CO.total_product_price) As 'preciototal', 
                            EO.comments, CONCAT(A.Name, ' ', A.LastName) As 'responsable', CONCAT(C.Name, ' ', C.LastName) As 'cliente' 
                            FROM exit_order EO INNER JOIN controlXoutput CO 
                            On CO.exit_order_Id = EO.Id INNER JOIN Account A 
                            On A.Id = EO.Account_Id INNER JOIN Client C 
                            On C.Id = EO.Client_Id 
                            GROUP BY EO.Id, EO.saledate, EO.comments, CONCAT(A.Name, ' ', A.LastName), CONCAT(C.Name, ' ', C.LastName) order by eo.saledate desc
                            """)
            rows = cursor.fetchall()
            exitorders = []
            for row in rows:
                exitorder = ExitOrder(row[0], row[1], row[2], row[3], row[4], row[5], row[6])
                exitorders.append(exitorder)
            
            cursor.close()
            return rows
        except Exception as e:
            print(e)