from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData
from sqlalchemy_serializer import SerializerMixin
from sqlalchemy.orm import validates
from datetime import datetime

naming_convention = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}

metadata = MetaData(naming_convention=naming_convention)

db = SQLAlchemy(metadata=metadata)


class User(db.Model, SerializerMixin):
    __tablename__ = "users"

    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.Text(), nullable=False)
    phone = db.Column(db.Text(), nullable=False, unique=True)
    email = db.Column(db.Text(), nullable=False, unique=True)
    # password_hash = db.Column(db.Text(), nullable=False)
    role = db.Column(db.Enum("admin", "agent", "user"), default="user", nullable=False)
    is_verified = db.Column(db.Boolean(), default=False, nullable=False)
    created_at = db.Column(db.DateTime(), server_default=db.func.now())
    updated_at = db.Column(db.DateTime(), onupdate=db.func.now(), default=datetime.now())

class Agent(db.Model, SerializerMixin):
    __tablename__ = "agents"

    id = db.Column(db.Integer(), primary_key=True)
    user_id = db.Column(db.Integer(), db.ForeignKey("users.id"), nullable=False)
    license_number = db.Column(db.Text(), nullable=False, unique=True)
    agency_id = db.Column(db.Integer(), db.ForeignKey("agencies.id"))
    bio = db.Column(db.Text(), nullable=True)
    rating = db.Column(db.Integer(), nullable=True)
    created_at = db.Column(db.DateTime(), server_default=db.func.now())
    updated_at = db.Column(db.DateTime(), onupdate=db.func.now(), default=datetime.now())

class Owner(db.Model, SerializerMixin):
    __tablename__ = 'owners'

    id = db.Column(db.Integer(), primary_key=True)
    user_id = db.Column(db.Integer(), db.ForeignKey("users.id"), nullable=False)
    created_at = db.Column(db.DateTime(), server_default=db.func.now())
    updated_at = db.Column(db.DateTime(), onupdate=db.func.now(), default=datetime.now())

class Property(db.Model, SerializerMixin):
    __tablename__ = "properties"

    id = db.Column(db.Integer(), primary_key=True)
    title = db.Column(db.Text(), nullable=False)
    description = db.Column(db.Text(), nullable=True)
    property_type_id = db.Column(db.Integer(), db.ForeignKey("property_types.id"), nullable=False)
    owner_id = db.Column(db.Integer(), db.ForeignKey("owners.id"), nullable=False)
    agent_id = db.Column(db.Integer(), db.ForeignKey("agents.id"), nullable=False)
    price = db.Column(db.Integer(), nullable=False)
    currency = db.Column(db.Text(), nullable=False)
    bedrooms = db.Column(db.Integer(), nullable=True)
    bathrooms = db.Column(db.Integer(), nullable=True)
    area_size = db.Column(db.Integer(), nullable=True)
    area_unit = db.Column(db.Text(), nullable=True)
    listing_type = db.Column(db.Text(), nullable=False)
    status = db.Column(db.Enum("onsale", "onrent", "lease"), nullable=False)
    year_built = db.Column(db.DateTime(), nullable=True)
    listing_date = db.Column(db.DateTime(), nullable=False)
    created_at = db.Column(db.DateTime(), server_default=db.func.now())
    updated_at = db.Column(db.DateTime(), onupdate=db.func.now(), default=datetime.now())

class Property_type(db.Model, SerializerMixin):
    __tablename__ = "property_types"

    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.Text())
    created_at = db.Column(db.DateTime(), server_default=db.func.now())
    updated_at = db.Column(db.DateTime(), onupdate=db.func.now(), default=datetime.now())

class Location(db.Model, SerializerMixin):
    __tablename__ = "locations"

    id = db.Column(db.Integer(), primary_key=True)
    country = db.Column(db.Text())
    state = db.Column(db.Text())
    city = db.Column(db.Text())
    neighborhood = db.Column(db.Text())
    latitude = db.Column(db.Text())
    longitude = db.Column(db.Text())
    created_at = db.Column(db.DateTime(), server_default=db.func.now())
    created_at = db.Column(db.DateTime(), onupdate=db.func.now(), default=datetime.now())

class PropertyLocation(db.Model, SerializerMixin):
    __tablename__ = "property_locations"

    id = db.Column(db.Integer(), primary_key=True)
    property_id = db.Column(db.Integer(), db.ForeignKey("properties.id"), nullable=False)
    location_id = db.Column(db.Integer(), db.ForeignKey("locations.id"), nullable=False)

class Agency(db.Model, SerializerMixin):
    __tablename__ = "agencies"   

    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.Text())
    address = db.Column(db.Text())
    phone = db.Column(db.Text())
    founded_year = db.Column(db.Text())
    created_at = db.Column(db.DateTime(), server_default=db.func.now())
    updated_at = db.Column(db.DateTime(), onupdate=db.func.now(), default=datetime.now())

