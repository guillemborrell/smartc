from ws.handlers import factory
from monitor.handlers import handler, app
import asyncio


def main():
    loop = asyncio.get_event_loop()
    coro = loop.create_server(factory, '0.0.0.0', 9000)
    server = loop.run_until_complete(coro)

    webcoro = loop.create_server(handler, '0.0.0.0', 8080)
    webserver = loop.run_until_complete(webcoro)

    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.close()
        webserver.close()
        loop.run_until_complete(webserver.wait_closed())
        loop.run_until_complete(app.shutdown())
        loop.run_until_complete(handler.shutdown(60.0))
        loop.run_until_complete(app.cleanup())

    print(' Shutdown successful')
    loop.close()
    

if __name__ == '__main__':
    main()
