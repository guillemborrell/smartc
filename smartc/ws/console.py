#   Smartc. Smart contracts for real time applications.
#   Copyright (C) 2017 Guillem Borrell i Nogueras (@guillemborrell)
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU Affero General Public License as published
#   by the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU Affero General Public License for more details.
#
#   You should have received a copy of the GNU Affero General Public License
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.

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

