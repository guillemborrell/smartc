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

import zmq
import time


def server_pub():
    print("Starting...")
    context = zmq.Context()
    socket = context.socket(zmq.PUB)
    socket.bind("tcp://127.0.0.1:5555")
    topic = "pub"

    for i in range(10):
        socket.send_multipart([topic.encode(), b"a_message"])
        time.sleep(1)
