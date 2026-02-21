from flask import request
from models import db, User, Property, Favorite, UserProfile, Inquiry, View, PropertyImage, PropertyLocation, Location, Property_type, AgentProfile, PropertyVideo, Conversation, Message
from flask_restful import Resource, reqparse
from flask_jwt_extended import get_jwt_identity
from utils import user_required
from datetime import datetime


class UserProfileResource(Resource):
    @user_required()
    def get(self):
        """Get current user's profile"""
        current_user_id = get_jwt_identity()
        
        user = User.query.get(current_user_id)
        
        if not user:
            return {"message": "User not found"}, 404
        
        user_profile = UserProfile.query.filter_by(user_id=current_user_id).first()
        
        profile_data = {
            'id': user.id,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'email': user.email,
            'phone': user.phone,
            'role': user.role,
            'is_verified': user.is_verified,
            'profile_picture': user_profile.profile_picture if user_profile else None,
            'created_at': user.created_at.strftime("%Y-%m-%d") if user.created_at else None,
            'updated_at': user.updated_at.strftime("%Y-%m-%d %H:%M") if user.updated_at else None
        }
        
        return profile_data, 200
    
    @user_required()
    def put(self):
        """Update current user's profile"""
        current_user_id = get_jwt_identity()
        
        user = User.query.get(current_user_id)
        
        if not user:
            return {"message": "User not found"}, 404
        
        data = request.get_json()
        
        if 'first_name' in data and data['first_name']:
            user.first_name = data['first_name']
        if 'last_name' in data and data['last_name']:
            user.last_name = data['last_name']
        if 'phone' in data and data['phone']:
            existing_phone = User.query.filter(User.phone == data['phone'], User.id != current_user_id).first()
            if existing_phone:
                return {"message": "Phone number already taken"}, 400
            user.phone = data['phone']
        
        user_profile = UserProfile.query.filter_by(user_id=current_user_id).first()
        
        if not user_profile:
            user_profile = UserProfile(user_id=current_user_id)
            db.session.add(user_profile)
        
        if 'profile_picture' in data:
            user_profile.profile_picture = data['profile_picture']
        
        db.session.commit()
        
        return {
            'message': 'Profile updated successfully',
            'profile': {
                'id': user.id,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'email': user.email,
                'phone': user.phone,
                'role': user.role,
                'is_verified': user.is_verified,
                'profile_picture': user_profile.profile_picture,
                'created_at': user.created_at.strftime("%Y-%m-%d") if user.created_at else None,
                'updated_at': user.updated_at.strftime("%Y-%m-%d %H:%M") if user.updated_at else None
            }
        }, 200


class UserPropertiesResource(Resource):
    def get(self):
        """Get all properties for user browsing with primary image and location"""
        properties = Property.query.all()

        result = []
        for prop in properties:
            prop_dict = prop.to_dict()
            
            # Get primary image
            primary_image = PropertyImage.query.filter_by(property_id=prop.id, is_primary=True).first()
            prop_dict['primary_image'] = primary_image.image_url if primary_image else None
            
            # Get location
            prop_location = PropertyLocation.query.filter_by(property_id=prop.id).first()
            if prop_location:
                location = Location.query.get(prop_location.location_id)
                if location:
                    prop_dict['location'] = location.neighborhood or location.city or f"{location.city}, {location.state}"
            
            # Get property type name for category filtering
            property_type = Property_type.query.get(prop.property_type_id)
            if property_type:
                prop_dict['property_type'] = property_type.name
            
            result.append(prop_dict)

        return result, 200


