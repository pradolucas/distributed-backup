from pprint import pprint


class LocalRegistry:
    """
    Object to store a list of servers
    """

    def __init__(self):
        self.servers = []
        self.forward_idx = -1
        self.backup_idx = -2

    def join_server(self, ip, port):
        """
        The manager server has its on register with all
        the other backup servers.
        join_server input a new key ip & port to this set
        """
        if (ip, port) not in self.servers:
            self.servers.append((ip, port))
        return f"Server {ip}:{port} joined"

    def next_redirect(self):
        """
        Get next server for download with round robin selection
        """
        self.forward_idx = (self.forward_idx + 1) % len(self.servers)
        next_val = self.servers[self.forward_idx]
        return next_val

    def next_backup(self):
        """
        Get next server for backup with round robin selection
        """
        self.backup_idx = (self.backup_idx + 1) % len(self.servers)
        next_val = self.servers[self.backup_idx]
        return next_val

    def __str__(self):
        pprint(self.servers)
        return ""
