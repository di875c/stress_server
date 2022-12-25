from marshmallow import Schema, fields, post_load, pre_load, post_dump, ValidationError
from app.store.database import models


class BaseSchema(Schema):
    # Custom options
    __envelope__ = {'single': 'parameter', 'many': 'parameters'}
    __model__ = None

    def get_envelope_key(self, many):
        """Helper to get the envelope key."""
        key = self.__envelope__["many"] if many else self.__envelope__["single"]
        assert key is not None, "Envelope key undefined"
        return key

    @pre_load(pass_many=True)
    def unwrap_envelope(self, data, many, **kwargs):
        key = self.get_envelope_key(many)
        return data[key]

    @post_dump(pass_many=True)
    def wrap_with_envelope(self, data, many, **kwargs):
        key = self.get_envelope_key(many)
        return {key: data}

    @post_load
    def make_object(self, data, **kwargs):
        return self.__model__(**data)


class BaseSchema_add(BaseSchema):
    comment = fields.Str()
    id = fields.Integer()


class BaseCOG(Schema):
    cog_x = fields.Float()
    cog_y = fields.Float()
    cog_z = fields.Float()


class BaseStructureSchema(BaseSchema):
    __model__ = models.BaseStructure
    # name = fields.Str(validate=["Frame", "Stringer", "Rib"])
    name = fields.Str()


class StructureSchema(BaseSchema_add):
    __model__ = models.Structure
    struct_type = fields.Str()
    number = fields.Float()
    side = fields.Str()


class SectionPropertySchema(BaseSchema_add, BaseCOG):
    __model__ = models.SectionProperty
    name = fields.Str()
    area = fields.Float()
    inertia_xx = fields.Float()
    inertia_yy = fields.Float()
    inertia_zz = fields.Float()
    reference_type = fields.Str()
    reference_number = fields.Float()


class MaterialSchema(BaseSchema_add):
    __model__ = models.Material
    name_id = fields.Integer()
    density = fields.Float()
    eu = fields.Float()
    nu = fields.Float()
    reference_type = fields.Str()
    reference_number = fields.Float()


class MassSchema(BaseSchema_add, BaseCOG):
    __model__ = models.Mass
    name = fields.Str()
    reference_type = fields.Str()
    reference_number = fields.Float()
    weight = fields.Float()


class NodeSchema(BaseSchema_add, BaseCOG):
    __model__ = models.Node
    name_id = fields.Integer()
    reference_type1 = fields.Str()
    reference_number1 = fields.Float()
    reference_type2 = fields.Str()
    reference_number2 = fields.Float()
    reference_side = fields.Str()