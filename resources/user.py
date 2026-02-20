from flask import request
from models import db, User, Property, Favorite, UserProfile, Inquiry, View, PropertyImage, PropertyLocation, Location, Property_type, AgentProfile, PropertyVideo
from flask_restful import Resource, reqparse
from flask_jwt_extended import get_jwt_identity
from utils import user_required
from datetime import datetime

class UserPropertiesResource(Resource):
    def get(self):
        """Get all properties for user browsing with primary image and location"""
        properties = Property.query.all()

        result = []
        for prop in properties:
            prop_dict = prop.to_dict()
            
            # Get primary image
            primary_image = PropertyImage.query.filter_by(property_id=prop.id, is_primary=True).first()
            prop_dict['primary_image'] = primary_image.image_url if primary_image else None
            
            # Get location
            prop_location = PropertyLocation.query.filter_by(property_id=prop.id).first()
            if prop_location:
                location = Location.query.get(prop_location.location_id)
                if location:
                    prop_dict['location'] = location.neighborhood or location.city or f"{location.city}, {location.state}"
            
            # Get property type name for category filtering
            property_type = Property_type.query.get(prop.property_type_id)
            if property_type:
                prop_dict['property_type'] = property_type.name
            
            result.append(prop_dict)

        return result, 200


class UserPropertyDetailResource(Resource):
    def get(self, property_id):
        """Get single property with full details including agent info"""
        prop = Property.query.get(property_id)
        
        if not prop:
            return {"message": "Property not found"}, 404
        
        prop_dict = prop.to_dict()
        
        # Get primary image
        primary_image = PropertyImage.query.filter_by(property_id=prop.id, is_primary=True).first()
        prop_dict['primary_image'] = primary_image.image_url if primary_image else None
        
        # Get all images
        all_images = PropertyImage.query.filter_by(property_id=prop.id).all()
        prop_dict['images'] = [img.image_url for img in all_images]
        
        # Get all videos
        all_videos = PropertyVideo.query.filter_by(propert_id=prop.id).all()
        prop_dict['videos'] = [video.video_url for video in all_videos]
        
        # Get location details
        prop_location = PropertyLocation.query.filter_by(property_id=prop.id).first()
        if prop_location:
            location = Location.query.get(prop_location.location_id)
            if location:
                prop_dict['location'] = {
                    'neighborhood': location.neighborhood,
                    'city': location.city,
                    'state': location.state,
                    'country': location.country,
                    'latitude': location.latitude,
                    'longitude': location.longitude
                }
        
        # Get property type
        property_type = Property_type.query.get(prop.property_type_id)
        if property_type:
            prop_dict['property_type'] = property_type.name
        
        # Get agent info
        agent_profile = AgentProfile.query.get(prop.agent_id)
        if agent_profile:
            agent_user = User.query.get(agent_profile.agent_id)
            if agent_user:
                prop_dict['agent'] = {
                    'id': agent_user.id,
                    'name': f"{agent_user.first_name} {agent_user.last_name}",
                    'email': agent_user.email,
                    'phone': agent_user.phone,
                    'bio': agent_profile.bio,
                    'rating': agent_profile.rating,
                    'license_number': agent_profile.license_number
                }
        
        return prop_dict, 200

class UserStatsResource(Resource):
    @user_required()
    def get(self):
        # Get the current user's ID from JWT
        current_user_id = get_jwt_identity()
        
        # Get the user's profile to find favorites
        user_profile = UserProfile.query.filter_by(user_id=current_user_id).first()
        
        # Count saved properties (favorites)
        saved_count = 0
        if user_profile:
            saved_count = Favorite.query.filter_by(user_id=user_profile.id).count()
        
        # Count inquiries sent by this user
        inquiries_count = Inquiry.query.filter_by(user_id=current_user_id).count()
        
        # Count scheduled visits (views)
        visits_count = View.query.filter_by(user_id=current_user_id).count()
        
        return {
            "saved": saved_count,
            "inquiries": inquiries_count,
            "visits": visits_count
        }, 200

