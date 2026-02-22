from flask import request, send_from_directory
from models import db, AgentProfile, Property, Inquiry, View, Payment, PropertyImage, PropertyVideo, User, Property_type, Location, PropertyLocation
from flask_restful import Resource
from flask_jwt_extended import get_jwt_identity
from utils import agent_required
from datetime import datetime
from sqlalchemy import func
import os

# Configure upload folder - same as in app.py
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


class AgentStatsResource(Resource):
    @agent_required()
    def get(self):
        # Get current agent's ID from JWT
        current_user_id = get_jwt_identity()

        # Get the agents profile to get all listed properties
        agent_profile = AgentProfile.query.filter_by(user_id=current_user_id).first()

        # Count number of listings
        listings_count = 0
        if agent_profile:
            listings_count = Property.query.filter_by(agent_id=agent_profile.id).count()

        # Count Inquiries
        inquiries_count = Inquiry.query.filter_by(agent_id=agent_profile.id).count()

        # Count viewings - get all properties owned by the agent, then count views for those properties
        property_ids = []
        if agent_profile:
            agent_properties = Property.query.filter_by(agent_id=agent_profile.id).all()
            property_ids = [p.id for p in agent_properties]
        
        viewings_count = 0
        if property_ids:
            viewings_count = View.query.filter(View.property_id.in_(property_ids)).count()

        # Count monthly revenue - filter by current agent and status "complete"
        now = datetime.now()
        start_of_month = datetime(now.year, now.month, 1)
        
        monthly_revenue = 0
        if agent_profile:
            monthly_revenue = db.session.query(db.func.sum(Payment.amount)).filter(
                Payment.agent_id == agent_profile.id,
                Payment.status == "complete",
                Payment.created_at >= start_of_month
            ).scalar() or 0

        return {
            "listings": listings_count,
            "inquiries": inquiries_count,
            "viewings": viewings_count,
            "revenue": monthly_revenue
        }, 200


class AgentPropertiesResource(Resource):
    @agent_required()
    def get(self):
        """Get agent's recent properties with view counts"""
        current_user_id = get_jwt_identity()
        agent_profile = AgentProfile.query.filter_by(user_id=current_user_id).first()
        
        if not agent_profile:
            return {"properties": []}, 200
        
        # Get limit from query params (default 5)
        limit = request.args.get('limit', 5, type=int)
        
        # Get properties with view counts
        properties = Property.query.filter_by(agent_id=agent_profile.id).order_by(
            Property.created_at.desc()
        ).limit(limit).all()
        
        properties_data = []
        for prop in properties:
            # Get primary image
            primary_image = PropertyImage.query.filter_by(
                property_id=prop.id, 
                is_primary=True
            ).first()
            
            # Count views for this property
            view_count = View.query.filter_by(property_id=prop.id).count()
            
            properties_data.append({
                "id": prop.id,
                "title": prop.title,
                "price": prop.price,
                "currency": prop.currency,
                "listing_type": prop.listing_type,
                "status": prop.status,
                "bedrooms": prop.bedrooms,
                "bathrooms": prop.bathrooms,
                "views": view_count,
                "image": primary_image.image_url if primary_image else None,
                "created_at": prop.created_at.isoformat() if prop.created_at else None
            })
        
        return {"properties": properties_data}, 200


