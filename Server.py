from abc import abstractmethod
import socket
import threading


class Server(threading.Thread):
    """
    Base class for Worker and Manager Servers
    """

    def __init__(self, ip: str, port_number: int):
        super().__init__()
        self.addr = (ip, port_number)
        self.manager_addr = ("localhost", 50000)

    @staticmethod
    def tcp_socket_create_connect(ip, port, bind=None):
        """
        Create a socket and connects to the designated ip, port
        To set up specific port, use arg bind
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
        # self.start()
        threading.Thread(target=self.listen_conn,
                         args=(conn_thread_class,)).start()

    def listen_conn(self, conn_thread_class):
        """
        Instatiate a socket that listen to new conn
        New conns are put in a new thread
        """

        listen_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        listen_socket.bind(self.addr)
        listen_socket.listen(5)
        print(
            f"[SERVER] Listening to connections in {self.addr}")
        while True:
            connect_socket, _ = listen_socket.accept()
            conn_thread_class(self, connect_socket).start()
        listen_socket.close()


class ConnThread(threading.Thread):
    """
    Threats the Server/Client connection request
    """

    def __init__(self, server, conn: socket.socket):
        super().__init__()
        self.server = server
        self.conn = conn

    @abstractmethod
    def run(self):
        pass
