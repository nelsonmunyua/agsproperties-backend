from flask import request
from flask_restful import Resource
from marshmallow import ValidationError
from flask_jwt_extended import verify_jwt_in_request, current_user, jwt_required
from auth.current_user import CurrentUserService
from modules.property.schema import ( CreatePropertySchema, UpdatePropertySchema, ToggleFavoriteSchema)
from modules.property.serializer import PropertySerializer
from modules.property.service import PropertyService
from shared.responses import ApiResponse
from modules.user.service import UserService


class PropertyCollectionResource(Resource):

    def get(self):
        """
        Public property listing.
        """

        filters = {
            "search": request.args.get("search"),
            "listing_type": request.args.get("listing_type"),
            "status": request.args.get("status"),
            "property_type": request.args.get("property_type"),
            "city": request.args.get("city"),
            "bedrooms": request.args.get("bedrooms", type=int),
            "bathrooms": request.args.get("bathrooms", type=int),
            "min_price": request.args.get("min_price", type=int),
            "max_price": request.args.get("max_price", type=int),
            "page": request.args.get("page", default=1, type=int),
            "per_page": request.args.get("per_page", default=12, type=int),
        }

        properties = PropertyService.list_properties(filters)

        return ApiResponse.success(
            data=PropertySerializer.collection(properties)
        )

    def post(self):

        verify_jwt_in_request()

        actor = CurrentUserService.get()

        schema = CreatePropertySchema()

        data = schema.load(request.form)

        property = PropertyService.create_property(
            actor=actor,
            data=data,
            images=request.files.getlist("images"),
            videos=request.files.getlist("videos"),
            location=data,
        )

        return ApiResponse.created(
            data=PropertySerializer.detail(property),
            message="Property created successfully."
        )

class PropertyResource(Resource):

    def get(self, property_id):

        property = PropertyService.get_property(
            property_id
        )

        return ApiResponse.success(
            PropertySerializer.detail(property)
        )

    def patch(self, property_id):
        verify_jwt_in_request()

        actor = CurrentUserService.get()
        schema = UpdatePropertySchema()
        data = schema.load(request.form)

        property = PropertyService.update_property(
            actor=actor,
            property_id=property_id,
            data=data,
            images=request.files.getlist("images"),
            videos=request.files.getlist("videos"),
            location=data,
            )

        return ApiResponse.success(
                data=PropertySerializer.detail(property),
                message="Property updated successfully."
            )    

         

    def delete(self, property_id):
        verify_jwt_in_request()

        actor = CurrentUserService.get()

        PropertyService.delete_property(
            actor,
            property_id,
        )

        return ApiResponse.deleted(
            message="Property deleted successfully."
        )  

class SavedPropertiesResource(Resource):

    def get(self):
        actor = CurrentUserService.get()

        # Extract HTTP arguments
        limit = request.args.get('limit', type=int, default=0)

        properties = PropertyService.get_saved_properties(
            actor,
            limit=limit
        ) 
        return ApiResponse.success(
            PropertySerializer.collection(properties)
        )
class TogglePropertyResource(Resource):

    def post(self):

        actor = CurrentUserService.get()
        schema = ToggleFavoriteSchema()
        data = schema.load(request.get_json())

        property_id = data["property_id"]
        is_favorited = PropertyService.toggle_favorite(actor, property_id)

        return ApiResponse.success(
            data = {"is_favorited": is_favorited, "property_id": property_id}
        )


        

        
                  