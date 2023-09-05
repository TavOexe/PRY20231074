from .entities.Product import Product

class ModelProduct():
    @classmethod
    def get_all(self,db):
        try:
            cursor = db.cursor()
            cursor.execute("SELECT id,name, description,image FROM Product")
            rows = cursor.fetchall()
            products = []
            for row in rows:
                product = Product(row[0], row[1], row[2], row[3])
                products.append(product)
            return products
        except Exception as e:
            print(e)

    @classmethod
    def get_by_id(self,db,id):
        try:
            cursor = db.cursor()
            cursor.execute("SELECT id,name, description,image FROM Product WHERE id = '{}' ".format(id))
            row = cursor.fetchone()
            if row is not None:
                product = Product(row[0], row[1], row[2], row[3])
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
                cursor.execute("INSERT INTO Product (name, description,image) VALUES ('{}','{}','{}')".format(product.name,product.description,product.image))
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
        
        
