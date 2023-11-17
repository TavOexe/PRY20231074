from .entities.Supplier import Supplier

class ModelSupplier():
    @classmethod
    def get_all(cls,db):
        try:
            cursor = db.cursor()
            cursor.execute("SELECT id, ruc,name, lastname,email,cellphone, Estado FROM Supplier")
            rows = cursor.fetchall()
            suppliers = []
            for row in rows:
                supplier = Supplier(row[0], row[1], row[2], row[3], row[4], row[5], row[6])
                suppliers.append(supplier)
            return suppliers
        except Exception as e:
            print(e)
    
    @classmethod
    def get_by_id(self,db,id):
        try:
            cursor = db.cursor()
            cursor.execute("SELECT id, ruc,name, lastname,email,cellphone, Estado FROM Supplier WHERE id = '{}' ".format(id))
            row = cursor.fetchone()
            if row is not None:
                supplier = Supplier(row[0], row[1], row[2], row[3], row[4], row[5], row [6])
                return supplier
            else:
                return  None
        except Exception as e:
            print(e)

    @classmethod
    def post(self,db,supplier):
        try:
            if supplier.ruc != '' and supplier.name != '' and supplier.lastname != '' and supplier.email != '' and supplier.cellphone != '':  
                cursor = db.cursor()
                cursor.execute("INSERT INTO Supplier (ruc,name, lastname,email,cellphone,Estado) VALUES ('{}','{}','{}','{}','{}', '{}')".format(supplier.ruc,supplier.name,supplier.lastname,supplier.email,supplier.cellphone, "Activo"))
                db.commit()
                return True
        except Exception as e:
            db.rollback()
            print(e)
            return False
    
    @classmethod
    def updatesupplier(cls, db, supplier_id):
        try:
            cursor = db.cursor()
            cursor.execute("SELECT Estado FROM Supplier WHERE Id = ?", (supplier_id,))
            estado_actual = cursor.fetchone()
        
            if estado_actual:
                nuevo_estado = "No Activo" if estado_actual[0] == "Activo" else "Activo"
                cursor.execute("UPDATE Supplier SET Estado = ? WHERE Id = ?", (nuevo_estado, supplier_id))
                db.commit()
                return True
            else:
                return False  # El cliente no fue encontrado
        except Exception as e:
            db.rollback()
            print(f"Error al actualizar el estado del proveedor: {e}")
            return False