class UserPropertyDetailResource(Resource):
    def get(self, property_id):
        """Get single property with full details including agent info"""
        prop = Property.query.get(property_id)
        
        if not prop:
            return {"message": "Property not found"}, 404
        
        prop_dict = prop.to_dict()
        
        # Get primary image
        primary_image = PropertyImage.query.filter_by(property_id=prop.id, is_primary=True).first()
        prop_dict['primary_image'] = primary_image.image_url if primary_image else None
        
        # Get all images
        all_images = PropertyImage.query.filter_by(property_id=prop.id).all()
        prop_dict['images'] = [img.image_url for img in all_images]
        
        # Get all videos
        all_videos = PropertyVideo.query.filter_by(propert_id=prop.id).all()
        prop_dict['videos'] = [video.video_url for video in all_videos]
        
        # Get location details
        prop_location = PropertyLocation.query.filter_by(property_id=prop.id).first()
        if prop_location:
            location = Location.query.get(prop_location.location_id)
            if location:
                prop_dict['location'] = {
                    'neighborhood': location.neighborhood,
                    'city': location.city,
                    'state': location.state,
                    'country': location.country,
                    'latitude': location.latitude,
                    'longitude': location.longitude
                }
        
        # Get property type
        property_type = Property_type.query.get(prop.property_type_id)
        if property_type:
            prop_dict['property_type'] = property_type.name
        
        # Get agent info
        agent_profile = AgentProfile.query.get(prop.agent_id)
        if agent_profile:
            agent_user = User.query.get(agent_profile.agent_id)
            if agent_user:
                prop_dict['agent'] = {
                    'id': agent_user.id,
                    'name': f"{agent_user.first_name} {agent_user.last_name}",
                    'email': agent_user.email,
                    'phone': agent_user.phone,
                    'bio': agent_profile.bio,
                    'rating': agent_profile.rating,
                    'license_number': agent_profile.license_number
                }
        
        return prop_dict, 200

class UserStatsResource(Resource):
    @user_required()
    def get(self):
        # Get the current user's ID from JWT
        current_user_id = get_jwt_identity()
        
        # Get the user's profile to find favorites
        user_profile = UserProfile.query.filter_by(user_id=current_user_id).first()
        
        # Count saved properties (favorites)
        saved_count = 0
        if user_profile:
            saved_count = Favorite.query.filter_by(user_id=user_profile.id).count()
        
        # Count inquiries sent by this user
        inquiries_count = Inquiry.query.filter_by(user_id=current_user_id).count()
        
        # Count scheduled visits (views)
        visits_count = View.query.filter_by(user_id=current_user_id, status="pending").count()
        
        return {
            "saved": saved_count,
            "inquiries": inquiries_count,
            "visits": visits_count
        }, 200

class SavedPropertiesResource(Resource):
    @user_required()
    def get(self):
        current_user_id = get_jwt_identity()
        
        # Get optional limit parameter (default to 4 for home page, 0 for all)
        limit = request.args.get('limit', type=int, default=0)

        # Get user's profile
        user_profile = UserProfile.query.filter_by(user_id=current_user_id).first()

        if not user_profile:
            return {"properties": []}, 200

        # Get all favorites for this user
        favorites_query = Favorite.query.filter_by(user_id=user_profile.id)
        
        # Apply limit if specified
        if limit > 0:
            favorites = favorites_query.limit(limit).all()
        else:
            favorites = favorites_query.all()

        properties = []
        for fav in favorites:
            property = Property.query.get(fav.property_id)  
            if property:
                properties.append(property.to_dict())

        return {"properties": properties}, 200


class ToggleFavoriteResource(Resource):
    @user_required()
    def post(self):
        """Toggle favorite status for a property"""
        current_user_id = get_jwt_identity()
        
        # Get user's profile
        user_profile = UserProfile.query.filter_by(user_id=current_user_id).first()
        
        if not user_profile:
            return {"message": "User profile not found"}, 404
        
        # Get property_id from request
        data = request.get_json()
        property_id = data.get('property_id')
        
        if not property_id:
            return {"message": "Property ID is required"}, 400
        
        # Check if property exists
        property = Property.query.get(property_id)
        if not property:
            return {"message": "Property not found"}, 404
        
        # Check if already favorited
        existing_favorite = Favorite.query.filter_by(
            user_id=user_profile.id,
            property_id=property_id
        ).first()
        
        if existing_favorite:
            # Remove from favorites
            db.session.delete(existing_favorite)
            db.session.commit()
            return {"message": "Removed from favorites", "is_favorited": False}, 200
        else:
            # Add to favorites
            new_favorite = Favorite(
                user_id=user_profile.id,
                property_id=property_id
            )
            db.session.add(new_favorite)
            db.session.commit()
            return {"message": "Added to favorites", "is_favorited": True}, 200