class AgentInquiriesResource(Resource):
    @agent_required()
    def get(self):
        """Get agent's recent inquiries"""
        current_user_id = get_jwt_identity()
        agent_profile = AgentProfile.query.filter_by(user_id=current_user_id).first()
        
        if not agent_profile:
            return {"inquiries": []}, 200
        
        # Get limit from query params (default 5)
        limit = request.args.get('limit', 5, type=int)
        
        # Get recent inquiries with user and property info
        inquiries = Inquiry.query.filter_by(agent_id=agent_profile.id).order_by(
            Inquiry.created_at.desc()
        ).limit(limit).all()
        
        inquiries_data = []
        for inquiry in inquiries:
            # Get user info
            user = User.query.get(inquiry.user_id)
            # Get property info
            property = Property.query.get(inquiry.property_id)
            
            # Calculate time ago
            time_ago = ""
            if inquiry.created_at:
                diff = datetime.now() - inquiry.created_at
                if diff.days > 0:
                    time_ago = f"{diff.days} day{'s' if diff.days > 1 else ''} ago"
                elif diff.seconds // 3600 > 0:
                    time_ago = f"{diff.seconds // 3600} hour{'s' if diff.seconds // 3600 > 1 else ''} ago"
                else:
                    time_ago = "Just now"
            
            inquiries_data.append({
                "id": inquiry.id,
                "user_id": inquiry.user_id,
                "name": f"{user.first_name} {user.last_name}" if user else "Unknown",
                "property_id": inquiry.property_id,
                "property": property.title if property else "Unknown Property",
                "message": inquiry.message,
                "status": inquiry.status,
                "time": time_ago,
                "created_at": inquiry.created_at.isoformat() if inquiry.created_at else None
            })
        
        return {"inquiries": inquiries_data}, 200


class AgentPropertyDetailResource(Resource):
    @agent_required()
    def get(self, property_id):
        """Get single property details for agent"""
        current_user_id = get_jwt_identity()
        agent_profile = AgentProfile.query.filter_by(user_id=current_user_id).first()
        
        if not agent_profile:
            return {"message": "Agent profile not found"}, 404
        
        # Get property that belongs to this agent
        property = Property.query.filter_by(id=property_id, agent_id=agent_profile.id).first()
        
        if not property:
            return {"message": "Property not found"}, 404
        
        # Get images
        images = PropertyImage.query.filter_by(property_id=property.id).order_by(PropertyImage.is_primary.desc(), PropertyImage.id).all()
        
        # Deduplicate images by image_url - keep only unique URLs
        seen_urls = set()
        unique_images = []
        for img in images:
            if img.image_url not in seen_urls:
                seen_urls.add(img.image_url)
                unique_images.append(img)
        
        # Get videos (note: model has 'propert_id' typo)
        videos = PropertyVideo.query.filter_by(propert_id=property.id).all()
        
        # Deduplicate videos
        seen_video_urls = set()
        unique_videos = []
        for vid in videos:
            if vid.video_url not in seen_video_urls:
                seen_video_urls.add(vid.video_url)
                unique_videos.append(vid)
        
        # Get view count
        view_count = View.query.filter_by(property_id=property.id).count()
        
        # Get property type
        property_type = Property_type.query.get(property.property_type_id)
        
        # Get location
        prop_location = PropertyLocation.query.filter_by(property_id=property.id).first()
        location = None
        if prop_location:
            location = Location.query.get(prop_location.location_id)
        
        return {
            "property": {
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
                "year_built": property.year_built.isoformat() if property.year_built else None,
                "listing_date": property.listing_date.isoformat() if property.listing_date else None,
                "property_type_id": property.property_type_id,
                "property_type": property_type.name if property_type else None,
                "views": view_count,
                "created_at": property.created_at.isoformat() if property.created_at else None,
            },
            "images": [{"id": img.id, "url": img.image_url, "is_primary": img.is_primary} for img in unique_images],
            "videos": [{"id": vid.id, "url": vid.video_url} for vid in unique_videos],
            "location": {
                "id": location.id if location else None,
                "country": location.country if location else None,
                "state": location.state if location else None,
                "city": location.city if location else None,
                "neighborhood": location.neighborhood if location else None,
                "latitude": location.latitude if location else None,
                "longitude": location.longitude if location else None,
            } if location else None
        }, 200


