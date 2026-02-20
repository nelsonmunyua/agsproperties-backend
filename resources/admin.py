from flask import request
from flask_restful import Resource, reqparse
from models import db, User, Property, Payment, PropertyImage, PropertyLocation, Location, Property_type, AgentProfile, PropertyAmenity, Amenity
from utils import admin_required

from flask import request
from flask_restful import Resource, reqparse
from models import db, User, Property, Payment, PropertyImage, PropertyLocation, Location
from utils import admin_required


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
        agents = User.query.filter_by(role='agent', is_verified=False).all()

        return [
            {
                "id": a.id,
                "name": f"{a.first_name} {a.last_name}",
                "email": a.email,
                "phone": a.phone,
                "date": a.created_at.strftime("%b %d, %Y")
            }
            for a in agents
        ], 200
    
class AgentApproval(Resource):
    @admin_required()
    def patch(self, user_id):
        # Get the agent(user)
        agent = User.query.get(user_id)
        if not agent:
            return {"message":"Agent does not found"}, 404
        # Get new status from the frontend
        data = request.get_json()

        if 'is_verified' in data:
            agent.is_verified = data['is_verified']
            # commit changes to the db
            db.session.commit()
            return {"message":f"Agent verified status updated to {agent.is_verified} "}, 200
        return {"message": "No update data provided"}, 400


    
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

class PropertyResource(Resource):
    def get(self):
        properties = Property.query.all()

        result = []
        for property in properties:
            prop_dict = property.to_dict()
            # Get the primary image for this property
            primary_image = PropertyImage.query.filter_by(property_id = property.id, is_primary=True).first()

            # Add image URL to the property dict
            prop_dict['image'] = primary_image.image_url if primary_image else None

            # Add location
            prop_location = PropertyLocation.query.filter_by(property_id = property.id).first()
            if prop_location:
                location = Location.query.get(prop_location.location_id)
                if location:
                    prop_dict['location'] = location.neighborhood
                    prop_dict['city'] = location.city

            result.append(prop_dict)        

        return result, 200


