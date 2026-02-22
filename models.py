from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData
from sqlalchemy_serializer import SerializerMixin
from sqlalchemy.orm import validates
from datetime import datetime
from flask_bcrypt import check_password_hash

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
    first_name = db.Column(db.Text(), nullable=False)
    last_name = db.Column(db.Text(), nullable=False)
    phone = db.Column(db.Text(), nullable=False, unique=True)
    email = db.Column(db.Text(), nullable=False, unique=True)
    password = db.Column(db.Text(), nullable=False)
    role = db.Column(db.Enum("admin", "agent", "user", name="user_type"), default="user", nullable=False)
    is_verified = db.Column(db.Boolean(), default=False, nullable=False)
    created_at = db.Column(db.DateTime(), server_default=db.func.now())
    updated_at = db.Column(db.DateTime(), onupdate=db.func.now(), default=datetime.now())

    def check_password(self, plain_password):
        return check_password_hash(self.password, plain_password)
    
    def to_json(self):
        return {'id':self.id, 'role':self.role}
    
class AdminProfile(db.Model, SerializerMixin):
    __tablename__ = "admin_profiles"  

    id = db.Column(db.Integer(), primary_key=True)
    user_id = db.Column(db.Integer(), db.ForeignKey("users.id"), nullable=False)
    profile_picture = db.Column(db.String())
    is_active = db.Column(db.Boolean(), default=False, nullable=False)
    last_login = db.Column(db.DateTime(), server_default=db.func.now())
    login_ip = db.Column(db.Text())
    permission = db.Column(db.Text())
    created_at = db.Column(db.DateTime(), server_default=db.func.now())
    updated_at = db.Column(db.DateTime(), onupdate=db.func.now(), default=datetime.now())


class AgentProfile(db.Model, SerializerMixin):
    __tablename__ = "agent_profiles"

    id = db.Column(db.Integer(), primary_key=True)
    user_id = db.Column(db.Integer(), db.ForeignKey("users.id"), nullable=False)
    license_number = db.Column(db.Text(), nullable=False, unique=True)
    agency_id = db.Column(db.Integer(), db.ForeignKey("agencies.id"))
    bio = db.Column(db.Text(), nullable=True)
    rating = db.Column(db.Integer(), nullable=True)
    created_at = db.Column(db.DateTime(), server_default=db.func.now())
    updated_at = db.Column(db.DateTime(), onupdate=db.func.now(), default=datetime.now())

class UserProfile(db.Model, SerializerMixin):
    __tablename__ = 'user_profiles'

    id = db.Column(db.Integer(), primary_key=True)
    user_id = db.Column(db.Integer(), db.ForeignKey("users.id"), nullable=False)
    profile_picture = db.Column(db.String())
    created_at = db.Column(db.DateTime(), server_default=db.func.now())
    updated_at = db.Column(db.DateTime(), onupdate=db.func.now(), default=datetime.now())

class Property(db.Model, SerializerMixin):
    __tablename__ = "properties"

    id = db.Column(db.Integer(), primary_key=True)
    title = db.Column(db.Text(), nullable=False)
    description = db.Column(db.Text(), nullable=True)
    property_type_id = db.Column(db.Integer(), db.ForeignKey("property_types.id"), nullable=False)
    agent_id = db.Column(db.Integer(), db.ForeignKey("agent_profiles.id"), nullable=False)
    price = db.Column(db.Integer(), nullable=False)
    currency = db.Column(db.Text(), nullable=False)
    bedrooms = db.Column(db.Integer(), nullable=True)
    bathrooms = db.Column(db.Integer(), nullable=True)
    area_size = db.Column(db.Integer(), nullable=True)
    area_unit = db.Column(db.Text(), nullable=True)
    listing_type = db.Column(db.Text(), nullable=False)
    status = db.Column(db.Enum("onsale", "onrent", "lease", name="property_status"), nullable=False)
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
    name = db.Column(db.Text())
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
    status = db.Column(db.Enum("completed", "canceled", "pending", "viewed", name="view_status"))
    created_at = db.Column(db.DateTime(), server_default=db.func.now())
    updated_at = db.Column(db.DateTime(), onupdate=db.func.now(), default=datetime.now())

class Transaction(db.Model, SerializerMixin):
    __tablename__ = "transactions"

    id = db.Column(db.Integer(), primary_key=True)
    property_id = db.Column(db.Integer(), db.ForeignKey("properties.id"), nullable=False)
    user_id = db.Column(db.Integer(), db.ForeignKey("users.id"), nullable=False)
    sale_price = db.Column(db.Text())
    closing_date = db.Column(db.DateTime())   
    transaction_type = db.Column(db.Text())
    created_at = db.Column(db.DateTime(), server_default=db.func.now())
    updated_at = db.Column(db.DateTime(), onupdate=db.func.now(), default=datetime.now())

class Subscription(db.Model, SerializerMixin):
    __tablename__ = "subscriptions"

    id = db.Column(db.Integer(), primary_key=True)
    agent_id = db.Column(db.Integer(), db.ForeignKey("agent_profiles.id"), nullable=True)
    plan = db.Column(db.Text())
    expires_at = db.Column(db.DateTime())
    created_at = db.Column(db.DateTime(), server_default=db.func.now())
    updated_at = db.Column(db.DateTime(), onupdate=db.func.now(), default=datetime.now())

