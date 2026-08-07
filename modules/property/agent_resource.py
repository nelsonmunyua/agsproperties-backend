from flask import request
from flask_restful import Resource
from flask_jwt_extended import verify_jwt_in_request
from auth.current_user import CurrentUserService
from modules.property.schema import CreatePropertySchema, UpdatePropertySchema
from modules.property.serializer import PropertySerializer
from modules.property.service import PropertyService
from shared.responses import ApiResponse


class AgentPropertyCollectionResource(Resource):
    """
    CRUD collection for the current agent's own properties.
    Serves: GET /agent/properties, POST /agent/properties/create
    """

    def get(self):
        """
        Return the current agent's properties with view counts.
        Response shape matches the frontend `{ properties: [...] }` contract.
        """
        verify_jwt_in_request()
        actor = CurrentUserService.get()

        limit = request.args.get("limit", type=int, default=100)

        properties = PropertyService.get_agent_properties(actor, limit=limit)

        view_counts = {}
        for prop in properties:
            view_counts[prop.id] = PropertyService.count_views(prop.id)

        return ApiResponse.success(
            data={
                "properties": PropertySerializer.agent_collection(
                    properties,
                    view_counts=view_counts,
                )
            }
        )

    def post(self):
        """
        Create a property on behalf of the current agent.
        """
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
            message="Property created successfully.",
        )


class AgentPropertyResource(Resource):
    """
    Detail/update/delete a single property owned by the current agent.
    Serves: GET /agent/properties/<id>, PUT /agent/properties/<id>/edit,
            DELETE /agent/properties/<id>/delete
    """

    def get(self, property_id):
        verify_jwt_in_request()
        actor = CurrentUserService.get()

        property = PropertyService.get_property(property_id)

        views = PropertyService.count_views(property_id)

        return ApiResponse.success(
            data={
                "property": PropertySerializer.detail(property),
                "images": [
                    PropertySerializer.image(image)
                    for image in property.images
                ],
                "videos": [
                    PropertySerializer.video(video)
                    for video in property.videos
                ],
                "location": PropertySerializer.location(property),
                "views": views,
            }
        )

    def put(self, property_id):
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
            message="Property updated successfully.",
        )

    def patch(self, property_id):
        # Alias PUT for PATCH clients.
        return self.put(property_id)

    def delete(self, property_id):
        verify_jwt_in_request()
        actor = CurrentUserService.get()

        PropertyService.delete_property(actor, property_id)

        return ApiResponse.deleted(
            message="Property deleted successfully."
        )
