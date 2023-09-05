from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

class User(UserMixin):
    def __init__(self, id, name,lastname,user_type_id,email,password,cellphone) -> None:
        self.id = id
        self.name = name
        self.lastname = lastname
        self.user_type_id = user_type_id
        self.email = email
        self.password = password
        self.cellphone = cellphone

    @classmethod
    def check_password(self,hashed_password ,password):
        return check_password_hash(hashed_password, password)
    
