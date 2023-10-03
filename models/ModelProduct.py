from .entities.Product import Product

class ModelProduct():
    @classmethod
    def get_all(self,db):
        try:
            cursor = db.cursor()
            cursor.execute("SELECT id,name, description,image, SKU, Estado FROM Product")
            rows = cursor.fetchall()
            products = []
            for row in rows:
                product = Product(row[0], row[1], row[2], row[3], row[4], row[5])
                products.append(product)
            return products
        except Exception as e:
            print(e)

    @classmethod
    def get_by_id(self,db,id):
        try:
            cursor = db.cursor()
            cursor.execute("SELECT id,name, description,image, SKU, Estado FROM Product WHERE id = '{}' ".format(id))
            row = cursor.fetchone()
            if row is not None:
                product = Product(row[0], row[1], row[2], row[3], row[4], row[5])
                return product
            else:
                return  None
        except Exception as e:
            print(e)
    
    @classmethod
    def post(self,db,product):
        try:
            if product.name != '' and product.description != '':  
                cursor = db.cursor()
                cursor.execute("INSERT INTO Product (name, description,image, SKU, Estado) VALUES ('{}','{}','{}', '{}', '{}')".format(product.name,product.description,product.image, product.SKU, "Activo"))
                db.commit()
                return True
        except Exception as e:
            db.rollback()
            print(e)
            return False
        
    @classmethod
    def delete(self,db,id):
        try:
            cursor = db.cursor()
            cursor.execute("DELETE FROM Product WHERE id = '{}' ".format(id))
            db.commit()
            return True
        except Exception as e:
            db.rollback()
            print(e)
            return False
        
    @classmethod
    def updateproduct(cls, db, product_id):
        try:
            cursor = db.cursor()
            cursor.execute("SELECT Estado FROM Product WHERE Id = ?", (product_id,))
            estado_actual = cursor.fetchone()
        
            if estado_actual:
                nuevo_estado = "No Activo" if estado_actual[0] == "Activo" else "Activo"
                cursor.execute("UPDATE Product SET Estado = ? WHERE Id = ?", (nuevo_estado, product_id))
                db.commit()
                return True
            else:
                return False  # El cliente no fue encontrado
        except Exception as e:
            db.rollback()
            print(f"Error al actualizar el estado del producto: {e}")
            return False
        
        
