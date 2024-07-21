import os
import socket
import threading
import json
from pathlib import Path
from pprint import pprint


class LocalRegistry:

    def __init__(self):
        self.servers = set()

    def join_server(self, ip, port):
        """
        The manager server has its on register with all
        the other backup servers.
        join_server input a new key ip & port to this set
        """
        self.servers.add((ip, port))
        return f"Server {ip}:{port} joined"

    def __str__(self):
        pprint(self.servers)


class Server(threading.Thread):

    def __init__(self, ip, numberPort, pathFolder):
        super().__init__()
        self.ipAddr = ip
        self.number_port = numberPort
        self.pathFolder = pathFolder
        self.reg = LocalRegistry()

    @staticmethod
    def listen():
        # Capture IP, port and folder path
        ip = input("Insira o IP: ")
        port = int(input("Insira a Porta: "))
        folderPath = input("Insira a pasta dos arquivos: ")

        # Instantiate a Server and start its thread
        p = Server(ip, port, folderPath)
        p.start()

        # Function to listen to requests from Server
        Server.listen_peers()

        while True:
            print("\nJOIN SERVER(1)\nTRANSFER FILE(2)\n>>>")
            try:
                option = int(input())
                if option == 1:
                    # Call function to perform remote join to the server
                    Server.reg.joinServer(ip, port)
                elif option == 2:
                    print(
                        f"Selecione um dos server para transferir arquivo: {', '.join(reg)}"
                    )
                    ip_tranfer = input("Insira o IP: ")
                    port_tranfer = int(input("Insira a Porta: "))
                    # Instantiate and start a thread to _tranfer the file
                    TranferThread(file_name, ip_tranfer).start()
                else:
                    print("Opção inválida\n")
            except ValueError:
                print("Opção inválida\n")

    # @staticmethod
    def listen_peers():
        """
        Instatiate a socket that listen to new conn
        New conns are put in a new thread
        """

        def listen():
            listen_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            listen_socket.bind(("", Server.number_port))
            listen_socket.listen(5)
            while True:
                connect_socket, _ = listen_socket.accept()
                ConnThread(connect_socket).start()

        threading.Thread(target=listen).start()

    @staticmethod
    def sendFileToServer(filePath, s: socket.socket):
        # Check if file exists in the Peer directory
        if os.path.exists(filePath):
            with open(filePath, "rb") as f:
                while True:
                    buffer = f.read(1024)
                    if not buffer:
                        break
                    s.sendall(buffer)


# Takes the peer connection request and sends to one of the designated servers
class ConnThread(threading.Thread):
    def __init__(self, node):
        super().__init__()
        self.node = node

    def run(self):
        try:
            istream = self.node.makefile("r")
            msg = istream.readline().strip()
            splits = msg.split("|")
            if splits[0] == "DOWNLOAD":
                filename = splits[1]
                Server.sendFileToServer(
                    os.path.join(Server.pathFolder, filename), self.node
                )
            self.node.close()
            print("\n>>>")
        except IOError:
            pass
