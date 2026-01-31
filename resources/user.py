from flask_restful import Resource, reqparse
from flask_bcrypt import check_password_hash, generate_password_hash
from models import User, Property, Payment, db
from flask_jwt_extended import  create_access_token, jwt_required  
from flask_jwt_extended import current_user 
from utils import admin_required                                                  


class Signup(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('first_name', required=True, help='First name is required')
    parser.add_argument('last_name', required=True, help='Last name is required')
    parser.add_argument('phone', required=True, help='Phone number is required')
    parser.add_argument('email', required=True, help='Email is required')
    parser.add_argument('password', required=True, help='Password is required')
    parser.add_argument('role', required=True, help="Role is required")
    
    def post(self):
        data = Signup.parser.parse_args()
          # hash password
        data['password'] = generate_password_hash(data['password'])
        # data['role'] = 'user'

        user = User(**data)
        
        # verify the uniquness of the email and phone in the db
        email = User.query.filter_by(email = data['email']).one_or_none()

        if email:
            return {"message": "Email already taken", "status": "fail"}, 400
        
        phone = User.query.filter_by(phone = data['phone']).one_or_none()

        if phone:
            return {"message": "Phone number already taken", "status": "fail"}, 400

        try:
            # save user to the db
            db.session.add(user)
            db.session.commit()

            user_json = user.to_dict()


            access_token = create_access_token(identity=user_json['id'], additional_claims={'role':user_json['role']})
            

            return {"message": "Account created successfully", "status": "success", "user": user.to_dict(rules=('-password',)), "access_token":access_token}, 201
        
        except:
            return {"message": "Unable to create account", "status": "fail"}, 400

class Login(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('email', required=True, help="Email is required")
    parser.add_argument('password', required=True, help="Password is required")

    def post(self):
        data = Login.parser.parse_args()

        # Get user using email
        user = User.query.filter_by(email = data['email']).first()

        if user:
        # Check if password provided is correct
               is_password_correct = user.check_password(data['password'])

               if is_password_correct:
                   
                   user_json = user.to_json()
                   access_token = create_access_token(identity=user_json['id'], additional_claims={'role':user_json['role']})
                   
         # Generate a token and return user dict
                   return {"message" : "Login successful", "status" : "success", "user":user.to_dict(rules=("-password",)), "access_token":access_token}, 200
               else:
                   return {"message" : "Invalid email/passwprd", "status": "fail"}, 403

        else:
            return {"message" : "Invalid email/password", "status" : "fail"}, 403  

class UsersResource(Resource):
    @admin_required()
    def get(self):
        # if current_user['role'] != "admin":
        #  return {"message": "Unauthorized request"}, 403
        users = User.query.all()
         
        return [user.to_dict() for user in users], 200
    
class AdminStatsResource(Resource):
    @admin_required()
    def get(self):
        total_users = User.query.count()
        active_agents = User.query.filter_by(role='agent').count()
        total_properties = Property.query.count()
        total_revenue = db.session.query(db.func.sum(Payment.amount)).scalar() or 0

        return {
            "total_users": total_users,
            "active_agents": active_agents,
            "total_properties": total_properties,
            "total_revenue": total_revenue
        }, 200  

class PendingAgentAproval(Resource):
    @admin_required()
    def get(self):
        agents = User.query.filter_by(role='agent', is_verified=True).all()

        return [
            {
                "name": f"{a.first_name} {a.last_name}",
                "email": a.email,
                "phone": a.phone,
                "date": a.created_at.strftime("%b %d, %Y")
            }
            for a in agents
        ], 200
    
class RecentUsers(Resource):
    @admin_required()
    def get(self):
        users = (
            User.query
            .order_by(User.created_at.desc())
            .limit(10)
            .all()
        )

        return [
            {
                "name": f"{u.first_name} {u.last_name}",
                "email": u.email,
                "role": u.role.capitalize(),
                "date": u.created_at.strftime("%b %d, %Y"),
                "status": "active" if u.is_verified else "inactive"
            }
            for u in users
        ], 200



    


