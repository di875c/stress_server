import aiohttp_jinja2
import asyncio
from .utils import ISection


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



