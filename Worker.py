import os
import socket
import threading
from time import sleep
from Server import Server, ConnThread


class Worker(Server):

    def __init__(self, ip, port_number, path_folder):
        super().__init__(ip, port_number)
        self.path_folder = path_folder
        self.backup_addr = ('localhost', 61000)
        self.connect_manager()
        self.listen()

    # def run(self):
        # self.connect_manager()
        # self.listen()

    def connect_manager(self):
        """
        Connect the current Worker Server to the Manager Server
        """
        # print(f"[WORKER] {(self.ip_addr, self.port_number)} Sending connect request to {(self.manager_ip, self.manager_port)}")
        manager_socket = Server.tcp_socket_create_connect(
            *(self.manager_ip, self.manager_port))
        print(
            f"[WORKER] {manager_socket.getsockname()} Connected to {manager_socket.getpeername()}")
        sleep(1)
        message = f"<JOIN> ({self.ip_addr, self.port_number})".encode('ascii')
        manager_socket.sendall(message)
        print("[WORKER] Message sent")
        manager_socket.close()
        return

    def backup_file_to_server(self, addr_d, file_name):
        """
        Takes a file from the current server and sends to another server
        """
        def send_file(addr_d, file_name):
            msg = f"<BACKUP> {file_name}".encode('ascii')
            transfer_socket = Server.tcp_socket_create_connect(*addr_d)
            transfer_socket.sendall(msg)

            file_path = os.path.join(self.path_folder, file_name)
            # Check if file exists in own 1 and send via TCP
            if os.path.exists(file_path):
                with open(file_path, "rb") as f:
                    while chunk := f.read(1024):
                        transfer_socket.sendall(chunk)
            transfer_socket.close()
        send_file(addr_d, file_name)
        # threading.Thread(target=send_file, args=(addr_d, file_name)).start()

    def listen(self):
        Server.listen(self, Worker.ConnThread)
        # sleep(1)
        # while True:
        #     print("\nBACKUP(2)\n>>> ")
        #     try:
        #         option = int(input())
        #         if option == 2:
        #             print(
        #                 f"Selecione um dos server para transferir arquivo: {', '.join(self.reg)}")
        #             ip_tranfer = input("Insira o IP: ")
        #             port_tranfer = int(input("Insira a Porta: "))
        #             file_name = input("Insira o arquivo para backup: ")

        #             # Instantiate and start a thread to tranfer the file
        #             Worker.backup_file_to_server(
        #                 self, ip_tranfer, port_tranfer, file_name)
        #             # TranferThread(file_name, ip_tranfer).start()
        #         else:
        #             # sleep(2)
        #             print("Opção inválida\n")
        #     except ValueError:
        #         print("Opção inválida\n")

    class ConnThread(ConnThread):

        """
        Threats the Server/Client connection request
        SAVE from clients
        BACKUP from other servers
        ? from Manager
        """

        def run(self):
            try:
                # istream = self.conn.makefile("r")
                # msg = istream.readline().strip()
                msg = self.conn.recv(1024).decode('utf-8')
                print(f"[WORKER] Received msg: {msg}")
                splits = msg.split(">")
                file_name = splits[1].strip()
                if msg.startswith("<SAVE>"):  # FROM CLIENT
                    self.rec_file(file_name)
                    self.server.backup_file_to_server(self.server.backup_addr, file_name)
                if msg.startswith("<BACKUP>"):  # FROM SERVER
                    self.rec_file(file_name)
                print("\n>>>")
            except IOError:
                pass
            self.conn.close()

        # def send_file(self: ConnThread, file_path):
        #     # Unificar com método de backup_file_to_server
        #     # Check if file exists in own directory and send via TCP
        #     if os.path.exists(file_path):  # Throw exception
        #         with open(file_path, "rb") as f:
        #             while chunk := f.read(1024):
        #                 self.conn.sendall(chunk)
        #         self.conn.close()

        def rec_file(self, file_name):
            file_path = os.path.join(self.server.path_folder, file_name)
            with open(file_path, "wb") as file:
                while data := self.conn.recv(1024):
                    file.write(data)
            self.conn.close()
