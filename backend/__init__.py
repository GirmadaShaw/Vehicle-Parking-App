import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_cors import CORS
import redis 
from celery import Celery

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv("FLASK_SECRET")
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.sqlite3'
app.config['JWT_SECRET_KEY'] = os.getenv("JWT_SECRET")
# 'W3T1Knab5FB7yWZgu_A81tZBjmwxNaLSzQu5ulx-H3E'
app.config['CELERY_BROKER_URL'] = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0")
app.config['CELERY_RESULT_BACKEND'] = os.getenv("CELERY_RESULT_BACKEND", "redis://localhost:6379/0")

CORS(app,   resources={ 
                        r"/*":{
                            'origins': 'http://localhost:5173',
                            # 'allow_headers': 'Access-Control-Allow-Origin'
                        }},
            supports_credentials=True,
            methods = ["GET", "PUT", "POST", "DELETE", "OPTIONS"],
            allow_headers=["Content-Type", "Authorization"]
    )

redis_client = redis.Redis(
    host=os.getenv("REDIS_HOST", "localhost"),
    port=int(os.getenv("REDIS_PORT", 6379)),
    db=0,
    decode_responses=True 
)

celery = Celery(app.import_name,
                broker=app.config['CELERY_BROKER_URL'],
                backend=app.config['CELERY_RESULT_BACKEND'])

class ContextTask(celery.Task):
    def __call__(self, *args, **kwargs):
        with app.app_context():
            return self.run(*args, **kwargs)
celery.Task = ContextTask



db = SQLAlchemy()
db.init_app(app)
jwt = JWTManager(app)

app.app_context().push() 

from backend import routes

