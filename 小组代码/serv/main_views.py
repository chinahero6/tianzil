from aiohttp import web
from .config import db_block, web_routes, render_html


# @web_routes.get("/")
# async def home_page(request):
#     return web.HTTPFound(location="/base")

@web_routes.get("/")
async def view_list_passwords(request):
    
    return render_html(request, 
                    'home.html')

@web_routes.get("/base")
async def view_list_passwords(request):
    
    return render_html(request, 
                    'base.html')




