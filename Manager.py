from ast import literal_eval
import socket
# import threading
from Registry import LocalRegistry
import Server
from Server import Server, ConnThread


class Manager (Server):
    def __init__(self, ip, port_number):
        # analyse type of architecture to not account fo path_folder
        super().__init__(ip, port_number)
        Server.listen(self, Manager.ConnThread)
        # self.reg = LocalRegistry()
        
    
    class ConnThread(ConnThread):

        """
        Threats the Server/Client connection request
        """

        def __init__(self, server, conn: socket.socket):
            super().__init__(server, conn)
            # print("Running init manager conn thread")

        # @staticmethod
        def next_server_workload(self, reg):
            return reg.next()
        
        # @staticmethod
        def redirect_conn(self, reg: LocalRegistry, conn: socket.socket):
            """
            """
            # threading.Thread(target=send_file_to_server,
            #                  args=(ip_d, port_d, file_name)).start()
            # server_redirect_addr = ConnThread.next_server_workload(reg)
            server_redirect_addr = reg.next()
            # s = Server.tcp_socket_create_connect(*conn.getpeername())
            msg = f'<REDIRECT> {server_redirect_addr}'.encode('ascii')
            # <{",".join([str(s) for s in server_redirect])}>'
            print("[MANAGER] Sending redirect")
            conn.sendall(msg)
            print(msg)

        def run(self):
            print("[Manager] Running Manager conn thread")
            print(f"[Manager] Connected to {self.conn.getpeername()}")
            try:
                print("[Manager] waiting response")
                msg = self.conn.recv(1024).decode('utf-8').strip()
                # istream = self.conn.makefile("r")
                # msg = istream.readline().strip()
                print(f"[Manager] Manager Received a message: {msg}")
                if msg.startswith("<JOIN>"):  # FROM SERVER
                    # Updates server list, (ip, port)
                    # print("[Manager] Received a <JOIN>")
                    server_redirect_addr = literal_eval(msg.split(">")[1])
                    self.server.reg.join_server(*server_redirect_addr)
                    print(self.server.reg.servers)
                elif msg.startswith("<SAVE>"):  # FROM CLIENT
                    # Redirect connection
                    print("[Manager] Received a <SAVE>")
                    self.redirect_conn(self.server.reg, self.conn)
                    # Send message to designated server?
                self.conn.close()
                # print("\n>>>")
            except IOError:
                pass
            
            self.conn.close()