from aiohttp import web


async def main(request):
    text = "Hello, world"
    return web.Response(text=text)


app = web.Application()
app.router.add_get('/', main)

handler = app.make_handler()
