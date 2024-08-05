import os
import socket
import threading
# import json
# from pathlib import Path
from Registry import LocalRegistry
from Server import Server 


class Worker(Server):

    # def __init__(self, ip, number_port, path_folder, manager_flag: bool):
    def __init__(self, ip, number_port, path_folder):
        super().__init__()
        self.ip_addr = ip
        self.number_port = number_port
        self.path_folder = path_folder
        # self.manager = manager_flag
        self.reg = LocalRegistry()
        self.manager_ip = "localhost"
        self.manager_port = "8080"
        self.connect_manager()

    def connect_manager(self):
        sub_server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sub_server_socket.connect((self.manager_ip, self.manager_port))
        message = "<JOIN>"
        sub_server_socket.sendall(message)
        return

    @staticmethod
    def tcp_socket_create_connect(ip, port):
        """
        Create a socket and connects to the designated ip, port 
        """
        s = socket.socket(
            socket.AF_INET, socket.SOCK_STREAM).connect((ip, port))
        return s

    def backup_file_to_server(self, ip_d, port_d, file_name):
        """
        Takes a file from the current server and sends to another server
        """
        def send_file_to_server(ip_d, port_d, file_name):

            # transfer_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            # transfer_socket.connect((ip_d, port_d))
            transfer_socket = Worker.tcp_socket_create_connect(ip_d, port_d)
            file_path = os.path.join(self.path_folder, file_name)

            # Check if file exists in own directory and send via TCP
            if os.path.exists(file_path):
                with open(file_path, "rb") as f:
                    while chunk := f.read(1024):
                        transfer_socket.sendall(chunk)
            transfer_socket.close()

        threading.Thread(target=send_file_to_server,
                         args=(ip_d, port_d, file_name)).start()

    # @staticmethod
    def listen(self):
        # Capture IP, port and folder path
        # ip = input("Insira o IP: ")
        # port = int(input("Insira a Porta: "))
        # folderPath = input("Insira a pasta dos arquivos: ")
        # ip = "localhost"
        # port = 8080
        # folderPath = "server_file_folder"

        # Instantiate a Server and start its thread
        # p = Server(ip, port, folderPath)
        # p = self

        self.start()

        # Function to listen to requests from Server
        self.listen_peers()

        while True:
            print("\nBACKUP(2)>>>")
            try:
                option = int(input())
                if option == 2:
                    print(
                        f"Selecione um dos server para transferir arquivo: {', '.join(self.reg)}")
                    ip_tranfer = input("Insira o IP: ")
                    port_tranfer = int(input("Insira a Porta: "))
                    file_name = input("Insira o arquivo para backup: ")

                    # Instantiate and start a thread to tranfer the file
                    Worker.backup_file_to_server(
                        self, ip_tranfer, port_tranfer, file_name)
                    # TranferThread(file_name, ip_tranfer).start()
                else:
                    print("Opção inválida\n")
            except ValueError:
                print("Opção inválida\n")

    # @staticmethod

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


# Threats the Manager/Server/Client connection request
# and treats based on the type
# JOIN
# DOWNLOAD
# BACKUP sends to one of the designated servers
# SAVE
class ConnThread(threading.Thread):
    def __init__(self, conn):
        super().__init__()
        self.conn = conn

    def run(self):
        try:
            istream = self.conn.makefile("r")
            msg = istream.readline().strip()
            splits = msg.split(">")
            if splits[0] == "<DOWNLOAD>":  # FROM CLIENT
                pass
            if splits[0] == "<BACKUP>":  # FROM CLIENT
                filename = splits[1]
                Worker.send_file_to_server(
                    os.path.join(Worker.path_folder, filename), self.conn
                )
            elif splits[0] == "<JOIN>":
                self.reg.joinServer(self.conn.getpeername())  # (ip, port)
            self.conn.close()
            print("\n>>>")
        except IOError:
            pass
