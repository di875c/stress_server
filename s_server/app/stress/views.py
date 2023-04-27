#import aiohttp_jinja2
import asyncio
from app.store.database import models
from app.store.database import mod_interface
from aiohttp import web
from sqlalchemy.future import select
import json, sys
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import update, bindparam, delete

CHECK_OPERATOR = {
    '<': lambda x, y: x < y,
    '>': lambda x, y: x > y,
    '==': lambda x, y: x == y,
    '<=': lambda x, y: x <= y,
    '>=': lambda x, y: x >= y,
    'between': lambda x, y: (y[0] <= x, x <= y[1]),
}


def recur_unpack(lst: list, return_lst=None) -> list:
    # prepare list with unpacked internal lists [[1,2,3],4,[[5,6],7]] --> [1,2,3,4,5,6,7]
    return_lst = list() if not return_lst else return_lst
    for _val in lst:
        if type(_val) == list or type(_val) == tuple:
            return_lst = recur_unpack(_val, return_lst)
        else:
            return_lst.append(_val)
    return return_lst


def extract_nested_parameters(base_schema: mod_interface.SQLAlchemyAutoSchema):
    for field in base_schema.fields:
        if 'nested' in base_schema.fields[field].__dict__:
            current_schema = base_schema.fields[field].schema
            ref_model = current_schema.Meta.model
            return field, current_schema, ref_model
    raise mod_interface.ValidationError(message=f'No relation model exists')


def prepare_criteria_from_html(data: dict) -> tuple:
    # take dict from request.parameters and preparing list of condition for orm request to DB
    class_name = data['table_name']
    modify_data, modify_sign, ref_keys, ref_field_st = {}, {}, {}, set()
    model = models.__dict__[class_name]
    base_schema = mod_interface.__dict__[class_name + 'Schema']() if class_name + 'Schema' in mod_interface.__dict__  \
        else mod_interface.model_schema_factory(model)()
    for _key, _val in data.items():
        if _key != 'table_name':
            _sign, *_value = _val.split()
            current_schema = base_schema
            current_model = model
            if _key not in base_schema.fields:
                ref_field, current_schema, current_model = extract_nested_parameters(current_schema)
                ref_field_st.add(getattr(model, ref_field)) # this set with reference field will be used in join request
            if _sign.lower() == 'between':
                modify_data.update({_key: [current_schema.dump({_key: _x})['parameter'][_key] for _x in _value]})
                modify_sign[_key] = (_sign.lower(), current_model)
            else:
                modify_sign[_key] = (_sign.lower(), current_model)
                modify_data.update(current_schema.dump({_key: _value[0]})['parameter'])
    return (recur_unpack([CHECK_OPERATOR[modify_sign[_key][0]](getattr(modify_sign[_key][1], _key), _val)
                          for _key, _val in modify_data.items()]), model, base_schema, ref_field_st)


# @aiohttp_jinja2.template("index1.html")
async def index(request):
    return web.Response(body= b"Server for data store after construction sizing aio http. Url has to started from \
db?table_name=<table_name>&<parameters>. get, post, put, del allowed for DB interaction")


def error_function(func):
    # error wrapper, send response with error information.
    async def _wrapper(*args, **kwargs):
        try:
            if isinstance(args[0], DbView):
                model_name = args[0]._request.rel_url.query.get('table_name', None)
                # print(model_name)
                if not model_name or model_name not in models.__dict__:
                    return web.Response(body=f"There is no table in Database with name {model_name}", status=502)
            result = await func(*args, **kwargs)
        except SQLAlchemyError as e:
            error = str(e.__dict__['orig'])
            return web.Response(status=502, body="SQL error appears\n {}".format(error))
        except mod_interface.ValidationError as e:
            error = str(e.messages)
            return web.Response(status=422, body="Server validation error appears\n {}".format(error))
        except ConnectionRefusedError as e:
            error = str(e.strerror)
            return web.Response(status=502, body="Connection to Database error appears\n {}".format(error))
        except ValueError as e:
            return web.Response(status=502, body="Data format mistake.\n {}".format(e))
        except Exception as error:
            return web.Response(body='some new error. {}'.format(error), status=422)
        return result
    return _wrapper


