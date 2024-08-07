from pprint import pprint


class LocalRegistry:

    """
    Object to store a list of servers
    """

    def __init__(self):
        self.servers = []  # Changed from set to list
        self.next_idx = -1

    def join_server(self, ip, port):
        """
        The manager server has its on register with all
        the other backup servers.
        join_server input a new key ip & port to this set

        TODO create a method in Manager that update the reg in all servers
        """
        if (ip, port) not in self.servers:
            self.servers.append((ip, port))
        return f"Server {ip}:{port} joined"

    def next(self):
        """
        Get next server with round robin selection 
        """
        self.next_idx = (self.next_idx + 1) % len(self.servers)
        next_val = self.servers[self.next_idx]
        return next_val

    def __str__(self):
        pprint(self.servers)
        return 
