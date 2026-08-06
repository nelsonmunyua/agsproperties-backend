from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData
from sqlalchemy_serializer import SerializerMixin
from sqlalchemy.orm import validates
from datetime import datetime
from flask_bcrypt import check_password_hash
from auth.roles import ROLE_PERMISSIONS

naming_convention = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}

metadata = MetaData(naming_convention=naming_convention)

db = SQLAlchemy(metadata=metadata)


class User(db.Model):
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
    updated_at = db.Column(db.DateTime(), server_default=db.func.now(), onupdate=db.func.now())

    # relationships
    admin_profile = db.relationship("AdminProfile", uselist=False, back_populates="user", cascade="all, delete-orphan")    
    agent_profile = db.relationship("AgentProfile", uselist=False, back_populates="user", cascade="all, delete-orphan")
    user_profile = db.relationship("UserProfile", uselist=False, back_populates="user", lazy="joined", cascade="all, delete-orphan")
     
     # computed properties
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    @property
    def profile(self):
        # return the profile that belongs to the user
        if self.role == "admin":
            return self.admin_profile
        if self.role == "agent":
            return self.agent_profile
        return self.user_profile

    @property
    def is_agent(self):
        return self.role == "agent"

    @property
    def is_admin(self):
        return self.role == "admin"

    @property
    def is_user(self):
        return self.role == "user"   

     # set permissions
    @property
    def permissions(self):
        return ROLE_PERMISSIONS.get(self.role, set())
    def has_permission(self, permission: str) -> bool:
        return permission in self.permissions                             



    def check_password(self, plain_password):
        """Verify password - handles both bcrypt hashes and plain text (legacy)"""
        if not self.password or not plain_password:
            return False
            
        # Ensure both are strings for comparison
        stored_password = self.password
        if isinstance(stored_password, bytes):
            stored_password = stored_password.decode('utf-8')
        
        try:
            # First try bcrypt hash
            return check_password_hash(stored_password, plain_password)
        except (ValueError, TypeError):
            # If bcrypt fails (invalid salt), try plain text comparison
            # This handles legacy data or improperly hashed passwords
            return stored_password == plain_password
        except Exception:
            # Catch any other unexpected errors
            return False
    

    
class AdminProfile(db.Model):
    __tablename__ = "admin_profiles"  

    id = db.Column(db.Integer(), primary_key=True)
    user_id = db.Column(db.Integer(), db.ForeignKey("users.id"), nullable=False)
    profile_picture = db.Column(db.String())
    is_active = db.Column(db.Boolean(), default=False, nullable=False)
    last_login = db.Column(db.DateTime(), server_default=db.func.now())
    login_ip = db.Column(db.Text())
    permission = db.Column(db.Text())
    created_at = db.Column(db.DateTime(), server_default=db.func.now())
    updated_at = db.Column(db.DateTime(), server_default=db.func.now(), onupdate=db.func.now())

    # relationships
    user = db.relationship("User", back_populates="admin_profile")




class AgentProfile(db.Model):
    __tablename__ = "agent_profiles"

    id = db.Column(db.Integer(), primary_key=True)
    user_id = db.Column(db.Integer(), db.ForeignKey("users.id"), nullable=False)
    license_number = db.Column(db.Text(), nullable=False, unique=True)
    agency_id = db.Column(db.Integer(), db.ForeignKey("agencies.id"))
    bio = db.Column(db.Text(), nullable=True)
    rating = db.Column(db.Integer(), nullable=True)
    created_at = db.Column(db.DateTime(), server_default=db.func.now())
    updated_at = db.Column(db.DateTime(), server_default=db.func.now(), onupdate=db.func.now())

    # relationship
    user = db.relationship("User", back_populates="agent_profile")
    agency = db.relationship("Agency", back_populates="agent_profiles")
    properties = db.relationship("Property", back_populates="agent", lazy="selectin")


class UserProfile(db.Model):
    __tablename__ = 'user_profiles'

    id = db.Column(db.Integer(), primary_key=True)
    user_id = db.Column(db.Integer(), db.ForeignKey("users.id"), nullable=False)
    profile_picture = db.Column(db.String())
    created_at = db.Column(db.DateTime(), server_default=db.func.now())
    updated_at = db.Column(db.DateTime(), server_default=db.func.now(), onupdate=db.func.now())

    # relationships
    user = db.relationship("User", back_populates="user_profile")
    favorites = db.relationship( "Favorite", back_populates="user_profile", cascade="all, delete-orphan")

