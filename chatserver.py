import select
import socket
from socket import socket
from typing import List, Union, Any


def server_main(server_sock: socket.socket) -> None:
    clients = [server_sock]
    message_queue = []
    while True:
        try:
            # use select to get the potential readers, writers and errors
            read_clients, write_clients, errors = select.select(clients, clients, clients)
            for sock in read_clients:
                if sock == server_sock:
                    # if the server socket is the one reading, then call accept to
                    # let new clients in and add to the list of active clients
                    conn, (ip, port) = sock.accept()
                    conn.setblocking(0)
                    print("client connected {}:{}".format(ip, port))
                    clients.append(conn)
                else:
                    data = str(sock.recv(1024), 'ascii')
                    if data:
                        message_queue.append((sock, bytes(str(sock.getpeername()) + " : " + data.upper(), 'ascii')))
                    else:
                        # if no data is transmitted, then close the socket and remove from list
                        sock.close()
                        clients.remove(sock)

            # broadcast the messages in message queue to all available writers
            # except the socket that originally sent the message
            for sock, message in message_queue:
                for w_sock in write_clients:
                    if sock != w_sock:
                        w_sock.sendall(message)

            message_queue.clear()

            for err in errors:
                err.close()
                clients.remove(err)

        except KeyboardInterrupt:
            for client in clients:
                client.close()


if __name__ == "__main__":
    HOST, PORT = 'localhost', 59007
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.setblocking(0)
        server.bind((HOST, PORT))
        server.listen(5)
        server_main(server)
        server.shutdown(0)
