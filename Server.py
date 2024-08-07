from abc import ABCMeta, abstractmethod
import socket
import threading
from Registry import LocalRegistry


class Server(threading.Thread):

    """
    Base class for Worker and Manager Servers
    """

    # def __init__(self, ip, number_port, path_folder, manager_flag: bool):
    def __init__(self, ip: str, port_number: int):
        super().__init__()
        self.ip_addr = ip
        self.port_number = port_number
        self.reg = LocalRegistry()  # Só manager?
        self.manager_ip = "localhost"
        self.manager_port = 50000  # juntar em tupla

    @staticmethod
    # To set up specific port, arg bind
    def tcp_socket_create_connect(ip, port, bind=None):
        """
        Create a socket and connects to the designated ip, port 
        """
        print(f"Trying connection to {ip}:{port}")
        s = socket.socket(
            socket.AF_INET, socket.SOCK_STREAM)
        if bind:
            print(f"With bind {bind}")
            s.bind(bind)
        s.connect((ip, port))
        print(f"Connected to {ip}:{port}")
        return s

    def listen(self, conn_thread_class):
        """
        Instatiate a new thread to listen to new connections
        """
        self.start()
        # Function to listen to requests from Server
        # Não pode ser bloqueante, rodar em thread
        threading.Thread(target=self.listen_peers,
                         args=(conn_thread_class,)).start()

    def listen_peers(self, conn_thread_class):
        """
        Instatiate a socket that listen to new conn
        New conns are put in a new thread
        """

        # def listen():

        listen_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # print(f"passou {self.passou+1}")
        listen_socket.bind((self.ip_addr, self.port_number))
        listen_socket.listen(5)
        print(
            f"[SERVER] Listening to connections in {(self.ip_addr, self.port_number)}")
        # print("[SERVER] Waiting connection\n")
        while True:
            connect_socket, _ = listen_socket.accept()
            conn_thread_class(self, connect_socket).start()

        listen_socket.close()
        # threading.Thread(target=listen).start()


class ConnThread(threading.Thread):

    """
    Threats the Server/Client connection request
    """

    # def __init__(self, server: Server, conn: socket.socket):
    def __init__(self, server, conn: socket.socket):
        super().__init__()
        self.server = server
        self.conn = conn
        # print("[SERVER] Received conn, Running Server conn thread")

    @abstractmethod
    def run(self):
        pass
