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

clients = []

class SocketHandler(websocket.WebSocketHandler):
    def check_origin(self, origin):
        print(origin)
        return True
    
    def open(self):
        if self not in clients:
            print('Added client', self)
            clients.append(self)

    def on_message(self, message):
        print(message)
        self.write_message(message)

    def on_close():
        if self in cl:
            print('Removed client', self)
            clients.remove(self)

