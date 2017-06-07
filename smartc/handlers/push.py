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

from tornado import websocket
from zmq.eventloop import zmqstream
import zmq


clients = []
context = zmq.Context()


class PushHandler(websocket.WebSocketHandler):
    def check_origin(self, origin):
        print(origin)
        return True

    def _push_message(self, message):
        self.write_message(message[1])

    def open(self):
        if self not in clients:
            print('Added client', self)
            clients.append(self)

        socket = context.socket(zmq.SUB)
        socket.connect("tcp://127.0.0.1:5555")
        socket.setsockopt_string(zmq.SUBSCRIBE, "pub")
        stream_sub = zmqstream.ZMQStream(socket)
        stream_sub.on_recv(self._push_message)

    def on_message(self, message):
        self.write_message(message)

    def on_close(self):
        if self in clients:
            print('Removed client', self)
            clients.remove(self)
