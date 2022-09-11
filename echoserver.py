import threading
import socketserver


class ThreadedTCPRequestHandler(socketserver.BaseRequestHandler):
    def handle(self) -> None:
        data = str(self.request.recv(1024), 'ascii')
        curr_thread = threading.current_thread()
        response = bytes("{}:{}".format(curr_thread.name, data), 'ascii')
        self.request.sendall(response)


class ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    pass


if __name__ == '__main__':
    # PORT 0 means select an arbitrary unused port
    HOST, PORT = 'localhost', 0
    server = ThreadedTCPServer((HOST, PORT), ThreadedTCPRequestHandler)
    ip, port = server.server_address
    print("Server started on {}:{} ".format(ip, port))
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("server stopped ")
        server.shutdown()



