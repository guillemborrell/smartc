from tornado import websocket, ioloop
import cmd


async def create_repl(url):
    client = Client(url)
    await client._init()
    return client


class Client(cmd.Cmd):
    def __init__(self, url):
        super(Client, self).__init__()
        self.url = url
        self.conn = None

    async def _init(self):
        self.conn = await websocket.websocket_connect(self.url)
        print(self.conn)

    def do_send(self, arg):
        ioloop.IOLoop.current().add_future(
            self.conn.write_message(arg, binary=True),
            lambda x: print(x))


async def main():
    repl = await create_repl('ws://localhost:8080/ws')
    repl.cmdloop()


if __name__ == '__main__':
    print(main)
    ioloop.IOLoop.instance().run_sync(main)

