from flask import Flask
from flask_migrate import Migrate
from models import db, User
from flask_restful import Api, Resource
from flask_bcrypt import Bcrypt
from resources.user import Signup, Login, UsersResource, AdminStatsResource, PendingAgentAproval, RecentUsers, PropertyResource
from flask_jwt_extended import JWTManager
from flask_cors import CORS

# Initialized flask app
app = Flask(__name__)

# configure db URI
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///agsproperties.db"

app.config["SQLALCHEMY_ECHO"] = True

app.config["BUNDLE_ERRORS"] = True

# Setup flask-JWT-extended extension
app.config["JWT_SECRET_KEY"] = 'super-secret'

#flask cors
CORS(app)

# link migration
migrate = Migrate(app, db)

# init our db
db.init_app(app)

# initialize flask restful
api = Api(app)

# initialize bcrypt
bcrypt = Bcrypt(app)

# initialize jwt
jwt = JWTManager(app)

# Register a callback function that loads a user from your database whenever
# a protected route is accessed. This should return any python object on a
# successful lookup, or None if the lookup failed for any reason (for example
# if the user has been deleted from the database).
# @jwt.user_lookup_loader
# def user_lookup_callback(_jwt_header, jwt_data):
#     identity = jwt_data["sub"]
#     user = User.query.filter_by(id=identity).one_or_none()

#     if user is None:
#         return {}
#     else:
#         return user

# db.init_app(app)
@app.route('/')
def index():
    return {'message' : 'Welcome to ags backend'}, 200




# Routes
api.add_resource(Signup, '/signup')
api.add_resource(Login, '/login')
api.add_resource(UsersResource, '/users')
api.add_resource(AdminStatsResource, '/admin/stats')
api.add_resource(PendingAgentAproval, '/admin/pending-approvals')
api.add_resource(RecentUsers, '/admin/recent-users')

api.add_resource(PropertyResource, '/properties')








if __name__ == '__main__':
    app.run(port=5555, debug=True)