class AgentPropertyCreateResource(Resource):
    @agent_required()
    def post(self):
        """Create a new property"""
        current_user_id = get_jwt_identity()
        agent_profile = AgentProfile.query.filter_by(user_id=current_user_id).first()
        
        if not agent_profile:
            return {"message": "Agent profile not found"}, 404
        
        # DEBUG: Log what's being received
        print("=== DEBUG: Form Data Received ===")
        print("Form keys:", list(request.form.keys()))
        print("Form values:", dict(request.form))
        print("Files:", list(request.files.keys()))
        
        # Get form data
        title = request.form.get('title')
        description = request.form.get('description')
        price = request.form.get('price')
        currency = request.form.get('currency', 'Ksh')
        listing_type = request.form.get('listing_type')
        status = request.form.get('status', 'onsale')
        property_type_id = request.form.get('property_type_id')
        bedrooms = request.form.get('bedrooms', type=int)
        bathrooms = request.form.get('bathrooms', type=int)
        area_size = request.form.get('area_size', type=int)
        area_unit = request.form.get('area_unit')
        
        # DEBUG: Log individual fields
        print(f"title: '{title}' (type: {type(title)})")
        print(f"price: '{price}' (type: {type(price)})")
        print(f"listing_type: '{listing_type}' (type: {type(listing_type)})")
        print(f"property_type_id: '{property_type_id}' (type: {type(property_type_id)})")
        
        # Validation
        if not all([title, price, listing_type, property_type_id]):
            missing = []
            if not title: missing.append('title')
            if not price: missing.append('price')
            if not listing_type: missing.append('listing_type')
            if not property_type_id: missing.append('property_type_id')
            print(f"=== DEBUG: Missing fields: {missing} ===")
            return {"message": "Title, price, listing type, and property type are required", "missing_fields": missing}, 400
        
        # Create property
        property = Property(
            title=title,
            description=description,
            price=int(price),
            currency=currency,
            listing_type=listing_type,
            status=status,
            property_type_id=int(property_type_id),
            agent_id=agent_profile.id,
            bedrooms=bedrooms,
            bathrooms=bathrooms,
            area_size=area_size,
            area_unit=area_unit,
            listing_date=datetime.now()
        )
        
        db.session.add(property)
        db.session.flush()  # Get property ID
        
        # Handle images
        images = request.files.getlist('images')
        print(f"=== DEBUG: Found {len(images)} images ===")
        for i, image in enumerate(images):
            if image:
                # Save to disk
                filename = f"property_{property.id}_{i}_{image.filename}"
                filepath = os.path.join(UPLOAD_FOLDER, filename)
                image.save(filepath)
                image_url = f"/uploads/{filename}"
                
                is_primary = request.form.get(f'is_primary_{i}', 'false').lower() == 'true' if i == 0 else False
                
                prop_image = PropertyImage(
                    property_id=property.id,
                    image_url=image_url,
                    is_primary=is_primary
                )
                db.session.add(prop_image)
                print(f"=== DEBUG: Saved image {i}: {image_url} ===")
        
        # Handle videos
        videos = request.files.getlist('videos')
        print(f"=== DEBUG: Found {len(videos)} videos ===")
        for video in videos:
            if video:
                filename = f"property_{property.id}_{video.filename}"
                filepath = os.path.join(UPLOAD_FOLDER, filename)
                video.save(filepath)
                video_url = f"/uploads/{filename}"
                
                prop_video = PropertyVideo(
                    propert_id=property.id,
                    video_url=video_url
                )
                db.session.add(prop_video)
                print(f"=== DEBUG: Saved video: {video_url} ===")
        
        # Handle location
        city = request.form.get('city')
        neighborhood = request.form.get('neighborhood')
        if city or neighborhood:
            location = Location(
                city=city,
                neighborhood=neighborhood
            )
            db.session.add(location)
            db.session.flush()
            
            prop_location = PropertyLocation(
                property_id=property.id,
                location_id=location.id
            )
            db.session.add(prop_location)
        
        db.session.commit()
        
        return {
            "message": "Property created successfully",
            "property_id": property.id
        }, 201


