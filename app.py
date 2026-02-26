from flask import Flask, send_from_directory
from flask_migrate import Migrate
from models import db, User
from flask_restful import Api, Resource
from flask_bcrypt import Bcrypt
from resources.auth import Signup, Login, Logout
from resources.admin import UsersResource, AdminStatsResource, PendingAgentAproval, RecentUsers, PropertyResource, AgentApproval
from resources.user import UserProfileResource, UserStatsResource, SavedPropertiesResource, RecentActivitiesResource, UserPropertiesResource, UserPropertyDetailResource, ToggleFavoriteResource, RecordPropertyViewResource, CreateInquiryResource, UserInquiriesResource, UserConversationsResource, ConversationMessagesResource, StartConversationResource, ScheduleVisitResource, UserScheduledVisitsResource
from resources.agent import AgentStatsResource, AgentPropertiesResource, AgentInquiriesResource, AgentPropertyDetailResource, AgentPropertyCreateResource, AgentPropertyUpdateResource, AgentPropertyDeleteResource
from flask_jwt_extended import JWTManager
from flask_cors import CORS
import os
from dotenv import load_dotenv

load_dotenv(override=True) 

# Initialized flask app
app = Flask(__name__)

# configure db URI
database_url = os.getenv("DATABASE_URL")
if not database_url:
    # Fallback for local development
    database_url = "sqlite:///agsproperties.db"
    
app.config["SQLALCHEMY_DATABASE_URI"] = database_url

# Disable SQL echo to prevent logging loop
app.config["SQLALCHEMY_ECHO"] = True

app.config["BUNDLE_ERRORS"] = True

# Setup flask-JWT-extended extension
# Use environment variable or fallback to a fixed default (for development only)
jwt_secret = os.getenv("JWT_SECRET_KEY")
if not jwt_secret:
    # WARNING: This is only for development. In production, always set JWT_SECRET_KEY env var
    # Using a static key so tokens remain valid across restarts
    jwt_secret = "ags-properties-dev-secret-key-do-not-use-in-production"
    print("WARNING: Using default JWT_SECRET_KEY. Set JWT_SECRET_KEY env var for production!")

app.config["JWT_SECRET_KEY"] = jwt_secret

#flask cors
allowed_origins = [
    "http://localhost:5173",  # local dev
    "https://agsproperties.vercel.app",  # your deployed frontend
    "*"  # Allow all origins in development
]

CORS(
    app,
    resources={r"/*": {"origins": allowed_origins}},
    supports_credentials=True,
    methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization", "X-Requested-With"],
    expose_headers=["Content-Type", "Authorization"],
    max_age=86400,
    automatic_options=True  # Let Flask-CORS handle OPTIONS automatically
)

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

# Create uploads folder if it doesn't exist
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Route to serve uploaded files
@app.route('/uploads/<path:filename>')
def serve_upload(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

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
api.add_resource(Logout, '/logout')
api.add_resource(UsersResource, '/users')
api.add_resource(AdminStatsResource, '/admin/stats')
api.add_resource(PendingAgentAproval, '/admin/pending-approvals')
api.add_resource(AgentApproval, '/admin/approve/<int:user_id>')
api.add_resource(RecentUsers, '/admin/recent-users')

api.add_resource(PropertyResource, '/properties')

# user routes
api.add_resource(UserProfileResource, '/user/profile')
api.add_resource(UserStatsResource, '/user/stats')
api.add_resource(SavedPropertiesResource, '/user/saved-properties')
api.add_resource(RecentActivitiesResource, '/user/recent-activity')
api.add_resource(UserPropertiesResource, '/user/properties')
api.add_resource(UserPropertyDetailResource, '/user/properties/<int:property_id>')
api.add_resource(ToggleFavoriteResource, '/user/favorite')
api.add_resource(RecordPropertyViewResource, '/user/record-view')

# Inquiry routes
api.add_resource(CreateInquiryResource, '/user/inquiry')
api.add_resource(UserInquiriesResource, '/user/inquiries')

# Messaging routes
api.add_resource(StartConversationResource, '/user/conversation/start')
api.add_resource(UserConversationsResource, '/user/conversations')
api.add_resource(ConversationMessagesResource, '/user/conversations/<int:conversation_id>')

# Visit scheduling routes
api.add_resource(ScheduleVisitResource, '/user/schedule-visit')
api.add_resource(UserScheduledVisitsResource, '/user/scheduled-visits')

# agents routes
api.add_resource(AgentStatsResource, '/agent/stats')
api.add_resource(AgentPropertiesResource, '/agent/properties')
api.add_resource(AgentPropertyDetailResource, '/agent/properties/<int:property_id>')
api.add_resource(AgentPropertyCreateResource, '/agent/properties/create')
api.add_resource(AgentPropertyUpdateResource, '/agent/properties/<int:property_id>/edit')
api.add_resource(AgentPropertyDeleteResource, '/agent/properties/<int:property_id>/delete')
api.add_resource(AgentInquiriesResource, '/agent/inquiries')



if __name__ == '__main__':
    app.run(port=5555, debug=True)
