import aiohttp_jinja2
import asyncio
from .utils import ISection
from app.store.database.models import *
from app.store.database.mod_interface import *
from aiohttp import web
from sqlalchemy.future import select
from sqlalchemy.orm import aliased
import json, sys
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import update, bindparam, delete

CHECK_OPERATOR = {
    '<': lambda x, y: x < y,
    '>': lambda x, y: x > y,
    '==': lambda x, y: x == y,
    '=<': lambda x, y: x <= y,
    '=>': lambda x, y: x >= y,
}

@aiohttp_jinja2.template("index.html")
async def index(request):
    return {'title': 'пишем первое приложение на aio http'}


def error_function(func):
    async def _wrapper(*args, **kwargs):
        try:
            result = await func(*args, **kwargs)
        except SQLAlchemyError as e:
            error = str(e.__dict__['orig'])
            return web.Response(status=502, body="SQL error appears\n {}".format(error))
        except ValidationError as e:
            error = str(e.messages)
            return web.Response(status=422, body="Server validation error appears\n {}".format(error))
        except ConnectionRefusedError as e:
            error = str(e.strerror)
            return web.Response(status=502, body="Connection to BD error appears\n {}".format(error))
        return result
    return _wrapper


# @aiohttp_jinja2.template("index1.html")
async def section_analysis(request):
    """
    calculate cross-section a*b with time delay = time
    :param request: cross_section?sec_type=ISection&w1=4&h=8&w2=6&t1=2&t2=1&t3=3&x=0&y=0&alpha=0&time=0
    :return:
    """
    parameters = request.rel_url.query
    await asyncio.sleep(int(parameters['time']))
    try:
        # print(parameters)
        class_name = parameters['sec_type']
        input_data = [float(_val) for _key, _val in parameters.items() if _key not in ('sec_type', 'time')]
        # print(input_data)
        section = globals()[class_name](*input_data)
        # return {'title': f"cross-section =  {section.area}\n cog = {section.cog}\n, inertia= {section.inertia}"}
        return web.Response(body=f"cross-section area =  {section.area}\n cog = {section.cog}\n, inertia= {section.inertia}")
    except ValidationError as e:
        error = str(e.messages)
        return web.Response(body="Error appears\n {}".format(error))


class DbView(web.View):
    @error_function
    async def get(self):
        """
        parameters are taken from url get request
        :param request: db?table_name=StructureSchema&struct_type=== Stringer&name==< 6
        :return: json with lines from table according to request
        """
        data = dict(self.request.rel_url.query)
        class_name = data['table_name']
        # print(data)
        modify_data, modify_sign = {}, {}
        async with Session() as session:
            async with session.begin():
                model = globals()[class_name.replace('Schema', '')]
                # schema = globals()[class_name]()
                schema = model_schema_factory(model)() if model != Element else ElementSchema()
                print(schema)
                for _key, _val in data.items():
                    if _key != 'table_name':
                        _sign, _value = _val.split()
                        modify_data[_key] = _value
                        modify_sign[_key] = _sign
                data = schema.dump(modify_data) #serialize data to model format
                # using CHECK_OPERATOR as dict with lambda function as comparisson opearator
                # if class_name != "ElementSchema" and class_name != "NodeSchema":
                model_objects = await session.execute(select(model).where(
                    *[CHECK_OPERATOR[modify_sign[_key]](getattr(model, _key), _val) for _key, _val in
                    data['parameter'].items()]))
                # else:
                    # model_objects = await session.execute(select(model).where(
                    # *[CHECK_OPERATOR[modify_sign[_key]](getattr(model, _key), _val) for _key, _val in
                    #   data.items()]))
                # deserialize data to dict format
                out_data = schema.dump(model_objects.scalars(), many=True)
                print('size of json attached: ', sys.getsizeof(out_data))
        return web.Response(body=json.dumps(out_data))

    @error_function
    async def post(self):
        """
        parameters are taken from json post request except table_name. It is taken from url
        :param request: db?table_name=StructureSchema&struct_type=== Stringer&name==< 6
        :return: add objects to database, accept or mistake as response
        """
        # try:
        # print(data)
        class_name = self.request.rel_url.query['table_name']
        # print(class_name)
        async with Session() as session:
            async with session.begin():
                data = await self.request.json()
                # print(type(data), data)
                if 'parameter' in data.keys():
                    model = globals()[class_name.replace('Schema', '')]
                    # schema = globals()[class_name]()
                    schema = model_schema_factory(model)()
                    # print('ja tut', schema)
                    model_object = schema.load(data)
                    session.add(model_object)
                elif 'parameters' in data.keys():
                    # schema = globals()[class_name](many=True)
                    model = globals()[class_name.replace('Schema', '')]
                    schema = model_schema_factory(model)(many=True)
                    print(schema, model)# data)
                    model_objects = schema.load(data)
                    # print(model_objects)
                    session.add_all(model_objects)
                else:
                    return web.Response(status=422, body=b"Wrong format no parameter or parameters in json")
        return web.Response(body=b"Successfully added to DB")

    @error_function
    async def put(self):
        """
        parameters are taken from json post request except table_name. It is taken from url
        :param request: db?table_name=NodeSchema
        json = {{"parameters":
             [
{"uid": 16405200.0, "cog_x": 450.326, "cog_y": -34.631, "cog_z": 308.7845, "comment": "comments"},
{"uid": 16404200.0, "cog_x": 450.326, "cog_y": -26.162, "cog_z": 311.1053, "comment": "comments"},
              ]}
        :return: add objects to database, accept or mistake as response
        """
        # try:
        # print(data)
        class_name = self.request.rel_url.query['table_name']
        # print(class_name)
        async with Session() as session:
            async with session.begin():
                data = await self.request.json()
                model = globals()[class_name.replace('Schema', '')]
                # print(type(data), data)
                if 'parameters' in data.keys():
                    stmt = (update(model).where(model.id == bindparam("uid")).values(
                        {name: bindparam(name) for name in data['parameters'][0].keys() if name != "uid"})
                    )
                    result = await session.execute(stmt, data['parameters'])
                else:
                    return web.Response(body=b"Wrong format no parameter or parameters in json")
        return web.Response(body="Successfully updated {}".format(result.rowcount))
        # except SQLAlchemyError as e:
        #     error = str(e.__dict__['orig'])
        #     return web.Response(body="SQL error appears\n {}".format(error))
        # except ValidationError as e:
        #     error = str(e.messages)
        #     return web.Response(body="Validation error appears\n {}".format(error))

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
        async with Session() as session:
            async with session.begin():
                data = await self.request.json()
                model = globals()[class_name.replace('Schema', '')]
                # print(type(data), data)
                if 'parameters' in data.keys():
                    stmt = (delete(model).where(model.id == bindparam("uid")))
                    result = await session.execute(stmt, data['parameters'])
                else:
                    return web.Response(body=b"Wrong format no parameter or parameters in json")
        return web.Response(body="Successfully updated {}".format(result.supports_sane_multi_rowcount))
        # except SQLAlchemyError as e:
        #     error = str(e.__dict__['orig'])
        #     return web.Response(body="SQL error appears\n {}".format(error))
        # except ValidationError as e:
        #     error = str(e.messages)
        #     return web.Response(body="Validation error appears\n {}".format(error))