class Property(db.Model):
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
    updated_at = db.Column(db.DateTime(), server_default=db.func.now(), onupdate=db.func.now())

    # relationships
    agent = db.relationship("AgentProfile", back_populates="properties", lazy="joined")
    property_type = db.relationship("PropertyType", back_populates="properties", lazy="joined")
    images = db.relationship("PropertyImage", back_populates="property", lazy="selectin", cascade="all, delete-orphan",)
    videos = db.relationship("PropertyVideo", back_populates="property", lazy="selectin", cascade="all, delete-orphan")
    property_location = db.relationship("PropertyLocation", back_populates="property", uselist=False, cascade="all, delete-orphan", lazy="joined")
    favorites = db.relationship("Favorite", back_populates="property", lazy="joined")


    @classmethod
    def create(cls, agent, data):

        return cls(

            title=data["title"],

            description=data.get("description"),

            property_type_id=data["property_type_id"],

            agent_id=agent.id,

            price=data["price"],

            currency=data["currency"],

            bedrooms=data.get("bedrooms"),

            bathrooms=data.get("bathrooms"),

            area_size=data.get("area_size"),

            area_unit=data.get("area_unit"),

            listing_type=data["listing_type"],

            status=data["status"],

            listing_date=datetime.utcnow(),

        )
    # computed properties
    @property
    def location(self):
        if self.property_location:
            return self.property_location.location
        return None

    @property
    def full_address(self):

        if not self.location_link:
            return None

        location = self.location_link.location

        return ", ".join(
            filter(
                None,
                [
                    location.street,
                    location.city,
                    location.state,
                    location.country
                ]
            )
        )  

    @property
    def primary_image(self):

        return next(
            (
                image
                for image in self.images
                if image.is_primary
            ),
            None
        )    

    @property
    def cover_image(self):

        image = self.primary_image

        if image:
            return image.image_url

        return None

    @property
    def formatted_price(self):
        return f"{self.currency} {self.price:,.0f}" 

    @property
    def formatted_area(self):

        if not self.area_size:
            return None

        return f"{self.area_size} {self.area_unit}"

    @property
    def agent_name(self):

        if not self.agent:
            return None

        return self.agent.user.full_name   

    @property
    def is_sale(self):
        return self.status == "onsale"   

    @property
    def is_rental(self):
        return self.status == "onrent"                          

class PropertyType(db.Model):
    __tablename__ = "property_types"

    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.Text())
    created_at = db.Column(db.DateTime(), server_default=db.func.now())
    updated_at = db.Column(db.DateTime(), server_default=db.func.now(), onupdate=db.func.now())

    # relationship
    properties = db.relationship("Property", back_populates="property_type")

class Location(db.Model):
    __tablename__ = "locations"

    id = db.Column(db.Integer(), primary_key=True)
    country = db.Column(db.String(120))
    state = db.Column(db.Text())
    city = db.Column(db.Text())
    street = db.Column(db.Text())
    neighborhood = db.Column(db.String(120))
    latitude = db.Column(db.Float())
    longitude = db.Column(db.Float())
    created_at = db.Column(db.DateTime(), server_default=db.func.now())
    updated_at = db.Column(db.DateTime(), server_default=db.func.now(), onupdate=db.func.now())

    # relationships
    property_locations = db.relationship("PropertyLocation", back_populates="location",
        cascade="all, delete-orphan")


class PropertyLocation(db.Model):
    __tablename__ = "property_locations"

    id = db.Column(db.Integer(), primary_key=True)
    property_id = db.Column(db.Integer(), db.ForeignKey("properties.id"), nullable=False, unique=True)
    location_id = db.Column(db.Integer(), db.ForeignKey("locations.id"), nullable=False)
    created_at = db.Column(db.DateTime(), server_default=db.func.now())

    # relationships
    property = db.relationship("Property", back_populates="property_location")

    location = db.relationship(
        "Location",
        back_populates="property_locations",
        lazy="joined"
    )


class Agency(db.Model):
    __tablename__ = "agencies"   

    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.Text())
    address = db.Column(db.Text())
    phone = db.Column(db.Text())
    founded_year = db.Column(db.Text())
    created_at = db.Column(db.DateTime(), server_default=db.func.now())
    updated_at = db.Column(db.DateTime(), server_default=db.func.now(), onupdate=db.func.now())

    # relationshhips
    agent_profiles = db.relationship("AgentProfile", back_populates="agency")

