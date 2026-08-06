from datetime import datetime
from modules.user.service import UserService
from modules.property.image_service import PropertyImageService
from modules.property.video_service import PropertyVideoService
from modules.property.location_service import PropertyLocationService
from models import (Property, User)
from modules.property.repository import PropertyRepository
from modules.property.policy import PropertyPolicy
from modules.property.exceptions import ( PropertyNotFound )
from shared.exceptions import ValidationException
from modules.property.serializer import PropertySerializer
from modules.user.service import UserService
from models import db

class PropertyService:
    # Handles all property bussiness logic
    @staticmethod
    def create_property(actor, data, images=None, videos=None, location=None):
        PropertyPolicy.authorize_create(actor)

        agent = UserService.resolve_property_owner( actor, data )

        property_data = data.copy()

        property_data["agent_id"] = agent.id
        property_data["listing_date"] = datetime.utcnow()

        property = Property(**property_data)    

        PropertyRepository.save(property)

        PropertyImageService.create_images( property, images,)

        PropertyVideoService.create_videos( property, videos,)

        PropertyLocationService.attach_location(property, location,)

        db.session.commit()


        return property

    @staticmethod
    def list_properties(filters=None):

       return PropertyRepository.list_properties(filters)
       
    @staticmethod
    def get_property(property_id):

        return PropertyRepository.get_property(property_id) 

    @staticmethod
    def get_saved_properties(user, limit=None):
        
        return PropertyRepository.saved_properties(user, limit=limit)

    @staticmethod
    def toggle_favorite(user, property_id):

        favorite = PropertyRepository.get_favorite_property_id(user, property_id)

        if favorite:
            PropertyRepository.delete(favorite)
            db.session.commit()
            return False  # Property was unfavorited
            
        else:
            favorite = PropertyRepository.set_favorite_property(user, property_id)

            PropertyRepository.save_favorite(favorite)

            db.session.commit()
            return True  # Property was favorited



        
            





      




