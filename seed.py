from app import app
from models import (
    db,
    User,
    AdminProfile,
    AgentProfile,
    UserProfile,
    Agency,
    Property_type,
    Property,
    Location,
    PropertyLocation,
    Amenity,
    PropertyAmenity,
    PropertyImage,
    Subscription,
    Payment,
    Favorite,
)
from flask_bcrypt import generate_password_hash
from datetime import datetime, timedelta
import random


def seed_data():
    with app.app_context():
        print("🌱 Clearing existing data...")
        db.drop_all()
        db.create_all()

        print("👤 Creating users...")
        admin = User(
            first_name="System",
            last_name="Admin",
            phone="0700000000",
            email="admin@example.com",
            password=generate_password_hash("admin123").decode("utf-8"),
            role="admin",
            is_verified=True,
        )

        agent_user = User(
            first_name="John",
            last_name="Agent",
            phone="0711111111",
            email="agent@example.com",
            password=generate_password_hash("agent123").decode("utf-8"),
            role="agent",
            is_verified=True,
        )

        normal_user = User(
            first_name="Jane",
            last_name="Buyer",
            phone="0722222222",
            email="user@example.com",
            password=generate_password_hash("user123").decode("utf-8"),
            role="user",
            is_verified=True,
        )

        db.session.add_all([admin, agent_user, normal_user])
        db.session.commit()

        print("🧑‍💼 Creating profiles...")
        admin_profile = AdminProfile(
            admin_id=admin.id,
            is_active=True,
            permission="full_access",
        )

        agency = Agency(
            name="Prime Realtors",
            address="Nairobi CBD",
            phone="0733333333",
            founded_year="2015",
        )
        db.session.add(agency)
        db.session.commit()

        agent_profile = AgentProfile(
            agent_id=agent_user.id,
            license_number="LIC-001",
            agency_id=agency.id,
            bio="Experienced real estate agent",
            rating=5,
        )

        user_profile = UserProfile(user_id=normal_user.id)

        db.session.add_all([admin_profile, agent_profile, user_profile])
        db.session.commit()

        print("🏠 Creating property types...")
        apartment = Property_type(name="Apartment")
        villa = Property_type(name="Villa")
        db.session.add_all([apartment, villa])
        db.session.commit()

        print("📍 Creating locations...")
        location = Location(
            country="Kenya",
            state="Nairobi",
            city="Nairobi",
            neighborhood="Westlands",
            latitude="-1.268",
            longitude="36.811",
        )
        db.session.add(location)
        db.session.commit()

        print("🏡 Creating properties...")
        property1 = Property(
            title="Modern 2 Bedroom Apartment",
            description="Spacious apartment with parking",
            property_type_id=apartment.id,
            agent_id=agent_profile.id,
            price=8500000,
            currency="KES",
            bedrooms=2,
            bathrooms=2,
            area_size=120,
            area_unit="sqm",
            listing_type="sale",
            status="onsale",
            listing_date=datetime.utcnow(),
        )

        db.session.add(property1)
        db.session.commit()

        property_location = PropertyLocation(
            property_id=property1.id,
            location_id=location.id,
        )
        db.session.add(property_location)

        print("⭐ Creating amenities...")
        wifi = Amenity(name="WiFi")
        parking = Amenity(name="Parking")
        pool = Amenity(name="Swimming Pool")
        db.session.add_all([wifi, parking, pool])
        db.session.commit()

        property_amenities = [
            PropertyAmenity(property_id=property1.id, amenity_id=wifi.id),
            PropertyAmenity(property_id=property1.id, amenity_id=parking.id),
        ]
        db.session.add_all(property_amenities)

        print("🖼 Adding images...")
        image = PropertyImage(
            property_id=property1.id,
            image_url="https://example.com/property1.jpg",
            is_primary=True,
        )
        db.session.add(image)

        print("💳 Creating subscription & payment...")
        subscription = Subscription(
            agent_id=agent_profile.id,
            plan="Premium",
            expires_at=datetime.utcnow() + timedelta(days=30),
        )

        payment = Payment(
            agent_id=agent_profile.id,
            amount=5000,
            payment_method="M-Pesa",
            status="complete",
        )

        db.session.add_all([subscription, payment])

        print("❤️ Creating favorite...")
        favorite = Favorite(
            user_id=user_profile.id,
            property_id=property1.id,
        )
        db.session.add(favorite)

        db.session.commit()
        print("✅ Database seeded successfully!")


if __name__ == "__main__":
    seed_data()
