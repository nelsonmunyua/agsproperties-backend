from flask_restful import Resource, reqparse
from flask_bcrypt import check_password_hash, generate_password_hash
from models import User, Property, Payment, PropertyImage, PropertyLocation, Location, db
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

