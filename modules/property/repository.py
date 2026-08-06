# module/property/repository

from sqlalchemy.orm import joinedload, selectinload
from flask_sqlalchemy.record_queries import get_recorded_queries
from sqlalchemy.orm import Session
from models import db
from models import (Property, AgentProfile, PropertyLocation, Favorite, UserProfile)

class PropertyRepository:

    @staticmethod
    def get_public_properties():

        return (
            Property.query.order_by(Property.created_at.desc()).all()
        )

    # Handles all database interaction for properties.
    
    @staticmethod
    def save(property):
        db.session.add(property)
        return property

    @staticmethod
    def delete(property):
        db.session.delete(property)

    @staticmethod
    def get_property(property_id):

        return (
            Property.query.options(
                joinedload(Property.agent)
                .joinedload(AgentProfile.user),

                joinedload(Property.property_type),

                selectinload(Property.images),

                selectinload(Property.videos),

                joinedload(Property.property_location)
                .joinedload(PropertyLocation.location)
            )
            .filter(Property.id == property_id).first()
        )

    @staticmethod
    def get_agent_properties(agent_id):

        return (
            Property.query.filter(
                Property.agent_id == agent_id
            )
            .options(
                joinedload(Property.property_type),
                selectinload(Property.images),
            )
            .order_by(Property.created_at.desc())
            .all()
        )

    @staticmethod
    def list_properties(filters=None):

        query = Property.query.options(

            joinedload(Property.agent)
            .joinedload(AgentProfile.user),

            joinedload(Property.property_type),

            selectinload(Property.images),

            selectinload(Property.videos),
        )

        if not filters:
            return (
                query.order_by(
                    Property.created_at.desc()
                )
                .all()
            )

        if filters.get("search"):
            query = query.filter(
                Property.title.ilike(
                    f"%{filters['search']}%"
                )
            )

        if filters.get("listing_type"):
            query = query.filter(
                Property.listing_type == filters["listing_type"]
            )

        if filters.get("status"):
            query = query.filter(
                Property.status == filters["status"]
            )

        if filters.get("property_type"):
            query = query.filter(
                Property.property_type_id
                == filters["property_type"]
            )

        if filters.get("bedrooms") is not None:
            query = query.filter(
                Property.bedrooms >= filters["bedrooms"]
            )

        if filters.get("bathrooms") is not None:
            query = query.filter(
                Property.bathrooms >= filters["bathrooms"]
            )

        if filters.get("min_price") is not None:
            query = query.filter(
                Property.price >= filters["min_price"]
            )

        if filters.get("max_price") is not None:
            query = query.filter(
                Property.price <= filters["max_price"]
            )

        return (
            query.order_by(
                Property.created_at.desc()
            )
            .all()
        )

    @staticmethod
    def exists(property_id):

        return (
            db.session.query(Property.id)
            .filter(Property.id == property_id)
            .first()
            is not None
        )
    # this method get's all the saved properties
    @staticmethod
    def saved_properties(user, limit=None):
        # Get user_profile.id
        profile = user.user_profile

        query = Favorite.query.filter_by(user_id = profile.id).options(
            joinedload(Favorite.property)
        )

        if limit and limit > 0:
            query = query.limit(limit)


        favorites = query.all()

        return [favorite.property for favorite in favorites]
    
    # This method is used to toggle a property to favorite it. 
    @staticmethod
    def get_favorite_property_id(user, property_id):
        # get user_profile.id
        profile = user.user_profile

        favorite = Favorite.query.filter_by(user_id=profile.id, property_id=property_id).first()

        return favorite

    @staticmethod
    def set_favorite_property(user, property_id):  
        profile = user.user_profile

        favorite = Favorite(user_id = profile.id, property_id=property_id)

        return favorite  

    @staticmethod
    def save_favorite(favorite):

        db.session.add(favorite)

        return favorite  

    @staticmethod
    def delete(favorite):

        db.session.delete(favorite)  




  