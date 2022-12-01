import aiohttp_jinja2
import asyncio

@aiohttp_jinja2.template("index.html")
async def index(request):
    return {'title': 'пишем первое приложение на aio http'}

@aiohttp_jinja2.template("index1.html")
async def section_analysis(request):
    """
    calculate cross-section a*b with time delay = time
    :param request: ?a=20&b=20&time=2
    :return:
    """
    parameters = request.rel_url.query
    await asyncio.sleep(int(parameters['time']))
    return {'title': f"cross-section =  {float(parameters['a']) * float(parameters['b'])}"}
