from aiohttp import web
from .config import db_block, web_routes, render_html


@web_routes.get('/error')
async def dialog_error(request):
    message = request.query.get("message")
    return_path = request.query.get("return")

    return render_html(request, 'dialog_error.html',
                       message=message,
                       return_path=return_path)
