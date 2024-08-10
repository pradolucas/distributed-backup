from os import listdir
from os.path import isfile, join, exists
from ast import literal_eval
import threading
from time import sleep
from Server import Server
# from Server import tcp_


class Client(threading.Thread):
    def __init__(self, path_folder):
        super().__init__()
        self.path_folder = path_folder
        self.manager_addr = ("localhost",  50000)

    def run(self):
        self.console_interface()

    def console_interface(self):
        """
        Console Interface
        """
        while True:
            sleep(1)
            print("\n(1) SAVE\n>>>", end=' ')
            try:
                option = int(input())
                if option == 1:
                    file_list = [f for f in listdir(
                        self.path_folder) if isfile(join(self.path_folder, f))]
                    file_list_selection = '\n'.join(
                        [f'({idx}) {f}' for idx, f in enumerate(file_list)])
                    file_idx = int(input(
                        f"\nSelecionar qual arquivo salvar:\n{file_list_selection} \n>>> "))
                    self.transfer_file_to_server(file_list[file_idx])
                else:
                    print("Opção inválida\n")
            except ValueError:
                print("Opção inválida\n")

    def get_save_addr(self):
        """
        Fetch the designated server addr to save file from the Manager Server
        """
        s = Server.tcp_socket_create_connect(*self.manager_addr)
        s.sendall(b"<SAVE>")
        print(f"\n[CLIENT] {s.getsockname()} Sended msg")

        # Receive response from manager
        msg = s.recv(1024).decode('utf-8').strip()
        print(f"[CLIENT] Received REDIRECT from MANAGER {msg}")
        if msg.startswith("<POINTER>"):
            server_redirect_addr = literal_eval(msg.split(">")[1])
        s.close()

        return server_redirect_addr

    def send_file(self, conn, file_name):
        """
        Check if file exists in own directory and send via TCP
        """
        file_path = join(self.path_folder, file_name)
        if exists(file_path):
            with open(file_path, "rb") as f:
                while chunk := f.read(1024):
                    conn.sendall(chunk)
        conn.close()

    def send_file_to_server(self, file_name, server_redirect_addr):
        """
        Check if file exists in own directory and send via TCP
        """
        transfer_socket = Server.tcp_socket_create_connect(
            *server_redirect_addr)
        message = f"<SAVE> {file_name}".encode('ascii')
        transfer_socket.sendall(message)
        self.send_file(transfer_socket, file_name)

    def transfer_file_to_server(self, file_name):
        """
        Creates a thread to fetch the server addr from 
        the Manager and send the file to the Worker Server
        """
        def handle():
            server_redirect_addr = self.get_save_addr()
            self.send_file_to_server(file_name, server_redirect_addr)

        threading.Thread(target=handle).start()
