from os import listdir
from os.path import isfile, join, exists
from ast import literal_eval
import socket
import threading
from time import sleep
from Server import Server


class Client(threading.Thread):
    def __init__(self, ip, port_number, path_folder):
        super().__init__()
        self.ip_addr = ip
        self.port_number = port_number
        self.path_folder = path_folder
        self.manager_addr = ("localhost",  50000)
        self.start()

        # client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # client_socket.connect((ip, number_port))

    @staticmethod
    def tcp_socket_create_connect(ip, port):
        """
        Create a socket and connects to the designated ip, port 
        """
        s = socket.socket(
            socket.AF_INET, socket.SOCK_STREAM).connect((ip, port))
        return s

    def run(self):

        # Instantiate a peer and start its thread
        # self.start()

        # searchResponse = None
        # file_name = None
        while True:
            print("\nSAVE(1)\n>>>", end=' ')
            try:
                option = int(input())
                if option == 1:
                    # File name to be searched
                    file_list = [f for f in listdir(
                        self.path_folder) if isfile(join(self.path_folder, f))]
                    file_list_selection = '\n'.join([f'({idx}) {f}' for idx, f in enumerate(file_list)])
                    file_idx = int(input(
                        f"\nSelecionar qual arquivo salvar:\n{file_list_selection} \n>>> "))
                    self.transfer_file_to_server(file_list[file_idx])
                    # Instantiate and start a thread to transfer the file
                    # DownloadThread(file_name, ip_download, port_download).start()
                else:
                    print("Opção inválida\n")
            except ValueError:
                print("Opção inválida\n")

    def listen(self):
        """
        ? Rodar em thread separada?

        """
        listen_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        listen_socket.bind((self.ip_addr, self.port_number))
        listen_socket.listen(5)
        while True:
            connect_socket, _ = listen_socket.accept()
            msg = connect_socket.recv(1024).strip()  # .decode('utf-8')
            if msg.startswith("<REDIRECT>"):
                server_redirect_addr = literal_eval(msg.split(">")[1])
                return server_redirect_addr

            # Server.ConnThread(self, connect_socket).start()

    def transfer_file_to_server(self, file_name):

        # Communicate Manager
        s = Server.tcp_socket_create_connect(
            *self.manager_addr)
        print()
        message = b"<SAVE>"
        s.sendall(message)
        print(f"[CLIENT] {s.getsockname()} Sended msg")
        msg = s.recv(1024).decode('utf-8').strip()
        print(f"[CLIENT] Received REDIRECT from MANAGER {msg}")
        if msg.startswith("<REDIRECT>"):
            server_redirect_addr = literal_eval(msg.split(">")[1])
        s.close()

        # threading.Thread(target=Peer.listen, args=self).start()
        # server_redirect_addr = Client.listen(self)  # Bloqueante

        # Check if file exists in own directory and send via TCP
        file_path = join(self.path_folder, file_name)
        transfer_socket = Server.tcp_socket_create_connect(
            *server_redirect_addr, (self.ip_addr, self.port_number))
        message = f"<SAVE> {file_name}".encode('ascii')
        transfer_socket.sendall(message)

        if exists(file_path):
            with open(file_path, "rb") as f:
                while chunk := f.read(1024):
                    transfer_socket.sendall(chunk)
        transfer_socket.close()

    # # Method for sending file to main server
    # @staticmethod
    # def sendFileToPeer(filePath, s):
    #     # Check if file exists in the Peer directory
    #     if os.path.exists(filePath):
    #         with open(filePath, 'rb') as f:
    #             while True:
    #                 buffer = f.read(1024)
    #                 if not buffer:
    #                     break
    #                 s.sendall(buffer)


# class ConnThread(threading.Thread):
#     def __init__(self, node):
#         super().__init__()
#         self.node = node

#     def run(self):
#         try:
#             istream = self.node.makefile('r')
#             msg = istream.readline().strip()
#             splits = msg.split('|')
#             if splits[0] == "DOWNLOAD":
#                 filename = splits[1]
#                 Peer.sendFileToPeer(os.path.join(
#                     Peer.pathFolder, filename), self.node)
#             self.node.close()
#             print("\n>>>")
#         except IOError:
#             pass


# class DownloadThread(threading.Thread):
#     def __init__(self, fileName, ipDownload, portDownload):
#         super().__init__()
#         self.fileName = fileName
#         self.ipDownload = ipDownload
#         self.portDownload = portDownload

#     def run(self):
#         try:
#             Peer.downloadFileFromPeer(
#                 self.fileName, self.ipDownload, self.portDownload)
#         except IOError:
#             pass


# if __name__ == "__main__":
#     Peer.main()
