import aiohttp_jinja2
import asyncio
from .utils import ISection
from app.store.database.models import Session, Structure, SectionProperty, Material, BaseStructure, Mass, Node
from app.store.database.mod_interface import (BaseStructureSchema, StructureSchema, SectionPropertySchema,
                                              MaterialSchema, ValidationError, MassSchema, NodeSchema)
from aiohttp import web
from sqlalchemy.future import select
from sqlalchemy.orm import aliased
import json
from sqlalchemy.exc import SQLAlchemyError

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


@aiohttp_jinja2.template("index1.html")
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
        return {'title': f"cross-section =  {section.area}\n cog = {section.cog}\n, inertia= {section.inertia}"}
    except:
        return {'title': 'something wrong'}


class DbView(web.View):
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
                schema = globals()[class_name]()
                model = globals()[class_name.replace('Schema', '')]
                for _key, _val in data.items():
                    if _key != 'table_name':
                        _sign, _value = _val.split()
                        modify_data[_key] = _value
                        modify_sign[_key] = _sign
                data = schema.dump(modify_data) #serialize data to model format
                # using CHECK_OPERATOR as dict with lambda function as comparisson opearator
                model_objects = await session.execute(select(model).where(
                    *[CHECK_OPERATOR[modify_sign[_key]](getattr(model, _key), _val) for _key, _val in
                    data['parameter'].items()]))
                # deserialize data to dict format
                out_data = schema.dump(model_objects.scalars(), many=True)
        return web.Response(body=json.dumps(out_data))
        # return web.Response(body=b"good")

    async def post(self):
        """
        parameters are taken from json post request except table_name. It is taken from url
        :param request: db?table_name=StructureSchema&struct_type=== Stringer&name==< 6
        :return: add objects to database, accept or mistake as response
        """
        try:
            # print(data)
            class_name = self.request.rel_url.query['table_name']
            print(class_name)
            async with Session() as session:
                async with session.begin():
                    data = await self.request.json()
                    print(type(data), data)
                    if 'parameter' in data.keys():
                        schema = globals()[class_name]()
                        print('ja tut', schema)
                        model_object = schema.load(data)
                        session.add(model_object)
                    elif 'parameters' in data.keys():
                        schema = globals()[class_name](many=True)
                        print(schema)
                        model_objects = schema.load(data)
                        # print(model_objects)
                        session.add_all(model_objects)
                    else:
                        return web.Response(body=b"Wrong format no parameter or parameters in json")
            return web.Response(body=b"Successfully added to DB")
        except SQLAlchemyError as e:
            error = str(e.__dict__['orig'])
            return web.Response(body="Error appears\n {}".format(error))
        except ValidationError as e:
            error = str(e.messages)
            return web.Response(body="Error appears\n {}".format(error))