class Payment(db.Model, SerializerMixin):
    __tablename__ = "payments"

    id = db.Column(db.Integer(), primary_key=True) 
    agent_id = db.Column(db.Integer(), db.ForeignKey("agent_profiles.id"), nullable=False)
    amount = db.Column(db.Integer())
    payment_method = db.Column(db.Text()) 
    status = db.Column(db.Enum("pending", "complete", name="payment_status"))
    created_at = db.Column(db.DateTime(), server_default=db.func.now())
    updated_at = db.Column(db.DateTime(), onupdate=db.func.now(), default=datetime.now())

class Favorite(db.Model, SerializerMixin):
    __tablename__ = "favorites"
    
    id = db.Column(db.Integer(), primary_key=True)
    user_id = db.Column(db.Integer(), db.ForeignKey("user_profiles.id"), nullable=False)
    property_id = db.Column(db.Integer(), db.ForeignKey("properties.id"), nullable=False)
    created_at = db.Column(db.DateTime(), server_default=db.func.now())
    updated_at = db.Column(db.DateTime(), onupdate=db.func.now(), default=datetime.now())


class Inquiry(db.Model, SerializerMixin):
    """Model for user inquiries about properties"""
    __tablename__ = "inquiries"

    id = db.Column(db.Integer(), primary_key=True)
    user_id = db.Column(db.Integer(), db.ForeignKey("users.id"), nullable=False)
    agent_id = db.Column(db.Integer(), db.ForeignKey("agent_profiles.id"), nullable=False)
    property_id = db.Column(db.Integer(), db.ForeignKey("properties.id"), nullable=False)
    message = db.Column(db.Text(), nullable=False)
    status = db.Column(db.Enum("new", "replied", "closed", name="inquiry_status"), default="new", nullable=False)
    reply = db.Column(db.Text(), nullable=True)
    created_at = db.Column(db.DateTime(), server_default=db.func.now())
    updated_at = db.Column(db.DateTime(), onupdate=db.func.now(), default=datetime.now())


class Conversation(db.Model, SerializerMixin):
    """Model for real-time messaging conversations"""
    __tablename__ = "conversations"

    id = db.Column(db.Integer(), primary_key=True)
    user_id = db.Column(db.Integer(), db.ForeignKey("users.id"), nullable=False)
    agent_id = db.Column(db.Integer(), db.ForeignKey("agent_profiles.id"), nullable=False)
    property_id = db.Column(db.Integer(), db.ForeignKey("properties.id"), nullable=True)
    last_message = db.Column(db.Text(), nullable=True)
    last_message_at = db.Column(db.DateTime(), server_default=db.func.now())
    created_at = db.Column(db.DateTime(), server_default=db.func.now())
    updated_at = db.Column(db.DateTime(), onupdate=db.func.now(), default=datetime.now())


class Message(db.Model, SerializerMixin):
    """Model for individual messages in a conversation"""
    __tablename__ = "messages"

    id = db.Column(db.Integer(), primary_key=True)
    conversation_id = db.Column(db.Integer(), db.ForeignKey("conversations.id"), nullable=False)
    sender_id = db.Column(db.Integer(), db.ForeignKey("users.id"), nullable=False)
    sender_type = db.Column(db.Enum("user", "agent", name="sender_type"), nullable=False)
    content = db.Column(db.Text(), nullable=False)
    is_read = db.Column(db.Boolean(), default=False, nullable=False)
    created_at = db.Column(db.DateTime(), server_default=db.func.now())


class Review(db.Model, SerializerMixin):
    """Model for user reviews/ratings of agents"""
    __tablename__ = "reviews"

    id = db.Column(db.Integer(), primary_key=True)
    user_id = db.Column(db.Integer(), db.ForeignKey("users.id"), nullable=False)
    agent_id = db.Column(db.Integer(), db.ForeignKey("agent_profiles.id"), nullable=False)
    property_id = db.Column(db.Integer(), db.ForeignKey("properties.id"), nullable=True)
    rating = db.Column(db.Integer(), nullable=False)  # 1-5 stars
    comment = db.Column(db.Text(), nullable=True)
    created_at = db.Column(db.DateTime(), server_default=db.func.now())
    updated_at = db.Column(db.DateTime(), onupdate=db.func.now(), default=datetime.now())


class Notification(db.Model, SerializerMixin):
    """Model for user notifications"""
    __tablename__ = "notifications"

    id = db.Column(db.Integer(), primary_key=True)
    user_id = db.Column(db.Integer(), db.ForeignKey("users.id"), nullable=False)
    title = db.Column(db.Text(), nullable=False)
    message = db.Column(db.Text(), nullable=False)
    notification_type = db.Column(db.Enum("inquiry", "viewing", "property", "system", name="notification_type"), default="system")
    is_read = db.Column(db.Boolean(), default=False, nullable=False)
    created_at = db.Column(db.DateTime(), server_default=db.func.now())
    updated_at = db.Column(db.DateTime(), onupdate=db.func.now(), default=datetime.now())



    
    

    












