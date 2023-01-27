from marshmallow import Schema, fields, post_load, pre_load, post_dump, ValidationError
from app.store.database import models
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema

class BaseSchema(SQLAlchemyAutoSchema):
    # Custom options
    __envelope__ = {'single': 'parameter', 'many': 'parameters'}
    # __model__ = None
    class Meta:
        model = None
        include_relationships = True
        load_instance = False
        include_fk = True

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
        return self.Meta.model(**data)


def model_schema_factory(bd_model):
    class ModelSchema(BaseSchema):
        class Meta:
            model = bd_model
            include_fk = True
            load_instance = False
            include_relationships = True
            ordered = True
    return ModelSchema




# class BaseSchemaAdd(BaseSchema):
#     class Meta:
#         ordered = True
#
#     id = fields.Integer()
#     time_created = fields.DateTime('%Y-%m-%d  %H:%M:%S')
#     time_updated = fields.DateTime('%Y-%m-%d  %H:%M:%S')
#     comment = fields.Str()
#
# class BaseSchemaAdd(BaseSchema):
#     class Meta:
#         ordered = True
#
#
# class BaseCOG(Schema):
#     cog_x = fields.Float()
#     cog_y = fields.Float()
#     cog_z = fields.Float()
#
#
# class BaseStructureSchema(BaseSchema):
#     # __model__ = models.BaseStructure
#     class Meta:
#         model = models.BaseStructure
#         include_relationships = True
#
#
# class StructureSchema(BaseSchema):
#     # __model__ = models.Structure
#     # struct_type = fields.Str()
#     # number = fields.Float()
#     # side = fields.Str()
#     class Meta:
#         model = models.Structure
#         include_fk = True
#         load_instance = False
#         include_relationships = True
#
# # class SectionPropertySchema(BaseSchemaAdd, BaseCOG):
# class SectionPropertySchema(BaseSchema):
#     # __model__ = models.SectionProperty
#     # id = fields.Str()
#     # area = fields.Float()
#     # inertia_xx = fields.Float()
#     # inertia_yy = fields.Float()
#     # inertia_zz = fields.Float()
#     # reference_type = fields.Str()
#     # reference_number = fields.Float()
#     # side = fields.Str()
#     # position_type = fields.Str()
#     # position_number = fields.Float()
#     # position_side = fields.Str()
#     class Meta:
#         model = models.SectionProperty
#         include_fk = True
#         load_instance = False

class MaterialSchema(BaseSchema):
    class Meta:
        model = models.Material
    # density = fields.Float()
    # eu = fields.Float()
    # nu = fields.Float()
    properties = fields.List(fields.Nested("ElPropertySchema", exclude=("material",)))

#
# class MassSchema(BaseSchemaAdd, BaseCOG):
#     __model__ = models.Mass
#     name = fields.Str()
#     reference_type = fields.Str()
#     reference_number = fields.Float()
#     weight = fields.Float()


# class NodeSchema(BaseSchema_add1, BaseCOG):
class NodeSchema(BaseSchema):
    class Meta:
        model = models.Node
    # reference_type1 = fields.Str()
    # reference_number1 = fields.Float()
    # reference_side1 = fields.Str()
    # reference_type2 = fields.Str()
    # reference_number2 = fields.Float()
    # reference_side2 = fields.Str()
    elements = fields.List(fields.Nested("ElementSchema", only=("id",)))


# class ElementSchema(BaseSchema_add1):
class ElementSchema(BaseSchema):
    class Meta:
        model = models.Element
    # element_type = fields.Str()
    nodes = fields.List(fields.Nested(lambda: NodeSchema(only=("id",))))
    # property_id = fields.Integer()
    # offset = fields.Str()
    # # node_start = fields.Integer()
    # # node_end = fields.Integer()
    # property_start = fields.Integer()
    # property_end = fields.Integer()


# class NodeElementSchema(Schema):
# class NodeElementSchema(BaseSchema):
#     __model__ = models.NodeElement
#     node = fields.Integer()
#     element = fields.Integer()


class ElPropertySchema(BaseSchema):
    class Meta:
        model = models.ElProperty
    # cross_section = fields.Integer()
    # shell_thick = fields.Float()
    # material_id = fields.Integer()
    material = fields.Nested(MaterialSchema(exclude=("properties",)))
    section = fields.Nested('SectionPropertySchema')
