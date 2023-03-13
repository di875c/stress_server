from marshmallow import Schema, fields, post_load, pre_load, post_dump, ValidationError
from app.store.database import models
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema

REFERENCE_LST = ('uid', 'frame', 'stringer', 'side')


class CustomList(fields.List):
#To update serialize methods to return None instead []
    def _deserialize(self, value, attr, data, **kwargs) -> list:
        if len(super()._deserialize(value, attr, data, **kwargs)) == 0:
            return None
        else:
            return super()._deserialize(value, attr, data, **kwargs)

    def _serialize(self, value, attr, data, **kwargs) -> list:
        if len(super()._serialize(value, attr, data, **kwargs)) == 0:
            return None
        else:
            return super()._serialize(value, attr, data, **kwargs)


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


# class MaterialSchema(BaseSchema):
#     class Meta:
#         model = models.Material
#     properties = fields.List(fields.Nested("ElPropertySchema", only=("uid",)))


class NodeSchema(BaseSchema):
    class Meta:
        model = models.Node
        include_fk = True
        load_instance = False
        include_relationships = True
        ordered = True
    # elements = CustomList(fields.Nested("ElementSchema", only=("uid",)))


class ElementSchema(BaseSchema):
    class Meta:
        model = models.Element
        include_fk = True
        load_instance = False
        include_relationships = True
        ordered = True
    # nodes = CustomList(fields.Nested(lambda: NodeSchema(only=REFERENCE_LST)))
    position = fields.Nested("NodeSchema", only=REFERENCE_LST[1:])
    offset_1 = fields.String()
    offset_2 = fields.String()



# class NodeElementSchema(Schema):
# class NodeElementSchema(BaseSchema):
#     __model__ = models.NodeElement
#     node = fields.Integer()
#     element = fields.Integer()


class ElPropertySchema(BaseSchema):
    class Meta:
        model = models.ElProperty
        include_fk = True
        load_instance = False
        include_relationships = True
        ordered = True
    material = fields.Nested(model_schema_factory(models.Material), only=("uid",))
    property_start = fields.Nested(model_schema_factory(models.SectionProperty), only=['area', 'inertia_xx', 'inertia_yy', 'inertia_xy', 'inertia_torsion'])
    property_end = fields.Nested(model_schema_factory(models.SectionProperty), only=['area', 'inertia_xx', 'inertia_yy', 'inertia_xy', 'inertia_torsion'])