class RecentActivitiesResource(Resource):
    @user_required()
    def get(self):
        current_user = get_jwt_identity()
        
        # Get optional limit parameter (default to 8 for home page, 0 for all)
        limit = request.args.get('limit', type=int, default=0)

        #Get user profile
        user_profile = UserProfile.query.filter_by(user_id=current_user).first()
        if not user_profile:
            return {"activities": []}, 200
        
        activities = []
      
        # Get recent property views (viewing/visiting a property)
        views_query = View.query.filter_by(user_id=current_user).order_by(View.created_at.desc())
        if limit > 0:
            views = views_query.limit(limit).all()
        else:
            views = views_query.all()
            
        for view in views:
            property = Property.query.get(view.property_id)
            if property:
                # Check the status to determine the type of view
                if view.status == "viewed":
                    # Pure property view - recorded when user visits property details
                    activities.append({
                        "type": "view",
                        "description": f"Viewed {property.title}",
                        "property": property.title,
                        "time": view.created_at.strftime("%Y-%m-%d %H:%M")
                    })
                elif view.status == "pending" or view.status == "completed":
                    # Scheduled viewing
                    activities.append({
                        "type": "viewing",
                        "description": f"Scheduled viewing for {view.sheduled_time.strftime('%Y-%m-%d %H:%M')}" if view.sheduled_time else "Property viewing",
                        "property": property.title,
                        "status": view.status,
                        "time": view.created_at.strftime("%Y-%m-%d %H:%M")
                    })

        # Get recent inquiries
        inquiries_query = Inquiry.query.filter_by(user_id=current_user).order_by(Inquiry.created_at.desc())
        if limit > 0:
            inquiries = inquiries_query.limit(limit).all()
        else:
            inquiries = inquiries_query.all()
            
        for inquiry in inquiries:
            property = Property.query.get(inquiry.property_id)
            if property:
                activities.append({
                    "type": "inquiry",
                    "description": inquiry.message[:50] + "..." if len(inquiry.message) > 50 else inquiry.message,
                    "property": property.title,
                    "time": inquiry.created_at.strftime("%Y-%m-%d %H:%M")
                })

        # Sort by time (most recent first)
        activities.sort(key=lambda x: x["time"], reverse=True)
        # Return only the limited number of most recent 
        if limit > 0:
            return {"activities": activities[:limit]}, 200
        return {"activities": activities}, 200


class RecordPropertyViewResource(Resource):
    @user_required()
    def post(self):
        """Record when a user views a property"""
        current_user_id = get_jwt_identity()
        
        # Get property_id from request
        data = request.get_json()
        property_id = data.get('property_id')
        
        if not property_id:
            return {"message": "Property ID is required"}, 400
        
        # Check if property exists
        property = Property.query.get(property_id)
        if not property:
            return {"message": "Property not found"}, 404
        
        # Check if user has already viewed this property recently (within last 24 hours)
        # to avoid duplicate entries
        from datetime import timedelta
        recent_view = View.query.filter(
            View.user_id == current_user_id,
            View.property_id == property_id,
            View.status == "viewed",
            View.created_at >= datetime.now() - timedelta(hours=24)
        ).first()
        
        if recent_view:
            # Update the existing view timestamp instead of creating a new one
            recent_view.created_at = datetime.now()
            db.session.commit()
            return {"message": "View timestamp updated"}, 200
        
        # Record the view (status None means it's just a view, not a scheduled viewing)
        new_view = View(
            property_id=property_id,
            user_id=current_user_id,
            sheduled_time=datetime.now(),  # Using current time as the view time
            status="viewed"  # Custom status for property views
        )
        db.session.add(new_view)
        db.session.commit()
        
        return {"message": "View recorded"}, 200