class DbView(web.View):
    @error_function
    async def get(self):
        """
        parameters are taken from url get request
        :param request: db?table_name=Structure&struct_type=== Stringer&name==< 6
        :return: json with lines from table according to request
        """
        data = dict(self.request.rel_url.query)
        async with models.Session() as session:
            async with session.begin():
                criteria_list, model, schema, ref_fields = prepare_criteria_from_html(data)
                model_objects = await session.execute(select(model).where(*criteria_list)) if len(ref_fields) == 0 else\
                    await session.execute(select(model).outerjoin(*ref_fields).where(*criteria_list))
                # print(schema.dump(model_objects.scalars(), many=True))
                print(schema)
                out_data = schema.dump(model_objects.scalars(), many=True)
                print('size of json attached: ', sys.getsizeof(out_data))
        return web.Response(body=json.dumps(out_data))

    @error_function
    async def post(self):
        """
        parameters are taken from json post request except table_name. It is taken from url
        :param request: db?table_name=Structure&struct_type=== Stringer&name==< 6
        :return: add objects to database, accept or mistake as response
        """
        data_from_url = dict(self.request.rel_url.query)
        class_name = data_from_url.pop('table_name')
        async with models.Session() as session:
            async with session.begin():
                model = models.__dict__[class_name]
                if 'Content-Type' in self.request.headers and self.request.headers['Content-Type'] == 'application/json':
                    schema = mod_interface.__dict__[class_name + 'Schema'](many=True) if class_name + 'Schema' in \
                                    mod_interface.__dict__ else mod_interface.model_schema_factory(model)(many=True)
                    data = await self.request.json()
                    # print(data)
                    model_objects = schema.load(data)
                    result = session.add_all(model_objects)
                else:
                    schema = mod_interface.__dict__[class_name + 'Schema'](many=False) if class_name + 'Schema' \
                            in mod_interface.__dict__ else mod_interface.model_schema_factory(model)(many=False)
                    model_object = schema.load({'parameter': data_from_url})
                    session.add(model_object)
        return web.Response(body=b"Successfully added to DB")

    @error_function
    async def put(self):
        """
        parameters are taken from json post request except table_name. It is taken from url
        :param request: db?table_name=Node
        json = {{"parameters":
             [
{"uid": 16405200.0, "cog_x": 450.326, "cog_y": -34.631, "cog_z": 308.7845, "comment": "comments"},
{"uid": 16404200.0, "cog_x": 450.326, "cog_y": -26.162, "cog_z": 311.1053, "comment": "comments"},
              ]}
        :return: add objects to database, accept or mistake as response
        """
        data_from_url = dict(self.request.rel_url.query)
        # print(data_from_url)
        class_name = data_from_url.pop('table_name')
        # print(class_name)
        async with models.Session() as session:
            async with session.begin():
                # data = await self.request.json()
                model = models.__dict__[class_name]
                if 'Content-Type' in self.request.headers and self.request.headers['Content-Type'] == 'application/json':
                    schema = mod_interface.__dict__[class_name + 'Schema'](many=True) if class_name + 'Schema' in \
                        mod_interface.__dict__ else mod_interface.model_schema_factory(model)(many=True)
                    data = await self.request.json()
                    ser_data = [*schema.dump(*data.values()).values()][0]
                else:
                    schema = mod_interface.__dict__[class_name + 'Schema'](many=False) if class_name + 'Schema' in \
                            mod_interface.__dict__ else mod_interface.model_schema_factory(model)(many=False)
                    ser_data = [*schema.dump(data_from_url).values()]
                # print(ser_data)
                for _item in ser_data:
                    _item['b_uid'] = _item.pop('uid')
                stmt = (update(model).where(model.uid == bindparam("b_uid")).values(
                    {name: bindparam(name) for name in ser_data[0].keys() if name != "b_uid"})
                )
                result = await session.execute(stmt, ser_data)
                # else:
                #     return web.Response(body=b"Wrong format no parameter or parameters in json", status=422)
        return web.Response(body="Successfully updated table {}".format(model.__tablename__))

    @error_function
    async def delete(self):
        """
                parameters are taken from json post request except table_name. It is taken from url
                :param request: db?table_name=NodeSchema
                json = {{"parameters":
                     [
        {"uid": 16405200.0},
        {"uid": 16404200.0},
                      ]}
                :return: delete objects from database, accept or mistake as response
                """
        # try:
        data = dict(self.request.rel_url.query)
        class_name = data['table_name']
        # print(data)
        async with models.Session() as session:
            async with session.begin():
                model = models.__dict__[class_name]
                if 'Content-Type' in  self.request.headers and self.request.headers['Content-Type'] == 'application/json':
                    # If delete method with excel using. Only uid index is taken into account.
                    schema = mod_interface.__dict__[class_name + 'Schema'](many=True, only=('uid',)) \
                        if class_name + 'Schema' in mod_interface.__dict__ else \
                        mod_interface.model_schema_factory(model + 'Schema')(many=True, only=('uid',))
                    data = await self.request.json()
                    ser_data = schema.dump(data['parameters'])
                    # print(ser_data)
                    if 'parameters' in data.keys():
                        stmt = (delete(model).where(model.uid == bindparam("uid")).returning(model.uid))
                        # query = await session.execute(select(model.uid).where(*[model.uid == _data['uid'] for _data in ser_data['parameters']]))
                        result = await session.execute(stmt, ser_data['parameters'])
                        # print(query.scalar())
                    else:
                        return web.Response(body=b"Wrong format no parameter or parameters in json")
                else:
                    # Parameters are from web interface. Selection with get principle.
                    print(data, '\n', prepare_criteria_from_html(data))
                    criteria_list, model, schema, ref_fields = prepare_criteria_from_html(data)
                    result = await session.execute(delete(model).where(*criteria_list))
        return web.Response(body="Successfully deleted {}".format(result.supports_sane_multi_rowcount()))

