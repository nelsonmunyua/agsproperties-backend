import os

from werkzeug.utils import secure_filename

from models import Location, PropertyLocation, db


class PropertyLocationService:

    @staticmethod
    def attach_location(property, data):

        if not data:
            return None

        location = Location(
            country=data.get("country"),
            state=data.get("state"),
            city=data.get("city"),
            street=data.get("street"),
            neighborhood=data.get("neighborhood"),
            latitude=data.get("latitude"),
            longitude=data.get("longitude"),
        )

        db.session.add(location)
        db.session.flush()

        property_location = PropertyLocation(
            property_id=property.id,
            location_id=location.id,
        )

        db.session.add(property_location)

        return property_location