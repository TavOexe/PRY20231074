#class Config:
#    SECRET_KEY = 'mysecretkey'

#class DevelopmentConfig (Config):
#    DEBUG = True
#    DRIVER = 'SQL Server'
#   SERVER = "DESKTOP-NT6FMGV\SQLEXPRESS"
#    DATABASE = "agrodb"
    #uid = 'gmanuser'
    #pwd = '#Gc949194518'
    
#    connection_string = f'DRIVER={DRIVER};SERVER={SERVER};DATABASE={DATABASE};'
    

#config = {
#    'development': DevelopmentConfig,
#}

class Config:
    SECRET_KEY = 'mysecretkey'

class DevelopmentConfig (Config):
    DEBUG = True
    DRIVER = 'ODBC Driver 17 for SQL Server'
    SERVER = 'LAPTOP-20OHRHFA'
    DATABASE = 'TP2_Test'
    #uid = 'gmanuser'
    #pwd = '#Gc949194518'
    connection_string = f"""DRIVER={DRIVER};SERVER={SERVER};DATABASE={DATABASE};Trusted_Connection=yes"""
    

config = {
    'development': DevelopmentConfig,
}


