from app import app
from models import (
    db,
    User, Agent, Owner, Agency,
    Property_type, Property,
    Location, PropertyLocation,
    Amenity, PropertyAmenity,
    PropertyImage, Subscription, Payment
)
from datetime import datetime, timedelta
import random


def seed_data():
    with app.app_context():
        print("🌱 Clearing existing data...")

        # Order matters because of FK constraints
        PropertyAmenity.query.delete()
        PropertyLocation.query.delete()
        PropertyImage.query.delete()
        Property.query.delete()
        Amenity.query.delete()
        Location.query.delete()
        Agent.query.delete()
        Owner.query.delete()
        Agency.query.delete()
        Property_type.query.delete()
        Payment.query.delete()
        Subscription.query.delete()
        User.query.delete()

        db.session.commit()

        print("👤 Creating users...")
        admin = User(
            name="Admin User",
            phone="+254700000001",
            email="admin@example.com",
            password="admin123",
            role="admin",
            is_verified=True
        )

        agent_user = User(
            name="Jane Agent",
            phone="+254700000002",
            email="agent@example.com",
            password="agent123",
            role="agent",
            is_verified=True
        )

        owner_user = User(
            name="John Owner",
            phone="+254700000003",
            email="owner@example.com",
            password="owner123",
            role="user",
            is_verified=True
        )

        client_user = User(
            name="Client User",
            phone="+254700000004",
            email="client@example.com",
            password="client123",
            role="user",
            is_verified=False
        )

        db.session.add_all([admin, agent_user, owner_user, client_user])
        db.session.commit()

        print("🏢 Creating agency...")
        agency = Agency(
            name="Prime Homes Ltd",
            address="Westlands, Nairobi",
            phone="+254711111111",
            founded_year="2015"
        )
        db.session.add(agency)
        db.session.commit()

        print("🧑‍💼 Creating agent & owner...")
        agent = Agent(
            user_id=agent_user.id,
            license_number="AGT-001",
            agency_id=agency.id,
            bio="Experienced real estate agent",
            rating=5
        )

        owner = Owner(
            user_id=owner_user.id
        )

        db.session.add_all([agent, owner])
        db.session.commit()

        print("🏠 Creating property types...")
        apartment = Property_type(name="Apartment")
        house = Property_type(name="House")
        land = Property_type(name="Land")

        db.session.add_all([apartment, house, land])
        db.session.commit()

        print("📍 Creating locations...")
        location1 = Location(
            country="Kenya",
            state="Nairobi",
            city="Nairobi",
            neighborhood="Kilimani",
            latitude="-1.2921",
            longitude="36.8219"
        )

        location2 = Location(
            country="Kenya",
            state="Nairobi",
            city="Nairobi",
            neighborhood="Westlands",
            latitude="-1.2673",
            longitude="36.8121"
        )

        db.session.add_all([location1, location2])
        db.session.commit()

        print("🏘️ Creating properties...")
        property1 = Property(
            title="Modern 2 Bedroom Apartment",
            description="Spacious apartment with city views",
            property_type_id=apartment.id,
            owner_id=owner.id,
            agent_id=agent.id,
            price=12000000,
            currency="KES",
            bedrooms=2,
            bathrooms=2,
            area_size=120,
            area_unit="sqm",
            listing_type="sale",
            status="onsale",
            year_built=datetime(2019, 1, 1),
            listing_date=datetime.now()
        )

        property2 = Property(
            title="Luxury 4 Bedroom House",
            description="Standalone house with garden",
            property_type_id=house.id,
            owner_id=owner.id,
            agent_id=agent.id,
            price=250000,
            currency="KES",
            bedrooms=4,
            bathrooms=3,
            area_size=350,
            area_unit="sqm",
            listing_type="rent",
            status="onrent",
            year_built=datetime(2015, 1, 1),
            listing_date=datetime.now()
        )

        db.session.add_all([property1, property2])
        db.session.commit()

        print("📌 Linking properties to locations...")
        db.session.add_all([
            PropertyLocation(property_id=property1.id, location_id=location1.id),
            PropertyLocation(property_id=property2.id, location_id=location2.id)
        ])
        db.session.commit()

        print("✨ Creating amenities...")
        wifi = Amenity(name="WiFi")
        parking = Amenity(name="Parking")
        pool = Amenity(name="Swimming Pool")

        db.session.add_all([wifi, parking, pool])
        db.session.commit()

        print("🔗 Linking amenities...")
        db.session.add_all([
            PropertyAmenity(property_id=property1.id, amenity_id=wifi.id),
            PropertyAmenity(property_id=property1.id, amenity_id=parking.id),
            PropertyAmenity(property_id=property2.id, amenity_id=parking.id),
            PropertyAmenity(property_id=property2.id, amenity_id=pool.id),
        ])
        db.session.commit()

        print("🖼️ Adding property images...")
        db.session.add_all([
            PropertyImage(
                property_id=property1.id,
                image_url="https://example.com/apartment1.jpg",
                caption="Living Room",
                is_primary=True
            ),
            PropertyImage(
                property_id=property2.id,
                image_url="https://example.com/house1.jpg",
                caption="Front View",
                is_primary=True
            )
        ])
        db.session.commit()

        print("💳 Creating subscription & payment...")
        subscription = Subscription(
            user_id=client_user.id,
            plan="premium",
            expires_at=datetime.now() + timedelta(days=30)
        )

        payment = Payment(
            user_id=client_user.id,
            amount=5000,
            payment_method="mpesa",
            status="complete"
        )

        db.session.add_all([subscription, payment])
        db.session.commit()

        print("✅ Database seeded successfully!")


if __name__ == "__main__":
    seed_data()
