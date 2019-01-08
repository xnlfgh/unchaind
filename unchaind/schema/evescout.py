from marshmallow import Schema, fields


class Region(Schema):
    id = fields.Int()
    name = fields.Str()


class WormholeType(Schema):
    id = fields.Int()
    name = fields.Str()
    src = fields.Str()
    dest = fields.Str()
    lifetime = fields.Int()
    jump_mass = fields.Int(data_key="jumpMass")
    max_mass = fields.Int(data_key="maxMass")


class SolarSystem(Schema):
    id = fields.Int()
    name = fields.Str()
    constellation_id = fields.Int(data_key="constellationID")
    security = fields.Float()
    region_id = fields.Int(data_key="regionId")
    region = fields.Nested(Region())


class Item(Schema):
    id = fields.Int(data_key="id")
    signature_id = fields.Str(data_key="signatureId")
    type = fields.Str(data_key="type")
    status = fields.Str(data_key="status")
    wormhole_mass = fields.Str(data_key="wormholeMass")
    wormhole_eol = fields.Str(data_key="wormholeEol")
    wormholeEstimatedEol = fields.DateTime()
    wormholeDestinationSignatureId = fields.Str()
    created_at = fields.DateTime(data_key="createdAt")
    created_by = fields.Str(data_key="createdBy")
    created_by_id = fields.Str(data_key="createdById")
    deleted_at = fields.DateTime(data_key="deletedAt", allow_none=True)
    deleted_by = fields.Str(data_key="deletedBy", allow_none=True)
    deleted_by_id = fields.Str(data_key="deletedById", allow_none=True)
    updated_at = fields.DateTime(data_key="updatedAt", allow_none=True)
    status_updated_at = fields.DateTime(
        data_key="statusUpdatedAt", allow_none=True
    )
    wormhole_source_wormhole_type_id = fields.Int(
        data_key="wormholeSourceWormholeTypeId"
    )
    wormhole_destination_wormhole_type_id = fields.Int(
        data_key="wormholeDestinationWormholeTypeId"
    )
    solar_system_id = fields.Int(data_key="solarSystemId")
    wormhole_destination_solar_system_id = fields.Int(
        data_key="wormholeDestinationSolarSystemId"
    )
    source_wormhole_type = fields.Nested(
        WormholeType(), data_key="sourceWormholeType"
    )
    destination_wormhole_type = fields.Nested(
        WormholeType(), data_key="destinationWormholeType"
    )
    source_solar_system = fields.Nested(
        SolarSystem(), data_key="sourceSolarSystem"
    )
    destination_solar_system = fields.Nested(
        SolarSystem(), data_key="destinationSolarSystem"
    )