class PropertyImage(db.Model,SerializerMixin):
    __tablename__ = "property_images" 

    id = db.Column(db.Integer(), primary_key=True)
    property_id = db.Column(db.Integer(), db.ForeignKey("properties.id"))
    image_url = db.Column(db.Text())
    caption = db.Column(db.Text())
    is_primary = db.Column(db.Boolean(), default=False, nullable=False)
    created_at = db.Column(db.DateTime(), server_default=db.func.now())
    updated_at = db.Column(db.DateTime(), onupdate=db.func.now(), default=datetime.now()) 

class PropertyVideo(db.Model, SerializerMixin):
    __tablename__ = "property_videos"

    id = db.Column(db.Integer(), primary_key=True)
    propert_id = db.Column(db.Integer(), db.ForeignKey("properties.id"), nullable=False)
    video_url = db.Column(db.Text())
    created_at = db.Column(db.DateTime(), server_default=db.func.now())
    updated_at = db.Column(db.DateTime(), onupdate=db.func.now(), default=datetime.now())

class Amenity(db.Model, SerializerMixin):
    __tablename__ = "amenities"

    id = db.Column(db.Integer(), primary_key=True)
    name =db.Column(db.Text())
    created_at = db.Column(db.DateTime(), server_default=db.func.now())
    updated_at = db.Column(db.DateTime(), onupdate=db.func.now(), default=datetime.now())

class PropertyAmenity(db.Model, SerializerMixin):
    __tablename__ = "property_amenities"

    id = db.Column(db.Integer(), primary_key=True)
    property_id = db.Column(db.Integer(), db.ForeignKey("properties.id"), nullable=False)
    amenity_id = db.Column(db.Integer(), db.ForeignKey("amenities.id"), nullable=False)

class View(db.Model, SerializerMixin):
    __tablename__ = "views"

    id = db.Column(db.Integer(), primary_key=True)
    property_id = db.Column(db.Integer(), db.ForeignKey("properties.id"), nullable=False)
    user_id = db.Column(db.Integer(), db.ForeignKey("users.id"), nullable=False)
    sheduled_time = db.Column(db.DateTime(), nullable=False)
    status = db.Column(db.Enum("completed", "canceled", "pending"))
    created_at = db.Column(db.DateTime(), server_default=db.func.now())
    updated_at = db.Column(db.DateTime(), onupdate=db.func.now(), default=datetime.now())

class Trasanction(db.Model, SerializerMixin):
    __tablename__ = "transactions"

    id = db.Column(db.Integer(), primary_key=True)
    property_id = db.Column(db.Integer(), db.ForeignKey("properties.id"), nullable=False)
    user_id = db.Column(db.Integer(), primary_key=db.ForeignKey("users.id"), nullable=False)
    sale_price = db.Column(db.Text())
    closing_date = db.Column(db.DateTime())   
    transaction_type = db.Column(db.Text())
    created_at = db.Column(db.DateTime(), server_default=db.func.now())
    updated_at = db.Column(db.DateTime(), onupdate=db.func.now(), default=datetime.now())

class Subscription(db.Model, SerializerMixin):
    __tablename__ = "subscriptions"

    id = db.Column(db.Integer(), primary_key=True)
    user_id = db.Column(db.Integer(), db.ForeignKey("users.id"), nullable=True)
    plan = db.Column(db.Text())
    expires_at = db.Column(db.DateTime())
    created_at = db.Column(db.DateTime(), server_default=db.func.now())
    updated_at = db.Column(db.DateTime(), onupdate=db.func.now(), default=datetime.now())

class Payment(db.Model, SerializerMixin):
    __tablename__ = "payments"

    id = db.Column(db.Integer(), primary_key=True) 
    user_id = db.Column(db.Integer(), db.ForeignKey("users.id"), nullable=False)
    amount = db.Column(db.Integer())
    payment_method = db.Column(db.Text()) 
    status = db.Column(db.Enum("pending", "complete"))
    created_at = db.Column(db.DateTime(), server_default=db.func.now())
    updated_at = db.Column(db.DateTime(), onupdate=db.func.now(), default=datetime.now())

class Favorite(db.Model, SerializerMixin):
    __tablename__ = "favorites"
    
    id = db.Column(db.Integer(), primary_key=True)
    user_id = db.Column(db.Integer(), db.ForeignKey("users.id"), nullable=False)
    property_id = db.Column(db.Integer(), db.ForeignKey("properties.id"), nullable=False)
    created_at = db.Column(db.DateTime(), server_default=db.func.now())
    updated_at = db.Column(db.DateTime(), onupdate=db.func.now(), default=datetime.now())



    
    

    












