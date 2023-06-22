from kubernetes import client, config


# config.load_kube_config()
# v1 = client.CoreV1Api()


class VmType:
    def __init__(self, data):
        self.name = list(data.keys())[0] if data else None
        self.id = data.get(self.name, {}).get("id", None)
        self.cpu = data.get(self.name, {}).get("cpu", None)
        self.memory = data.get(self.name, {}).get("memory", None)
        self.storage = data.get(self.name, {}).get("storage", None)
        self.operating_system = data.get(self.name, {}).get("operatingSystem", None)
        self.price = data.get(self.name, {}).get("price", None)

    def print_vm_details(self):
        print("VM Name:", self.name)
        print("CPU:", self.cpu)
        print("Memory:", self.memory)
        print("Storage:", self.storage)
        print("Operating System:", self.operating_system)
        print("Price:", self.price)


class VM:
    def __init__(self, index, vm_type: VmType):
        self.index = index
        self.type = vm_type
