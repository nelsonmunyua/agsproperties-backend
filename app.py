from flask import Flask
from flask_migrate import Migrate
from models import db
from flask_restful import Api, Resource
from flask_bcrypt import Bcrypt
from resources.user import Signup

# Initialized flask app
app = Flask(__name__)

# configure db URI
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///agsproperties.db"

app.config["SQLALCHEMY_ECHO"] = True

# link migration
migrate = Migrate(app, db)

# init our db
db.init_app(app)

# initialize flask restful
api = Api(app)

# db.init_app(app)
@app.route('/')
def index():
    return {'message' : 'Welcome to ags backend'}, 200

api.add_resource(Signup, '/signup')








if __name__ == '__main__':
    app.run(port=5555, debug=True)