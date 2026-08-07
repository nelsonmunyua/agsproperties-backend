from flask import request
from models import Property


def _absolute_url(path):
    """Convert a stored (possibly relative) media URL to an absolute URL."""
    if not path:
        return None
    if path.startswith(("http://", "https://", "//")):
        return path
    return f"{request.host_url.rstrip('/')}{path}"


class PropertySerializer:

    #Serializes Property objects for API responses.
    

    @staticmethod
    def image(image):
        return {
            "id": image.id,
            "url": _absolute_url(image.image_url),
            "caption": image.caption,
            "is_primary": image.is_primary,
        }

    @staticmethod
    def video(video):
        return {
            "id": video.id,
            "url": _absolute_url(video.video_url),
        }

    @staticmethod
    def property_type(property_type):
        if not property_type:
            return None

        return {
            "id": property_type.id,
            "name": property_type.name,
        }

    @staticmethod
    def agent(agent):

        if not agent:
            return None

        return {
            "id": agent.id,
            "license_number": agent.license_number,

            "user": {
                "id": agent.user.id,
                "first_name": agent.user.first_name,
                "last_name": agent.user.last_name,
                "phone": agent.user.phone,
                "email": agent.user.email,
            }
        }

    @staticmethod
    def location(property):
        location = property.location

        if not location:
            return None

        return {
            "country": location.country,
            "state": location.state,
            "city": location.city,
            "street": location.street,
            "neighborhood": location.neighborhood,
            "latitude": location.latitude,
            "longitude": location.longitude,
        }

    @staticmethod
    def summary(property: Property):

        location_data = None
        if property.property_location and property.property_location.location:
            loc = property.property_location.location
            location_data = {
                "country": loc.country,
                "state": loc.state,
                "city": loc.city,
                "street": loc.street,
                "neighborhood": loc.neighborhood,
                "latitude": loc.latitude,
                "longitude": loc.longitude,
            }

        return {

            "id": property.id,

            "title": property.title,

            "price": property.price,

            "currency": property.currency,

            "area_size": property.area_size,

            "description": property.description,

            "listing_type": property.listing_type,

            "status": property.status,

            "bedrooms": property.bedrooms,

            "bathrooms": property.bathrooms,

            "location": location_data,

            "created_at": property.created_at.isoformat() if property.created_at else None,

            "primary_image": _absolute_url(
                next(
                    (
                        image.image_url
                        for image in property.images
                        if image.is_primary
                    ),
                    next(
                        (
                            image.image_url
                            for image in property.images
                        ),
                        None,
                    ),
                )
            ),

            "property_type":
                PropertySerializer.property_type(
                    property.property_type
                ),

        }

    @staticmethod
    def detail(property: Property):

        return {

            "id": property.id,

            "title": property.title,

            "description": property.description,

            "price": property.price,

            "currency": property.currency,

            "listing_type": property.listing_type,

            "status": property.status,

            "bedrooms": property.bedrooms,

            "bathrooms": property.bathrooms,

            "area_size": property.area_size,

            "area_unit": property.area_unit,

            "listing_date": property.listing_date.isoformat() if property.listing_date else None,

            "created_at": property.created_at.isoformat() if property.created_at else None,

            "updated_at": property.updated_at.isoformat() if property.updated_at else None,


            "agent":
                PropertySerializer.agent(
                    property.agent
                ),

            "property_type":
                PropertySerializer.property_type(
                    property.property_type
                ),

            "images": [
                PropertySerializer.image(image)
                for image in property.images
            ],

            "videos": [
                PropertySerializer.video(video)
                for video in property.videos
            ],

            "location":
                PropertySerializer.location(
                    property
                ),
        }

    @staticmethod
    def collection(properties):

        return [
            PropertySerializer.summary(property)
            for property in properties
        ]