class CreateInquiryResource(Resource):
    @user_required()
    def post(self):
        """Create a new inquiry about a property"""
        current_user_id = get_jwt_identity()
        
        # Get data from request
        data = request.get_json()
        property_id = data.get('property_id')
        message = data.get('message')
        
        if not property_id:
            return {"message": "Property ID is required"}, 400
        
        if not message:
            return {"message": "Message is required"}, 400
        
        # Check if property exists
        property = Property.query.get(property_id)
        if not property:
            return {"message": "Property not found"}, 404
        
        # Get the agent who listed the property
        agent_profile = AgentProfile.query.get(property.agent_id)
        if not agent_profile:
            return {"message": "Agent not found for this property"}, 404
        
        # Create the inquiry
        new_inquiry = Inquiry(
            user_id=current_user_id,
            agent_id=agent_profile.id,
            property_id=property_id,
            message=message,
            status="new"
        )
        db.session.add(new_inquiry)
        db.session.commit()
        
        return {
            "message": "Inquiry sent successfully",
            "inquiry": new_inquiry.to_dict()
        }, 201


class UserInquiriesResource(Resource):
    @user_required()
    def get(self):
        """Get all inquiries sent by the current user"""
        current_user_id = get_jwt_identity()
        
        # Get optional limit parameter
        limit = request.args.get('limit', type=int, default=0)
        
        # Get all inquiries for this user, ordered by most recent
        inquiries_query = Inquiry.query.filter_by(user_id=current_user_id).order_by(Inquiry.created_at.desc())
        
        if limit > 0:
            inquiries = inquiries_query.limit(limit).all()
        else:
            inquiries = inquiries_query.all()
        
        result = []
        for inquiry in inquiries:
            inquiry_dict = inquiry.to_dict()
            
            # Get property info
            property = Property.query.get(inquiry.property_id)
            if property:
                inquiry_dict['property'] = {
                    'id': property.id,
                    'title': property.title,
                    'price': property.price,
                    'currency': property.currency
                }
                # Get primary image
                primary_image = PropertyImage.query.filter_by(property_id=property.id, is_primary=True).first()
                if primary_image:
                    inquiry_dict['property']['image'] = primary_image.image_url
            
            # Get agent info
            agent_profile = AgentProfile.query.get(inquiry.agent_id)
            if agent_profile:
                agent_user = User.query.get(agent_profile.agent_id)
                if agent_user:
                    inquiry_dict['agent'] = {
                        'id': agent_user.id,
                        'name': f"{agent_user.first_name} {agent_user.last_name}",
                        'email': agent_user.email,
                        'phone': agent_user.phone
                    }
            
            result.append(inquiry_dict)
        
        return {"inquiries": result}, 200


# ==================== MESSAGING RESOURCES ====================

class UserConversationsResource(Resource):
    @user_required()
    def get(self):
        """Get all conversations for the current user"""
        current_user_id = get_jwt_identity()
        
        # Get all conversations for this user, ordered by most recent
        conversations = Conversation.query.filter_by(
            user_id=current_user_id
        ).order_by(Conversation.last_message_at.desc()).all()
        
        result = []
        for conv in conversations:
            conv_dict = {
                'id': conv.id,
                'last_message': conv.last_message,
                'last_message_at': conv.last_message_at.strftime("%Y-%m-%d %H:%M") if conv.last_message_at else None,
                'created_at': conv.created_at.strftime("%Y-%m-%d %H:%M")
            }
            
            # Get agent info
            agent_profile = AgentProfile.query.get(conv.agent_id)
            if agent_profile:
                agent_user = User.query.get(agent_profile.agent_id)
                if agent_user:
                    conv_dict['agent'] = {
                        'id': agent_user.id,
                        'name': f"{agent_user.first_name} {agent_user.last_name}",
                        'email': agent_user.email,
                        'phone': agent_user.phone
                    }
            
            # Get property info if exists
            if conv.property_id:
                property = Property.query.get(conv.property_id)
                if property:
                    conv_dict['property'] = {
                        'id': property.id,
                        'title': property.title,
                        'price': property.price,
                        'currency': property.currency
                    }
                    # Get primary image
                    primary_image = PropertyImage.query.filter_by(property_id=property.id, is_primary=True).first()
                    if primary_image:
                        conv_dict['property']['image'] = primary_image.image_url
            
            # Get unread message count
            unread_count = Message.query.filter(
                Message.conversation_id == conv.id,
                Message.sender_type == "agent",
                Message.is_read == False
            ).count()
            conv_dict['unread_count'] = unread_count
            
            result.append(conv_dict)
        
        return {"conversations": result}, 200


