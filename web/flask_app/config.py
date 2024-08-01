from dotenv import load_dotenv
from os import path, environ

# Load flask environment variables (.flaskenv-sample)
flaskenv_path = path.join(path.dirname(__file__), "../.flaskenv-sample")
load_dotenv(flaskenv_path)

# DbConfig configuration
class DbConfig(object):
  SQLALCHEMY_DATABASE_URI = environ.get("DATABASE_URL")
  SQLALCHEMY_TRACK_MODIFICATIONS = False
  SQLALCHEMY_RECORD_QUERIES = True
  SQLALCHEMY_ENGINE_OPTIONS = {
    "pool_pre_ping": True,
    "pool_recycle": 300,
    "pool_timeout": 30,
    "pool_size": 10,
    "max_overflow": 20,
  }

# TestingConfig configuration
class TestingConfig(DbConfig):
  DEBUG = True
  TESTING = True
  SECRET_KEY = str(environ.get("SECRET_KEY"))
  ARGON2_HASH_LENGTH = 32
  ARGON2_SALT_LENGTH = 8
  MQTT_BROKER_URL = str(environ.get("MQTT_BROKER_URL"))
  MQTT_BROKER_PORT = int(environ.get("MQTT_BROKER_PORT"))
  MQTT_TLS_ENABLED = False
  MQTT_LAST_WILL_QOS = 0
  MQTT_KEEPALIVE = 180

# ProductionConfig configuration
class ProductionConfig(DbConfig):
  DEBUG = False
  TESTING = False
  SECRET_KEY = str(environ.get("SECRET_KEY"))
  ARGON2_HASH_LENGTH = 64
  ARGON2_SALT_LENGTH = 16
  MQTT_BROKER_URL = str(environ.get("MQTT_BROKER_URL"))
  MQTT_BROKER_PORT = int(environ.get("MQTT_BROKER_PORT"))
  MQTT_TLS_ENABLED = False
  MQTT_LAST_WILL_QOS = 0
  MQTT_KEEPALIVE = 180
