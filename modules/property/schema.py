from marshmallow import (
    Schema,
    ValidationError,
    fields,
    validate,
    validates,
    validates_schema,
)


class CreatePropertySchema(Schema):
    """
    Validation schema for creating a property.
    """

    title = fields.Str(
        required=True,
        validate=validate.Length(min=3, max=255),
    )

    description = fields.Str(
        allow_none=True,
    )

    property_type_id = fields.Int(
        required=True,
        strict=True,
    )

    price = fields.Int(
        required=True,
        strict=True,
    )

    currency = fields.Str(
        load_default="KES",
        validate=validate.Length(max=10),
    )

    bedrooms = fields.Int(
        allow_none=True,
    )

    bathrooms = fields.Int(
        allow_none=True,
    )

    area_size = fields.Int(
        allow_none=True,
    )

    area_unit = fields.Str(
        allow_none=True,
    )

    listing_type = fields.Str(
        required=True,
        validate=validate.OneOf(
            [
                "sale",
                "rent",
                "lease",
            ]
        ),
    )

    status = fields.Str(
        load_default="onsale",
        validate=validate.OneOf(
            [
                "onsale",
                "onrent",
                "lease",
            ]
        ),
    )

    city = fields.Str(
        allow_none=True,
    )

    neighborhood = fields.Str(
        allow_none=True,
    )

    county = fields.Str(
        allow_none=True,
    )

    latitude = fields.Float(
        allow_none=True,
    )

    longitude = fields.Float(
        allow_none=True,
    )

    @validates("price")
    def validate_price(self, value, **kwargs):
        if value <= 0:
            raise ValidationError(
                "Price must be greater than zero."
            )

    @validates("bedrooms")
    def validate_bedrooms(self, value, **kwargs):
        if value is not None and value < 0:
            raise ValidationError(
                "Bedrooms cannot be negative."
            )

    @validates("bathrooms")
    def validate_bathrooms(self, value, **kwargs):
        if value is not None and value < 0:
            raise ValidationError(
                "Bathrooms cannot be negative."
            )

    @validates("area_size")
    def validate_area_size(self, value, **kwargs):
        if value is not None and value <= 0:
            raise ValidationError(
                "Area size must be greater than zero."
            )

    @validates_schema
    def validate_location(self, data, **kwargs):
        latitude = data.get("latitude")
        longitude = data.get("longitude")

        if latitude is not None:
            if latitude < -90 or latitude > 90:
                raise ValidationError(
                    {
                        "latitude": [
                            "Latitude must be between -90 and 90."
                        ]
                    }
                )

        if longitude is not None:
            if longitude < -180 or longitude > 180:
                raise ValidationError(
                    {
                        "longitude": [
                            "Longitude must be between -180 and 180."
                        ]
                    }
                )


class UpdatePropertySchema(CreatePropertySchema):

        title = fields.Str(
        required=False,
        validate=validate.Length(min=3, max=255),
        )

        property_type_id = fields.Int(
        required=False,
        )

        price = fields.Int(
        required=False,
        )

        listing_type = fields.Str(
        required=False,
        validate=validate.OneOf(
            [
                "sale",
                "rent",
                "lease",
            ]
        ),
        )

        status = fields.Str(
            required=False,
            validate=validate.OneOf(
                [
                    "onsale",
                    "onrent",
                    "lease",
                ]
            ),
        )  

class ToggleFavoriteSchema(Schema):
    # validation schema for toggling a property
    property_id = fields.Int(
        required=True,
        strict=True,
    )

    @validates("property_id")
    def validate_property_id(self, value, **kwargs):
        if value is None:
            raise ValidationError(
                "Property ID is required."
            )
