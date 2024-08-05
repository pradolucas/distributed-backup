import socket
import threading
from Worker import Worker
from Registry import LocalRegistry


class Manager (Worker):
    def __init__(self, ip, number_port):
        # analyse type of architecture to not account fo path_folder
        super().__init__(ip, number_port, path_folder="")
        # self.ip_addr = ip
        # self.number_port = number_port
        # self.reg = LocalRegistry()

    def listen(self):

        self.start()
        # Function to listen to requests from Server
        self.listen_peers()

    def listen_peers(self):
        """
        Instatiate a socket that listen to new conn
        New conns are put in a new thread
        """

        def listen():
            listen_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            listen_socket.bind((self.ip_addr, self.number_port))
            listen_socket.listen(5)
            while True:
                connect_socket, _ = listen_socket.accept()
                ConnThread(connect_socket).start()

        threading.Thread(target=listen).start()


class ConnThread(threading.Thread):

    """
    Threats the Server/Client connection request
    """

    def __init__(self, conn):
        super().__init__()
        self.conn = conn

    def run(self):
        try:
            istream = self.conn.makefile("r")
            msg = istream.readline().strip()
            splits = msg.split(">")
            if splits[0] == "<JOIN>":  # FROM SERVER
                self.reg.joinServer(self.conn.getpeername())  # (ip, port); updates list
            elif splits[0] == "<SAVE>":  # FROM CLIENT
                pass
            self.conn.close()
            print("\n>>>")
        except IOError:
            pass
