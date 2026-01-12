from flask import Flask
from flask_migrate import Migrate
from models import db

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///agsproperties.db"

app.config["SQLALCHEMY_ECHO"] = True

migrate = Migrate(app, db)

# link db to the flask instance
db.init_app(app)

# db.init_app(app)
@app.route('/')
def index():
    return {'message' : 'Welcome to ags backend'}, 200








if __name__ == '__main__':
    app.run(port=5555, debug=True)