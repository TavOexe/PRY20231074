from .entities.User import User
class ModelUser():
    @classmethod
    def login(self,db,user):
        try:
            cursor = db.cursor()
            cursor.execute("SELECT id,name,lastname,user_type_id,email,password,cellphone FROM Account WHERE email = '{}' ".format(user.email))
            row = cursor.fetchone()
            if row is not None:
                user = User(row[0], row[1], row[2], row[3], row[4], row[5], row[6])
                return user
            else:
                return  None
            
        except Exception as e:
            print(e)
    
    @classmethod
    def get_by_id(self,db,id):
        try:
            cursor = db.cursor()
            cursor.execute("SELECT id,name,lastname,user_type_id,email,password,cellphone FROM Account WHERE id = '{}' ".format(id))
            row = cursor.fetchone()
            if row is not None:
                user = User(row[0], row[1], row[2], row[3], row[4], row[5], row[6])
                return user
            else:
                return  None
        except Exception as e:
            print(e)





#probar una contraseña de 

            