class ConversationMessagesResource(Resource):
    @user_required()
    def get(self, conversation_id):
        """Get all messages in a conversation"""
        current_user_id = get_jwt_identity()
        
        # Verify the conversation belongs to this user
        conversation = Conversation.query.filter_by(
            id=conversation_id,
            user_id=current_user_id
        ).first()
        
        if not conversation:
            return {"message": "Conversation not found"}, 404
        
        # Get all messages in this conversation
        messages = Message.query.filter_by(
            conversation_id=conversation_id
        ).order_by(Message.created_at.asc()).all()
        
        # Mark messages as read
        for msg in messages:
            if msg.sender_type == "agent" and not msg.is_read:
                msg.is_read = True
        db.session.commit()
        
        result = []
        for msg in messages:
            msg_dict = {
                'id': msg.id,
                'content': msg.content,
                'sender_type': msg.sender_type,
                'is_read': msg.is_read,
                'created_at': msg.created_at.strftime("%Y-%m-%d %H:%M")
            }
            
            # Get sender info
            sender = User.query.get(msg.sender_id)
            if sender:
                msg_dict['sender'] = {
                    'id': sender.id,
                    'name': f"{sender.first_name} {sender.last_name}"
                }
            
            result.append(msg_dict)
        
        return {"messages": result}, 200
    
    @user_required()
    def post(self, conversation_id):
        """Send a message in a conversation"""
        current_user_id = get_jwt_identity()
        
        # Verify the conversation belongs to this user
        conversation = Conversation.query.filter_by(
            id=conversation_id,
            user_id=current_user_id
        ).first()
        
        if not conversation:
            return {"message": "Conversation not found"}, 404
        
        data = request.get_json()
        content = data.get('content')
        
        if not content:
            return {"message": "Message content is required"}, 400
        
        # Create the message
        new_message = Message(
            conversation_id=conversation_id,
            sender_id=current_user_id,
            sender_type="user",
            content=content,
            is_read=False
        )
        db.session.add(new_message)
        
        # Update conversation's last message
        conversation.last_message = content
        conversation.last_message_at = datetime.now()
        
        db.session.commit()
        
        return {
            "message": "Message sent successfully",
            "msg": {
                'id': new_message.id,
                'content': new_message.content,
                'sender_type': new_message.sender_type,
                'created_at': new_message.created_at.strftime("%Y-%m-%d %H:%M")
            }
        }, 201


class StartConversationResource(Resource):
    @user_required()
    def post(self):
        """Start a new conversation with an agent"""
        current_user_id = get_jwt_identity()
        
        data = request.get_json()
        agent_id = data.get('agent_id')
        property_id = data.get('property_id')
        initial_message = data.get('message')
        
        if not agent_id:
            return {"message": "Agent ID is required"}, 400
        
        if not initial_message:
            return {"message": "Initial message is required"}, 400
        
        # Check if conversation already exists
        existing_conv = Conversation.query.filter_by(
            user_id=current_user_id,
            agent_id=agent_id,
            property_id=property_id
        ).first()
        
        if existing_conv:
            # Add message to existing conversation
            new_message = Message(
                conversation_id=existing_conv.id,
                sender_id=current_user_id,
                sender_type="user",
                content=initial_message,
                is_read=False
            )
            db.session.add(new_message)
            existing_conv.last_message = initial_message
            existing_conv.last_message_at = datetime.now()
            db.session.commit()
            
            return {
                "message": "Message added to existing conversation",
                "conversation_id": existing_conv.id
            }, 200
        
        # Create new conversation
        new_conversation = Conversation(
            user_id=current_user_id,
            agent_id=agent_id,
            property_id=property_id,
            last_message=initial_message
        )
        db.session.add(new_conversation)
        db.session.flush()  # Get the new conversation ID
        
        # Create first message
        new_message = Message(
            conversation_id=new_conversation.id,
            sender_id=current_user_id,
            sender_type="user",
            content=initial_message,
            is_read=False
        )
        db.session.add(new_message)
        db.session.commit()
        
        return {
            "message": "Conversation started successfully",
            "conversation_id": new_conversation.id
        }, 201


