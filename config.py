DEBUG = True
DB_URL = "dbname=taskManager"
SECRET = "s3cr3t"
SALT = "S4lTH3r3"


try:
    from local_config import *
except ImportError:
    print("No local config found!")