class PropertyImage(db.Model):
    __tablename__ = "property_images" 

    id = db.Column(db.Integer(), primary_key=True)
    property_id = db.Column(db.Integer(), db.ForeignKey("properties.id"))
    image_url = db.Column(db.Text())
    caption = db.Column(db.Text())
    is_primary = db.Column(db.Boolean(), default=False, nullable=False)
    created_at = db.Column(db.DateTime(), server_default=db.func.now())
    updated_at = db.Column(db.DateTime(), server_default=db.func.now(), onupdate=db.func.now())

    # relationship
    property = db.relationship("Property", back_populates="images")


class PropertyVideo(db.Model):
    __tablename__ = "property_videos"

    # NOTE: The actual DB column is `property_id` (FK to properties.id).
    # The legacy `propert_id` typo existed in some query references — those
    # have been corrected to use `property_id` consistently.
    id = db.Column(db.Integer(), primary_key=True)
    property_id = db.Column(db.Integer(), db.ForeignKey("properties.id"), nullable=False)
    video_url = db.Column(db.Text())
    created_at = db.Column(db.DateTime(), server_default=db.func.now())
    updated_at = db.Column(db.DateTime(), server_default=db.func.now(), onupdate=db.func.now())

    # relationships
    property = db.relationship("Property", back_populates="videos")

class Amenity(db.Model):
    __tablename__ = "amenities"

    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.Text())
    created_at = db.Column(db.DateTime(), server_default=db.func.now())
    updated_at = db.Column(db.DateTime(), server_default=db.func.now(), onupdate=db.func.now())

class PropertyAmenity(db.Model):
    __tablename__ = "property_amenities"

    id = db.Column(db.Integer(), primary_key=True)
    property_id = db.Column(db.Integer(), db.ForeignKey("properties.id"), nullable=False)
    amenity_id = db.Column(db.Integer(), db.ForeignKey("amenities.id"), nullable=False)

class View(db.Model):
    __tablename__ = "views"

    id = db.Column(db.Integer(), primary_key=True)
    property_id = db.Column(db.Integer(), db.ForeignKey("properties.id"), nullable=False)
    user_id = db.Column(db.Integer(), db.ForeignKey("users.id"), nullable=False)
    sheduled_time = db.Column(db.DateTime(), nullable=False)
    status = db.Column(db.Enum("completed", "canceled", "pending", "viewed", name="view_status"))
    created_at = db.Column(db.DateTime(), server_default=db.func.now())
    updated_at = db.Column(db.DateTime(), server_default=db.func.now(), onupdate=db.func.now())

class Transaction(db.Model):
    __tablename__ = "transactions"

    id = db.Column(db.Integer(), primary_key=True)
    property_id = db.Column(db.Integer(), db.ForeignKey("properties.id"), nullable=False)
    user_id = db.Column(db.Integer(), db.ForeignKey("users.id"), nullable=False)
    sale_price = db.Column(db.Text())
    closing_date = db.Column(db.DateTime())   
    transaction_type = db.Column(db.Text())
    created_at = db.Column(db.DateTime(), server_default=db.func.now())
    updated_at = db.Column(db.DateTime(), server_default=db.func.now(), onupdate=db.func.now())

class Subscription(db.Model):
    __tablename__ = "subscriptions"

    id = db.Column(db.Integer(), primary_key=True)
    agent_id = db.Column(db.Integer(), db.ForeignKey("agent_profiles.id"), nullable=True)
    plan = db.Column(db.Text())
    expires_at = db.Column(db.DateTime())
    created_at = db.Column(db.DateTime(), server_default=db.func.now())
    updated_at = db.Column(db.DateTime(), server_default=db.func.now(), onupdate=db.func.now())

class Payment(db.Model):
    __tablename__ = "payments"

    id = db.Column(db.Integer(), primary_key=True) 
    agent_id = db.Column(db.Integer(), db.ForeignKey("agent_profiles.id"), nullable=False)
    amount = db.Column(db.Integer())
    payment_method = db.Column(db.Text()) 
    status = db.Column(db.Enum("pending", "complete", name="payment_status"))
    created_at = db.Column(db.DateTime(), server_default=db.func.now())
    updated_at = db.Column(db.DateTime(), server_default=db.func.now(), onupdate=db.func.now())

