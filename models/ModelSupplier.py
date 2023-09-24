from .entities.Supplier import Supplier

class ModelSupplier():
    @classmethod
    def get_all(self,db):
        try:
            cursor = db.cursor()
            cursor.execute("SELECT id, ruc,name, lastname,email,cellphone FROM Supplier")
            rows = cursor.fetchall()
            suppliers = []
            for row in rows:
                supplier = Supplier(row[0], row[1], row[2], row[3], row[4], row[5])
                suppliers.append(supplier)
            return suppliers
        except Exception as e:
            print(e)
    
    @classmethod
    def get_by_id(self,db,id):
        try:
            cursor = db.cursor()
            cursor.execute("SELECT id, ruc,name, lastname,email,cellphone FROM Supplier WHERE id = '{}' ".format(id))
            row = cursor.fetchone()
            if row is not None:
                supplier = Supplier(row[0], row[1], row[2], row[3], row[4], row[5])
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
                cursor.execute("INSERT INTO Supplier (ruc, name, lastname, email, cellphone) VALUES ('{}','{}','{}','{}','{}')".format(supplier.ruc,supplier.name,supplier.lastname,supplier.email,supplier.cellphone))
                db.commit()
                return True
        except Exception as e:
            db.rollback()
            print(e)
            return False
        
    @classmethod
    def delete(self, db, suppliers_id):
        try:
            cursor = db.cursor()
            cursor.execute("DELETE FROM Supplier WHERE Id = '{}' ".format(suppliers_id))
            db.commit()
            return True
        except Exception as e:
            db.rollback()
            print(e)
            return False