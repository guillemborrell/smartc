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

import os
from multiprocessing import Process

from tornado import web
from zmq.eventloop import ioloop

from smartc.broker import server_pub
from smartc.handlers.web import IndexHandler
from smartc.handlers.push import PushHandler
from smartc.handlers.rest import RestHandler

ioloop.install()

app = web.Application([
    (r'/', IndexHandler),
    (r'/push', PushHandler),
    (r'/rest', RestHandler),
    (r'/(favicon.ico)', web.StaticFileHandler, {
        'path': os.path.join(os.pardir, 'static')
    }),
    ])


def main(port):
    app.listen(port)
    ioloop.IOLoop.instance().start()
    

if __name__ == '__main__':
    Process(target=server_pub).start()
    main(8080)