# ==================== SCHEDULE VISIT RESOURCES ====================

class ScheduleVisitResource(Resource):
    @user_required()
    def post(self):
        """Schedule a property visit"""
        current_user_id = get_jwt_identity()
        
        data = request.get_json()
        property_id = data.get('property_id')
        date = data.get('date')
        time = data.get('time')
        message = data.get('message', '')
        
        if not property_id:
            return {"message": "Property ID is required"}, 400
        
        if not date:
            return {"message": "Date is required"}, 400
        
        if not time:
            return {"message": "Time is required"}, 400
        
        # Check if property exists
        property = Property.query.get(property_id)
        if not property:
            return {"message": "Property not found"}, 404
        
        # Combine date and time into a datetime
        from datetime import datetime
        try:
            scheduled_datetime = datetime.strptime(f"{date} {time}", "%Y-%m-%d %H:%M")
        except ValueError:
            return {"message": "Invalid date or time format"}, 400
        
        # Create the scheduled visit
        new_view = View(
            property_id=property_id,
            user_id=current_user_id,
            sheduled_time=scheduled_datetime,
            status="pending"
        )
        db.session.add(new_view)
        db.session.commit()
        
        return {
            "message": "Visit scheduled successfully",
            "visit": {
                'id': new_view.id,
                'property_id': property_id,
                'scheduled_time': new_view.sheduled_time.strftime("%Y-%m-%d %H:%M"),
                'status': new_view.status
            }
        }, 201


class UserScheduledVisitsResource(Resource):
    @user_required()
    def get(self):
        """Get all scheduled visits for the current user"""
        current_user_id = get_jwt_identity()
        
        # Get optional limit parameter
        limit = request.args.get('limit', type=int, default=0)
        
        # Get all scheduled visits (status = pending or completed) for this user
        visits_query = View.query.filter(
            View.user_id == current_user_id,
            View.status.in_(['pending', 'completed'])
        ).order_by(View.sheduled_time.asc())
        
        if limit > 0:
            visits = visits_query.limit(limit).all()
        else:
            visits = visits_query.all()
        
        result = []
        for visit in visits:
            visit_dict = {
                'id': visit.id,
                'scheduled_time': visit.sheduled_time.strftime("%Y-%m-%d %H:%M") if visit.sheduled_time else None,
                'status': visit.status,
                'created_at': visit.created_at.strftime("%Y-%m-%d %H:%M")
            }
            
            # Get property info
            property = Property.query.get(visit.property_id)
            if property:
                visit_dict['property'] = {
                    'id': property.id,
                    'title': property.title,
                    'price': property.price,
                    'currency': property.currency,
                    'listing_type': property.listing_type
                }
                # Get primary image
                primary_image = PropertyImage.query.filter_by(property_id=property.id, is_primary=True).first()
                if primary_image:
                    visit_dict['property']['image'] = primary_image.image_url
                
                # Get location
                prop_location = PropertyLocation.query.filter_by(property_id=property.id).first()
                if prop_location:
                    location = Location.query.get(prop_location.location_id)
                    if location:
                        visit_dict['property']['location'] = location.neighborhood or location.city
            
            result.append(visit_dict)
        
        return {"visits": result}, 200
            