class Favorite(db.Model):
    __tablename__ = "favorites"
    
    id = db.Column(db.Integer(), primary_key=True)
    user_id = db.Column(db.Integer(), db.ForeignKey("user_profiles.id"), nullable=False)
    property_id = db.Column(db.Integer(), db.ForeignKey("properties.id"), nullable=False)
    created_at = db.Column(db.DateTime(), server_default=db.func.now())
    updated_at = db.Column(db.DateTime(), server_default=db.func.now(), onupdate=db.func.now())

    # relationship
    property = db.relationship("Property", back_populates="favorites", lazy="joined")
    user_profile = db.relationship( "UserProfile", back_populates="favorites")


class Inquiry(db.Model):
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
    updated_at = db.Column(db.DateTime(), server_default=db.func.now(), onupdate=db.func.now())

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "agent_id": self.agent_id,
            "property_id": self.property_id,
            "message": self.message,
            "status": self.status,
            "reply": self.reply,
            "created_at": self.created_at.strftime("%Y-%m-%d %H:%M") if self.created_at else None,
            "updated_at": self.updated_at.strftime("%Y-%m-%d %H:%M") if self.updated_at else None,
        }


class Conversation(db.Model):
    """Model for real-time messaging conversations"""
    __tablename__ = "conversations"

    id = db.Column(db.Integer(), primary_key=True)
    user_id = db.Column(db.Integer(), db.ForeignKey("users.id"), nullable=False)
    agent_id = db.Column(db.Integer(), db.ForeignKey("agent_profiles.id"), nullable=False)
    property_id = db.Column(db.Integer(), db.ForeignKey("properties.id"), nullable=True)
    last_message = db.Column(db.Text(), nullable=True)
    last_message_at = db.Column(db.DateTime(), server_default=db.func.now())
    created_at = db.Column(db.DateTime(), server_default=db.func.now())
    updated_at = db.Column(db.DateTime(), server_default=db.func.now(), onupdate=db.func.now())


class Message(db.Model):
    """Model for individual messages in a conversation"""
    __tablename__ = "messages"

    id = db.Column(db.Integer(), primary_key=True)
    conversation_id = db.Column(db.Integer(), db.ForeignKey("conversations.id"), nullable=False)
    sender_id = db.Column(db.Integer(), db.ForeignKey("users.id"), nullable=False)
    sender_type = db.Column(db.Enum("user", "agent", name="sender_type"), nullable=False)
    content = db.Column(db.Text(), nullable=False)
    is_read = db.Column(db.Boolean(), default=False, nullable=False)
    created_at = db.Column(db.DateTime(), server_default=db.func.now())
    updated_at = db.Column(db.DateTime(), server_default=db.func.now(), onupdate=db.func.now())


class Review(db.Model):
    """Model for user reviews/ratings of agents"""
    __tablename__ = "reviews"

    id = db.Column(db.Integer(), primary_key=True)
    user_id = db.Column(db.Integer(), db.ForeignKey("users.id"), nullable=False)
    agent_id = db.Column(db.Integer(), db.ForeignKey("agent_profiles.id"), nullable=False)
    property_id = db.Column(db.Integer(), db.ForeignKey("properties.id"), nullable=True)
    rating = db.Column(db.Integer(), nullable=False)  # 1-5 stars
    comment = db.Column(db.Text(), nullable=True)
    created_at = db.Column(db.DateTime(), server_default=db.func.now())
    updated_at = db.Column(db.DateTime(), server_default=db.func.now(), onupdate=db.func.now())


class Notification(db.Model):
    """Model for user notifications"""
    __tablename__ = "notifications"

    id = db.Column(db.Integer(), primary_key=True)
    user_id = db.Column(db.Integer(), db.ForeignKey("users.id"), nullable=False)
    title = db.Column(db.Text(), nullable=False)
    message = db.Column(db.Text(), nullable=False)
    notification_type = db.Column(db.Enum("inquiry", "viewing", "property", "system", name="notification_type"), default="system")
    is_read = db.Column(db.Boolean(), default=False, nullable=False)
    created_at = db.Column(db.DateTime(), server_default=db.func.now())
    updated_at = db.Column(db.DateTime(), server_default=db.func.now(), onupdate=db.func.now())



    
    

    












