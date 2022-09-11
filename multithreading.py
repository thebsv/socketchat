import socket

from collections import defaultdict
from threading import Thread, Lock
from typing import List

clients = {}
client_messages = defaultdict(list)
lock_object = Lock()


class Database:
    @staticmethod
    def insert_client(c_sock, c_addr) -> None:
        global lock_object, clients
        lock_object.acquire()
        clients[c_addr] = c_sock
        lock_object.release()

    @staticmethod
    def get_client(to_client) -> socket.socket:
        global lock_object, clients
        lock_object.acquire()
        cli_sock = clients[to_client]
        lock_object.release()
        return cli_sock

    @staticmethod
    def retrieve_all_client_names() -> List[str]:
        global lock_object, clients
        lock_object.acquire()
        clis = [str(x) for x in clients.keys()]
        lock_object.release()
        return clis

    @staticmethod
    def retrieve_all_client_socks() -> List[socket.socket]:
        global lock_object, clients
        lock_object.acquire()
        clis = [x for x in clients.values()]
        lock_object.release()
        return clis

    @staticmethod
    def remove_client(c_sock) -> None:
        global lock_object, clients
        lock_object.acquire()
        del clients[c_sock]
        lock_object.release()

    @staticmethod
    def retrieve_client_history(c_sock) -> List[str]:
        global lock_object, client_messages
        lock_object.acquire()
        msgs = [x for x in client_messages[c_sock]]
        lock_object.release()
        return msgs

    @staticmethod
    def insert_message(c_sock, message) -> None:
        global lock_object, client_messages
        lock_object.acquire()
        client_messages[c_sock].append(message)
        lock_object.release()

    @staticmethod
    def print_e() -> None:
        global lock_object, clients, client_messages
        lock_object.acquire()
        print(clients, client_messages)
        lock_object.release()


db = Database()


class ClientThread(Thread):
    def __init__(self, c_sock, c_addr):
        Thread.__init__(self)
        self.client_sock = c_sock
        self.client_addr = c_addr
        db.insert_client(c_sock, c_addr)

    def run(self) -> None:
        print("connection from: {}".format(self.client_sock))
        try:
            while self.client_sock:
                data = str(self.client_sock.recv(1024), 'ascii')
                if data:
                    db.insert_message(self.client_sock, data)
                    if data == "exit":
                        db.remove_client(self.client_sock)
                        self.client_sock.close()
                        break
                    elif data.find("/list") > -1:
                        self.client_sock.sendall(bytes(str(db.retrieve_all_client_names()), 'ascii'))
                    elif data.find("/send") > -1:
                        # print("client {} {}".format(self.client_sock.getpeername(), data))
                        _, to_client, *message = data.split(' ')
                        to_client = ('127.0.0.1', int(to_client))
                        # db.print_e()
                        c_sock = db.get_client(to_client)
                        c_sock.sendall(bytes(" ".join(message), 'ascii'))
                    elif data.find("/broadcast") > -1:
                        _, *message = data.split(' ')
                        for cli in db.retrieve_all_client_socks():
                            if self.client_sock != cli:
                                cli.sendall(bytes(" ".join(message), 'ascii'))
                    elif data.find("/history") > -1:
                        self.client_sock.sendall(bytes(str(db.retrieve_client_history(self.client_sock)), 'ascii'))
                    else:
                        print("client {} sent {} ".format(self.client_sock.getpeername(), data))
                else:
                    db.remove_client(self.client_addr)
                    self.client_sock.close()
        except KeyboardInterrupt:
            db.remove_client(self.client_addr)
            self.client_sock.close()


def server_main(server_sock):
    client_threads = []
    try:
        while True:
            server_sock.listen(1)
            c_sock, c_addr = server_sock.accept()
            c_thread = ClientThread(c_sock, c_addr)
            client_threads.append(c_thread)
            c_thread.start()
    except KeyboardInterrupt:
        for ct in client_threads:
            ct.join()


if __name__ == "__main__":
    HOST, PORT = 'localhost', 59007
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind((HOST, PORT))
        server_main(server)
