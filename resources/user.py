from flask_restful import Resource, reqparse
from flask_bcrypt import check_password_hash, generate_password_hash
from models import User, db


class Signup(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('name', required=True, help='Name is required')
    parser.add_argument('phone', required=True, help='Phone Number is required')
    parser.add_argument('email', required=True, help='Email is required')
    parser.add_argument('password', required=True, help='Password is required')
    
    def post(self):
        data = Signup.parser.parse_args()
          # hash password
        data['password'] = generate_password_hash(data['password'])
        data['role'] = 'user'

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
            

            return {"message": "Account created successfully", "status": "success", "user": user.to_dict(rules=('-password',))}, 201
        
        except:
            return {"message": "Unable to create account", "status": "fail"}, 400