class AgentPropertyUpdateResource(Resource):
    @agent_required()
    def put(self, property_id):
        """Update an existing property"""
        current_user_id = get_jwt_identity()
        agent_profile = AgentProfile.query.filter_by(user_id=current_user_id).first()
        
        if not agent_profile:
            return {"message": "Agent profile not found"}, 404
        
        # Get property that belongs to this agent
        property = Property.query.filter_by(id=property_id, agent_id=agent_profile.id).first()
        
        if not property:
            return {"message": "Property not found"}, 404
        
        # Update fields
        if request.form.get('title'):
            property.title = request.form.get('title')
        if request.form.get('description'):
            property.description = request.form.get('description')
        if request.form.get('price'):
            property.price = int(request.form.get('price'))
        if request.form.get('currency'):
            property.currency = request.form.get('currency')
        if request.form.get('listing_type'):
            property.listing_type = request.form.get('listing_type')
        if request.form.get('status'):
            property.status = request.form.get('status')
        if request.form.get('property_type_id'):
            property.property_type_id = int(request.form.get('property_type_id'))
        if request.form.get('bedrooms'):
            property.bedrooms = int(request.form.get('bedrooms'))
        if request.form.get('bathrooms'):
            property.bathrooms = int(request.form.get('bathrooms'))
        if request.form.get('area_size'):
            property.area_size = int(request.form.get('area_size'))
        if request.form.get('area_unit'):
            property.area_unit = request.form.get('area_unit')
        
        # Handle new images
        images = request.files.getlist('images')
        for image in images:
            if image:
                filename = f"property_{property.id}_{image.filename}"
                image_url = f"/uploads/{filename}"
                
                # Check if this is first image, make it primary
                existing_images = PropertyImage.query.filter_by(property_id=property.id).count()
                is_primary = existing_images == 0
                
                prop_image = PropertyImage(
                    property_id=property.id,
                    image_url=image_url,
                    is_primary=is_primary
                )
                db.session.add(prop_image)
        
        # Handle existing images to keep
        existing_images = request.form.get('existing_images')
        if existing_images:
            import json
            kept_images = json.loads(existing_images)
            # Keep only the specified images, delete others
            PropertyImage.query.filter(
                PropertyImage.property_id == property.id,
                ~PropertyImage.id.in_(kept_images)
            ).delete(synchronize_session=False)
        
        # Handle new videos
        videos = request.files.getlist('videos')
        for video in videos:
            if video:
                filename = f"property_{property.id}_{video.filename}"
                video_url = f"/uploads/{filename}"
                
                prop_video = PropertyVideo(
                    propert_id=property.id,
                    video_url=video_url
                )
                db.session.add(prop_video)
        
        # Handle existing videos to keep
        existing_videos = request.form.get('existing_videos')
        if existing_videos:
            import json
            kept_videos = json.loads(existing_videos)
            PropertyVideo.query.filter(
                PropertyVideo.propert_id == property.id,
                ~PropertyVideo.id.in_(kept_videos)
            ).delete(synchronize_session=False)
        
        db.session.commit()
        
        return {
            "message": "Property updated successfully",
            "property_id": property.id
        }, 200


class AgentPropertyDeleteResource(Resource):
    @agent_required()
    def delete(self, property_id):
        """Delete a property"""
        current_user_id = get_jwt_identity()
        agent_profile = AgentProfile.query.filter_by(user_id=current_user_id).first()
        
        if not agent_profile:
            return {"message": "Agent profile not found"}, 404
        
        # Get property that belongs to this agent
        property = Property.query.filter_by(id=property_id, agent_id=agent_profile.id).first()
        
        if not property:
            return {"message": "Property not found"}, 404
        
        # Delete related records first
        PropertyImage.query.filter_by(property_id=property.id).delete(synchronize_session=False)
        PropertyVideo.query.filter_by(propert_id=property.id).delete(synchronize_session=False)
        PropertyLocation.query.filter_by(property_id=property.id).delete(synchronize_session=False)
        View.query.filter_by(property_id=property.id).delete(synchronize_session=False)
        Inquiry.query.filter_by(property_id=property.id).delete(synchronize_session=False)
        
        # Delete property
        db.session.delete(property)
        db.session.commit()
        
        return {"message": "Property deleted successfully"}, 200

