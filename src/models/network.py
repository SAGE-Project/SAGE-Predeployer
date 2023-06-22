import json


class Network:
    def __init__(self, data):

        self.public_ips = data.get("publicIPs", None)
        self.ip_type = data.get("IPType", None)

    def print_network_details(self):
        print("Public IPs:", self.public_ips)
        print("IP Type:", self.ip_type)
