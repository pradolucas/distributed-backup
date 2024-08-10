from ast import literal_eval
import socket
from Registry import LocalRegistry
from Server import Server, ConnThread


class Manager (Server):
    def __init__(self, ip, port_number):
        super().__init__(ip, port_number)
        self.reg = LocalRegistry()

    def run(self):
        Server.listen(self, Manager.ConnThread)

    class ConnThread(ConnThread):

        """
        Threats the Server/Client connection request
        """

        def redirect_conn(self, reg: LocalRegistry, conn: socket.socket):
            """
            Provides next available worker to save file
            """
            server_redirect_addr = reg.next_redirect()
            # Tratar exceção onde não há workers
            msg = f'<POINTER> {server_redirect_addr}'.encode('ascii')
            print("[MANAGER] Sending redirect")
            conn.sendall(msg)
            print(msg)

        def backup_conn(self, reg: LocalRegistry, conn: socket.socket):
            """
            Provides next available worker to backup file
            """
            server_backup_addr = reg.next_backup()
            # Tratar exceção onde não há workers
            msg = f'<POINTER> {server_backup_addr}'.encode('ascii')
            print("[MANAGER] Sending backup")
            conn.sendall(msg)
            print(msg)

        def run(self):
            print("[Manager] Running Manager conn thread")
            print(f"[Manager] Connected to {self.conn.getpeername()}")
            try:
                msg = self.conn.recv(1024).decode('utf-8').strip()
                print(f"[Manager] Manager Received a message: {msg}")
                if msg.startswith("<JOIN>"):  # FROM SERVER
                    server_redirect_addr = literal_eval(msg.split(">")[1])
                    self.server.reg.join_server(*server_redirect_addr)
                    print(self.server.reg.servers)
                elif msg.startswith("<SAVE>"):  # FROM CLIENT
                    # Redirect connection
                    print("[Manager] Received a <SAVE>")
                    self.redirect_conn(self.server.reg, self.conn)
                elif msg.startswith("<BACKUP>"):  # FROM SERVER
                    self.backup_conn(self.server.reg, self.conn)
                self.conn.close()
            except IOError:
                pass

            self.conn.close()
