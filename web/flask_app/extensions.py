from flask_argon2 import Argon2
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_wtf.csrf import CSRFProtect
# from flask_socketio import SocketIO
from flask_mqtt import Mqtt

# Initialize flask extensions
argon2 = Argon2()
db = SQLAlchemy()
migrate = Migrate()
csrf = CSRFProtect()
# socketio = SocketIO()
mqtt = Mqtt()
