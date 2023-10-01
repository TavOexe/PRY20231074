from .entities.Client import Client

class ModelClient():
    @classmethod
    def get_all(self,db):
        try:
            cursor = db.cursor()
            cursor.execute("SELECT id, ruc,name, lastname,address, email,cellphone, Estado FROM Client")
            rows = cursor.fetchall()
            clients = []
            for row in rows:
                client = Client(row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7])
                clients.append(client)
            return clients
        except Exception as e:
            print(e)
    
    @classmethod
    def get_by_id(self,db,id):
        try:
            cursor = db.cursor()
            cursor.execute("SELECT id, ruc, name, lastname, address, email, cellphone, Estado FROM Client WHERE id = '{}' ".format(id))
            row = cursor.fetchone()
            if row is not None:
                client = Client(row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7])
                return client
            else:
                return  None
        except Exception as e:
            print(e)

    @classmethod
    def post(self,db,client):
        try:
            if client.ruc != '' and client.name != '' and client.lastname != '' and client.address != '' and client.email != '' and client.cellphone != '':  
                cursor = db.cursor()
                cursor.execute("INSERT INTO Client (ruc, name, lastname, address, email, cellphone, Estado) VALUES ('{}', '{}', '{}', '{}', '{}', '{}', '{}')".format(client.ruc, client.name, client.lastname, client.address, client.email, client.cellphone, "Activo"))
                db.commit()
                return True
        except Exception as e:
            db.rollback()
            print(e)
            return False
        
    @classmethod
    def updateclient(cls, db, cliente_id):
        try:
            cursor = db.cursor()
            cursor.execute("SELECT Estado FROM Client WHERE Id = ?", (cliente_id,))
            estado_actual = cursor.fetchone()
        
            if estado_actual:
                nuevo_estado = "No Activo" if estado_actual[0] == "Activo" else "Activo"
                cursor.execute("UPDATE Client SET Estado = ? WHERE Id = ?", (nuevo_estado, cliente_id))
                db.commit()
                return True
            else:
                return False  # El cliente no fue encontrado
        except Exception as e:
            db.rollback()
            print(f"Error al actualizar el estado del cliente: {e}")
            return False

      