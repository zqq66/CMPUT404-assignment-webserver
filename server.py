#  coding: utf-8 
import socketserver
import os

# Copyright 2013 Abram Hindle, Eddie Antonio Santos
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
#
# Furthermore it is derived from the Python documentation examples thus
# some of the code is Copyright © 2001-2013 Python Software
# Foundation; All Rights Reserved
#
# http://docs.python.org/2/library/socketserver.html
#
# run: python freetests.py

# try: curl -v -X GET http://127.0.0.1:8080/


class MyWebServer(socketserver.BaseRequestHandler):
    def handle(self):
        self.data = self.request.recv(1024).strip()
        # print("Got a request of: %s\n" % self.data)
        request = self.data.decode('utf-8').split()
        if len(request) > 2:
            self.method, self.address = request[0], request[1]
            # check request should used
            if self.method != 'GET':
                self._405_()
            else:
                self.path = os.path.abspath("www") + self.address
                if os.path.isdir(self.path):
                    if not self.path.endswith('/'):
                        self.path += '/'
                        self.address += '/'
                        self._301_(self.address)
                    self.path += "index.html"
                    if os.path.exists(self.path):
                        self._200_("text/html", self.path)
                    else:
                        self._404_()

                elif os.path.isfile(self.path):
                    # check mime type
                    if self.path.endswith(".html"):
                        self._200_('text/html', self.path)
                    elif self.path.endswith(".css"):
                        self._200_('text/css', self.path)
                    else:
                        self._404_()
                else:
                    self._404_()
        else:
            raise ValueError("Invalid Request")

        self.request.sendall(bytearray("OK",'utf-8'))

    def _200_(self, content_type, path):
        header = 'HTTP/1.1 200 OK\r\n' + 'Content-Type: ' + content_type + '\r\n'
        file = open(path)
        response = file.read()
        file.close()
        self.request.sendall((header + "\r\n" + response).encode('utf8'))

    def _301_(self, path):
        header = 'HTTP/1.1 301 MOVED PERMANENTLY\r\n' + "Location: " + path + "\r\n"
        self.request.sendall(header.encode('utf8'))

    def _404_(self):
        # Not Found
        self.request.sendall("HTTP/1.1 404 Not Found\r\n\r\n<html><body><h3>404 File not found</h3></body</html>".encode('utf8'))

    def _405_(self):
        self.request.sendall('HTTP/1.1 405 Method Not Allowed\r\n'.encode('utf8'))


if __name__ == "__main__":
    HOST, PORT = "localhost", 8080

    socketserver.TCPServer.allow_reuse_address = True
    # Create the server, binding to localhost on port 8080
    server = socketserver.TCPServer((HOST, PORT), MyWebServer)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()
