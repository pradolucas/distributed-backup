from ast import literal_eval
import os
from Server import Server


class Worker(Server):

    def __init__(self, ip, port_number, path_folder):
        super().__init__(ip, port_number)
        self.path_folder = path_folder

    def run(self):
        self.connect_manager()
        Server.listen(self, Worker.ConnThread)

    def connect_manager(self):
        """
        Connect the current Worker Server to the Manager Server
        """
        manager_socket = Server.tcp_socket_create_connect(
            *self.manager_addr)
        print(
            f"[WORKER] {manager_socket.getsockname()} Connected to {manager_socket.getpeername()}")
        message = f"<JOIN> ({self.addr})".encode('ascii')
        manager_socket.sendall(message)
        print("[WORKER] Message sent")
        manager_socket.close()
        return

    def get_backup_addr(self):
        """
        Fetch server addr from Manager to make backup
        """
        msg = b"<BACKUP>"
        s = Server.tcp_socket_create_connect(*self.manager_addr)
        s.sendall(msg)

        msg = s.recv(1024).decode('utf-8').strip()
        if msg.startswith("<POINTER>"):
            server_backup_addr = literal_eval(msg.split(">")[1])
        s.close()

        return server_backup_addr

    def backup_file_to_server(self, addr_d, file_name):
        """
        Takes a file from the current server and sends to another server
        """
        msg = f"<BACKUP> {file_name}".encode('ascii')
        transfer_socket = Server.tcp_socket_create_connect(*addr_d)
        transfer_socket.sendall(msg)

        # Check if file exists in own folder and send via TCP
        self.send_file(transfer_socket, file_name)
        transfer_socket.close()

    def send_file(self, conn, file_name):
        """
        Check if file exists in own directory and send via TCP
        """
        file_path = os.path.join(self.path_folder, file_name)
        if os.path.exists(file_path):
            with open(file_path, "rb") as f:
                while chunk := f.read(1024):
                    conn.sendall(chunk)

    def rec_file(self, conn, file_name):
        """
        Creates file in own directory and receive via TCP
        """
        file_path = os.path.join(self.path_folder, file_name)
        with open(file_path, "wb") as file:
            while data := conn.recv(1024):
                file.write(data)
        conn.close()

    class ConnThread(Server.ConnThread):

        """
        Threats the Server/Client connection request
        SAVE from clients
        BACKUP from other servers
        ?POINTER from Manager
        """

        def run(self):
            try:
                msg = self.conn.recv(1024).decode('utf-8')
                print(f"[WORKER] Received msg: {msg}")
                splits = msg.split(">")
                file_name = splits[1].strip()
                if msg.startswith("<SAVE>"):  # FROM CLIENT
                    self.server.rec_file(self.conn, file_name)
                    backup_addr = self.server.get_backup_addr()
                    self.server.backup_file_to_server(backup_addr, file_name)
                elif msg.startswith("<BACKUP>"):  # FROM SERVER
                    self.server.rec_file(self.conn, file_name)
            except IOError:
                pass
            self.conn.close()
