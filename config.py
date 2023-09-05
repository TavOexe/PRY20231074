class Config:
    SECRET_KEY = 'mysecretkey'

class DevelopmentConfig (Config):
    DEBUG = True
    DRIVER = 'SQL Server'
    SERVER = "LAPTOP-KU7B7VQF"
    DATABASE = "agrodbPrueba"
    #uid = 'gmanuser'
    #pwd = '#Gc949194518'
    
    connection_string = f'DRIVER={DRIVER};SERVER={SERVER};DATABASE={DATABASE};'
    

config = {
    'development': DevelopmentConfig,
}


