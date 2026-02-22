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
            user_id=admin.id,
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
            user_id=agent_user.id,
            license_number="LIC-001",
            agency_id=agency.id,
            bio="Experienced real estate agent",
            rating=5,
        )

        user_profile = UserProfile(user_id=normal_user.id)

        db.session.add_all([admin_profile, agent_profile, user_profile])
        db.session.commit()

        print("🏠 Creating property types...")
        property_types = [
            Property_type(name="Apartment"),
            Property_type(name="Villa"),
            Property_type(name="Bungalow"),
            Property_type(name="Mansion"),
            Property_type(name="House"),
            Property_type(name="Maisonette"),
            Property_type(name="Commercial"),
        ]
        
        db.session.add_all(property_types)
        db.session.commit()
        
        # Create a dictionary for easy access
        pt = {pt.name: pt for pt in property_types}

        print("📍 Creating locations...")
        locations_data = [
            {"neighborhood": "Westlands", "latitude": "-1.268", "longitude": "36.811"},
            {"neighborhood": "Karen", "latitude": "-1.318", "longitude": "36.751"},
            {"neighborhood": "Upper Hill", "latitude": "-1.300", "longitude": "36.820"},
            {"neighborhood": "Runda", "latitude": "-1.230", "longitude": "36.830"},
            {"neighborhood": "Langata", "latitude": "-1.360", "longitude": "36.740"},
            {"neighborhood": "Ngong Road", "latitude": "-1.320", "longitude": "36.780"},
            {"neighborhood": "CBD", "latitude": "-1.283", "longitude": "36.820"},
            {"neighborhood": "South C", "latitude": "-1.320", "longitude": "36.850"},
        ]
        
        locations = []
        for loc in locations_data:
            location = Location(
                country="Kenya",
                state="Nairobi",
                city="Nairobi",
                neighborhood=loc["neighborhood"],
                latitude=loc["latitude"],
                longitude=loc["longitude"],
            )
            locations.append(location)
        
        db.session.add_all(locations)
        db.session.commit()

        print("🏡 Creating properties...")
        
        # Original property
        property1 = Property(
            title="Modern 2 Bedroom Apartment",
            description="Spacious apartment with parking",
            property_type_id=pt["Apartment"].id,
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

        # Property 2 - 4 Bedroom Bungalow
        property2 = Property(
            title="4 Bedroom Bungalow for Sale",
            description="Spacious home with garden",
            property_type_id=pt["Bungalow"].id,
            agent_id=agent_profile.id,
            price=25000000,
            currency="KES",
            bedrooms=4,
            bathrooms=3,
            area_size=200,
            area_unit="sqm",
            listing_type="sale",
            status="onsale",
            listing_date=datetime.utcnow(),
        )
        db.session.add(property2)

        # Property 3 - Studio Apartment
        property3 = Property(
            title="Studio Apartment for Rent",
            description="Ideal for singles, secure estate",
            property_type_id=pt["Apartment"].id,
            agent_id=agent_profile.id,
            price=25000,
            currency="KES",
            bedrooms=1,
            bathrooms=1,
            area_size=45,
            area_unit="sqm",
            listing_type="rent",
            status="onrent",
            listing_date=datetime.utcnow(),
        )
        db.session.add(property3)

        # Property 4 - 5 Bedroom Mansion
        property4 = Property(
            title="5 Bedroom Mansion for Sale",
            description="Luxury living with compound",
            property_type_id=pt["Mansion"].id,
            agent_id=agent_profile.id,
            price=45000000,
            currency="KES",
            bedrooms=5,
            bathrooms=4,
            area_size=400,
            area_unit="sqm",
            listing_type="sale",
            status="onsale",
            listing_date=datetime.utcnow(),
        )
        db.session.add(property4)

        # Property 5 - 3 Bedroom House
        property5 = Property(
            title="3 Bedroom House for Rent",
            description="Family home, pet-friendly",
            property_type_id=pt["House"].id,
            agent_id=agent_profile.id,
            price=60000,
            currency="KES",
            bedrooms=3,
            bathrooms=2,
            area_size=150,
            area_unit="sqm",
            listing_type="rent",
            status="onrent",
            listing_date=datetime.utcnow(),
        )
        db.session.add(property5)

        # Property 6 - 1 Bedroom Apartment
        property6 = Property(
            title="1 Bedroom Apartment for Sale",
            description="Affordable entry-level investment",
            property_type_id=pt["Apartment"].id,
            agent_id=agent_profile.id,
            price=4800000,
            currency="KES",
            bedrooms=1,
            bathrooms=1,
            area_size=50,
            area_unit="sqm",
            listing_type="sale",
            status="onsale",
            listing_date=datetime.utcnow(),
        )
        db.session.add(property6)

        # Property 7 - Office Space
        property7 = Property(
            title="Office Space for Rent",
            description="Prime business location",
            property_type_id=pt["Commercial"].id,
            agent_id=agent_profile.id,
            price=80000,
            currency="KES",
            bedrooms=0,
            bathrooms=2,
            area_size=100,
            area_unit="sqm",
            listing_type="rent",
            status="onrent",
            listing_date=datetime.utcnow(),
        )
        db.session.add(property7)

        # Property 8 - 2 Bedroom Maisonette
        property8 = Property(
            title="2 Bedroom Maisonette for Sale",
            description="Dual-key property, ideal for rental",
            property_type_id=pt["Maisonette"].id,
            agent_id=agent_profile.id,
            price=8500000,
            currency="KES",
            bedrooms=2,
            bathrooms=2,
            area_size=90,
            area_unit="sqm",
            listing_type="sale",
            status="onsale",
            listing_date=datetime.utcnow(),
        )
        db.session.add(property8)

        db.session.commit()

        print("📍 Creating property locations...")
        properties = [property1, property2, property3, property4, property5, property6, property7, property8]
        
        for idx, property in enumerate(properties):
            property_location = PropertyLocation(
                property_id=property.id,
                location_id=locations[idx].id
            )
            db.session.add(property_location)
        
        db.session.commit()

        print("⭐ Creating amenities...")
        amenities_data = ["WiFi", "Parking", "Swimming Pool", "Garden", "24/7 Security", "Gym", "Furnished"]
        amenities = []
        
        for amenity_name in amenities_data:
            amenity = Amenity(name=amenity_name)
            amenities.append(amenity)
        
        db.session.add_all(amenities)
        db.session.commit()
        
        # Create a dictionary for easy access
        am = {a.name: a for a in amenities}

        print("🔗 Adding property amenities...")
        property_amenities = [
            # Property 1
            PropertyAmenity(property_id=property1.id, amenity_id=am["WiFi"].id),
            PropertyAmenity(property_id=property1.id, amenity_id=am["Parking"].id),
            # Property 2
            PropertyAmenity(property_id=property2.id, amenity_id=am["Garden"].id),
            PropertyAmenity(property_id=property2.id, amenity_id=am["Parking"].id),
            PropertyAmenity(property_id=property2.id, amenity_id=am["24/7 Security"].id),
            # Property 3
            PropertyAmenity(property_id=property3.id, amenity_id=am["WiFi"].id),
            PropertyAmenity(property_id=property3.id, amenity_id=am["24/7 Security"].id),
            PropertyAmenity(property_id=property3.id, amenity_id=am["Furnished"].id),
            # Property 4
            PropertyAmenity(property_id=property4.id, amenity_id=am["Swimming Pool"].id),
            PropertyAmenity(property_id=property4.id, amenity_id=am["Gym"].id),
            PropertyAmenity(property_id=property4.id, amenity_id=am["Parking"].id),
            PropertyAmenity(property_id=property4.id, amenity_id=am["24/7 Security"].id),
            PropertyAmenity(property_id=property4.id, amenity_id=am["Garden"].id),
            # Property 5
            PropertyAmenity(property_id=property5.id, amenity_id=am["Garden"].id),
            PropertyAmenity(property_id=property5.id, amenity_id=am["Parking"].id),
            PropertyAmenity(property_id=property5.id, amenity_id=am["24/7 Security"].id),
            # Property 6
            PropertyAmenity(property_id=property6.id, amenity_id=am["Parking"].id),
            PropertyAmenity(property_id=property6.id, amenity_id=am["24/7 Security"].id),
            # Property 7
            PropertyAmenity(property_id=property7.id, amenity_id=am["Parking"].id),
            PropertyAmenity(property_id=property7.id, amenity_id=am["WiFi"].id),
            PropertyAmenity(property_id=property7.id, amenity_id=am["24/7 Security"].id),
            # Property 8
            PropertyAmenity(property_id=property8.id, amenity_id=am["Parking"].id),
            PropertyAmenity(property_id=property8.id, amenity_id=am["24/7 Security"].id),
        ]
        
        db.session.add_all(property_amenities)
        db.session.commit()

        print("🖼 Adding images...")
        image_urls = [
            # Property 1
            "https://example.com/property1.jpg",
            # Property 2
            "https://images.unsplash.com/photo-1593696140826-c58b021acf8b?ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxzZWFyY2h8MzB8fGhvbWUlMjBpbnRlcmlvcnxlbnwwfHwwfHx8MA%3D%3D&auto=format&fit=crop&q=60&w=500",
            # Property 3
            "https://imgs.search.brave.com/ovEir4fdsAbd1NyFQ29CbpWvBccx5MzvFYMYuO2-XY0/rs:fit:500:0:1:0/g:ce/aHR0cHM6Ly90NC5m/dGNkbi5uZXQvanBn/LzA5LzU1Lzg5LzU5/LzM2MF9GXzk1NTg5/NTkyMl9QaDYzZ1JQ/RWRpMEZlS3VtZDla/YUJFSXBjdFBySVJQ/Ni5qcGc",
            # Property 4
            "https://imgs.search.brave.com/VGVaY4G_x6I-QdfBE6c1-b2rDkRuM2lzjAxxZ3NZZwY/rs:fit:500:0:1:0/g:ce/aHR0cHM6Ly9tZWRp/YS5nZXR0eWltYWdl/cy5jb20vaWQvMTM2/MzgxNzUzNy9waG90/by9sdXh1cnktbW9k/ZXJuLWhvdXNlLWlu/dGVyaW9yLXdpdGgt/Y29ybmVyLXNvZmEt/Ym9va3NoZWxmLWFu/ZC1zdGFpcmNhc2Uu/anBnP3M9NjEyeDYx/MiZ3PTAmaz0yMCZj/PUJZOUV2cmdMX1Zz/UWtUa2V0bmNlMHl2/OWxURXB2WmtWdzBZ/OU5rTW94Tjg9",
            # Property 5
            "https://imgs.search.brave.com/n49JVlj4UkEyfFMoxIcZndukfETd-9HV2soPMQSeqB8/rs:fit:500:0:1:0/g:ce/aHR0cHM6Ly90NC5m/dGNkbi5uZXQvanBn/LzA1Lzc5LzU3LzI1/LzM2MF9GXzU3OTU3/MjU4Ml9UWkRVSlVV/VDBqZkxCUXZwcDZ5/U1hCME82c3RHZGFk/Sy5qcGc",
            # Property 6
            "https://imgs.search.brave.com/jvQaZyIokhRCLEb4qisbTCNJgVDtxqwVSgUrXJcy11U/rs:fit:500:0:1:0/g:ce/aHR0cHM6Ly9tZWRp/YS5pc3RvY2twaG90/by5jb20vaWQvMTc4/OTg4MTgzL3Bob3Rv/L2hvdXNlLWluLWJh/ZC1zdW1tZXItdGh1/bmRlcnN0b3JtLmpw/Zz9zPTYxMng2MTIm/dz0wJms9MjAmYz1L/QXhkWTFtTTRIN2l4/S2h6NzMxWFhZR2Y1/UzA4MWJzSGItU3lY/Zk5EVWRJPQ",
            # Property 7
            "https://imgs.search.brave.com/hC4PIeTn5WarfR1FYVsRK5GvJIhslicZLUvdSObR7YA/rs:fit:500:0:1:0/g:ce/aHR0cHM6Ly9pbWFn/ZXMuc3F1YXJlc3Bh/Y2UtY2RuLmNvbS9j/b250ZW50L3YxLzYz/Nzc4NDY0YTE0YzU0/NTAyZmZkOWQ4YS84/YjE4ZjZlMC05OWFl/LTQ4OGEtOTk2OC1j/YjZkMGJhZDY1NDUv/RmFtcmhvdXNlLUhv/bWVwYWdlLTMtMTAy/NHg2MjAucG5n",
            # Property 8
            "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTqdqF5shrilcOGvhLMQKyoHL0eHgxBH80iUw&s",
        ]
        
        for idx, property in enumerate(properties):
            image = PropertyImage(
                property_id=property.id,
                image_url=image_urls[idx],
                is_primary=True,
            )
            db.session.add(image)
        
        db.session.commit()

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