class SavedPropertiesResource(Resource):
    @user_required()
    def get(self):
        current_user_id = get_jwt_identity()

        # Get user's profile
        user_profile = UserProfile.query.filter_by(user_id=current_user_id).first()

        if not user_profile:
            return {"properties": []}, 200

        #Get all favorite for this user
        favorites = Favorite.query.filter_by(user_id=user_profile.id).all()

        properties = []
        for fav in favorites:
            property = Property.query.get(fav.property_id)  
            if property:
                properties.append(property.to_dict())

        return {"properties": properties}, 200   


class ToggleFavoriteResource(Resource):
    @user_required()
    def post(self):
        """Toggle favorite status for a property"""
        current_user_id = get_jwt_identity()
        
        # Get user's profile
        user_profile = UserProfile.query.filter_by(user_id=current_user_id).first()
        
        if not user_profile:
            return {"message": "User profile not found"}, 404
        
        # Get property_id from request
        data = request.get_json()
        property_id = data.get('property_id')
        
        if not property_id:
            return {"message": "Property ID is required"}, 400
        
        # Check if property exists
        property = Property.query.get(property_id)
        if not property:
            return {"message": "Property not found"}, 404
        
        # Check if already favorited
        existing_favorite = Favorite.query.filter_by(
            user_id=user_profile.id,
            property_id=property_id
        ).first()
        
        if existing_favorite:
            # Remove from favorites
            db.session.delete(existing_favorite)
            db.session.commit()
            return {"message": "Removed from favorites", "is_favorited": False}, 200
        else:
            # Add to favorites
            new_favorite = Favorite(
                user_id=user_profile.id,
                property_id=property_id
            )
            db.session.add(new_favorite)
            db.session.commit()
            return {"message": "Added to favorites", "is_favorited": True}, 200

# Get recent activities

class RecentActivitiesResource(Resource):
    @user_required()
    def get(self):
        current_user = get_jwt_identity()

        #Get user profile
        user_profile = UserProfile.query.filter_by(user_id=current_user).first()
        if not user_profile:
            return {"activities": []}, 200
        
        activities = []
      
       # Get recent property views
        views = View.query.filter_by(user_id=current_user).order_by(View.created_at.desc()).limit(5).all()
        for view in views:
            property = Property.query.get(View.property_id)
            activities.append({
                "type": "view",
                "description": f"Viewed {property.title if property else 'a property'}",
                "property": property.title if property else None,
                "time": view.created_at.strftime("%Y-%m-%d %H:%M")
            })    


        # Get recent inquiries
        inquiries = Inquiry.query.filter_by(user_id=current_user).order_by(Inquiry.created_at.desc()).limit(5).all()
        for inquiry in inquiries:
            property = Property.query.get(Inquiry.property_id)
            activities.append({
                "type": "inquiry",
                "description": inquiry.message[:50] + "..." if len(inquiry.message) > 50 else inquiry.message,
                "property": property.title if property else None,
                "time": inquiry.created_at.strftime("%Y-%m-%d %H:%M")
            })             
        #Get scheduled viewings (pending visits)
        scheduled = View.query.filter_by(user_id = current_user, status="pending").order_by(View.sheduled_time.desc()).limit(5).all()
        for view in scheduled:
            property = Property.query.get(view.property_id)
            activities.append({
                "type": "scheduled",
                "description": f"Scheduled viewing for {view.sheduled_time.strftime('%Y-%m-%d %H:%M')}",
                "property": property.title if property else None,
                "time": view.created_at.strftime("%Y-%m-%d %H:%M")
            })

            # Sort by time (most recent first)
            activities.sort(Key=lambda x: x["time"], reverse=True)
            # Return only the 10 most recent 
            return {"activities": activities[:10]},
            

