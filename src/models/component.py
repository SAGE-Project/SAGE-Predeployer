import yaml
import jinja2

from src.config import Config


class Component:
    def __init__(self, data):
        self.id = data.get("id", None)
        self.name = data.get("name", "").lower().replace(" ", "-").replace(".", "-")

        self.compute = {
            "cpu": data.get("Compute", {}).get("CPU", 0),  # 1000m
            "gpu": data.get("Compute", {}).get("GPU", None),
            "memory": data.get("Compute", {}).get("Memory", 0),  # memory in Mi
        }
        if (
            not self.compute["cpu"]
            and not self.compute["gpu"]
            and not self.compute["memory"]
        ):
            self.compute = None

        self.storage = {
            "type": data.get("Storage", {}).get("StorageType", None),
            "size": data.get("Storage", {}).get("StorageSize", 0) // 1000,
        }
        if not self.storage["type"] and self.storage["size"] == "0":
            self.storage = None

        self.network = data.get("Network", None)
        self.keywords = data.get("keywords", None)
        # self.operating_system = data.get("operatingSystem", None)
        self.operating_system = "k8s.gcr.io/pause:2.0"

        self.preferences = data.get("preferences", None)

        self.conflicts = []
        self.full_deployment = False
        self.collocations = []

        self.nodes = []

    def render_jinja(self, template_file, options=None):
        if options is None:
            options = {}

        template_loader = jinja2.FileSystemLoader(searchpath=Config.TEMPLATE_DIR)
        template_env = jinja2.Environment(loader=template_loader)
        template = template_env.get_template(template_file)

        rendered_template = template.render({"obj": self, "options": options})
        parsed_yaml = yaml.safe_load(rendered_template)
        return yaml.dump(parsed_yaml)

    @classmethod
    def find_component_by_id(cls, id, components):
        for component in components:
            if component.id == id:
                return component

    def print_component_details(self):
        print("Component ID:", self.id)
        print("Component Name:", self.name)
        print("Compute:", self.compute)
        print("Storage:", self.storage)
        print("Network:", self.network)
        print("Keywords:", self.keywords)
        print("Conflicts:", self.conflicts)
