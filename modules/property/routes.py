from modules.property.resource import (
    PropertyCollectionResource,
    PropertyResource,
    SavedPropertiesResource,
    TogglePropertyResource  
)


def register_property_routes(api):

    api.add_resource( PropertyCollectionResource, "/properties")
    api.add_resource( PropertyResource, "/properties/<int:property_id>")
    api.add_resource( SavedPropertiesResource, "/saved-properties")
    api.add_resource( TogglePropertyResource, "/favorite")

