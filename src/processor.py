import os
import json
import logging
from pathlib import Path

from src.infra_manager import InfraManager
from src.config import Config
from src.models.vm import VmType, VM
from src.models.network import Network
from src.models.component import Component
from src.models.restrictions import (
    Restriction,
    Conflicts,
    LowerBound,
    UpperBound,
    EqualBound,
    FullDeployment,
    RequireProvide,
    OneToOneDependency
)

logger = logging.getLogger(__name__)

MODELS = {
    "name": "",
    "components": [],  # type: Component
    "network": [],  # type: Network
    "restrictions": [],  # type: Restriction
    "vms_types": [],  # type: VmType
    "vms": [],  # type: VM
    "assign_matrix": [],
}


def _get_vm_type(id):
    for vm in MODELS["vms_types"]:
        if vm.id == id:
            return vm


def _clear_dir(directory):
    for filename in os.listdir(directory):
        file_path = os.path.join(directory, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
        except Exception as e:
            print('Failed to delete %s. Reason: %s' % (file_path, e))


def input_to_models():
    with open(Config.INPUT_FILE, "r") as json_file:
        data = json.load(json_file)

    MODELS["name"] = data["application"]
    parse_components(data)
    parse_network(data)
    parse_restriction(data)
    parse_vms(data)
    parse_vm_distribution(data)


def parse_vm_distribution(data):
    MODELS["assign_matrix"] = data["output"]["assign_matr"]

    # assign components to vms
    for i in range(len(MODELS["assign_matrix"])):
        for j in range(len(MODELS["assign_matrix"][i])):
            if MODELS["assign_matrix"][i][j] == 1:
                MODELS["components"][i].nodes.append(j)

    MODELS["assign_matrix"].insert(0, data["output"]["types_of_VMs"])


def parse_components(data):
    # load components
    for component_data in data["components"]:
        MODELS["components"].append(Component(component_data))

    logger.info(f"Loaded {len(MODELS['components'])} components models")


def parse_network(data):
    # load ips
    MODELS["network"].append(Network(data["IP"]))
    logger.info(f"Loaded {len(MODELS['network'])} network models")


def parse_vms(data):
    # parse output
    if "output" not in data.keys():
        raise Exception("No result found in the input file")

    # for vm_data in data["output"]["VMs specs"]:
    for vm_data in data["output"]["VMs specs"]:
        MODELS["vms_types"].append(VmType(vm_data))

    logger.info(f"Loaded {len(MODELS['vms_types'])} vms types")

    # load vm data["output"]["types_of_VMs"]
    for i, vm_type_id in enumerate(data["output"]["types_of_VMs"]):
        vm_type = _get_vm_type(vm_type_id)
        MODELS["vms"].append(VM(i, vm_type))

    logger.info(f"Loaded {len(MODELS['vms'])} vms")


def parse_restriction(data):
    # load restrictions
    for item in data["restrictions"]:
        if item["type"] == "Conflicts":
            conflict = Conflicts(item)
            MODELS["restrictions"].append(conflict)
            alpha_component = Component.find_component_by_id(conflict.alpha_comp_id, MODELS["components"])

            for comp_id in conflict.comps_id_list:
                comp = Component.find_component_by_id(comp_id, MODELS["components"])
                alpha_component.conflicts.append(comp.name)

        elif item["type"] == "EqualBound":
            MODELS["restrictions"].append(EqualBound(item))
        elif item["type"] == "LowerBound":
            MODELS["restrictions"].append(LowerBound(item))
        elif item["type"] == "UpperBound":
            MODELS["restrictions"].append(UpperBound(item))
        elif item["type"] == "FullDeployment":
            full_depl = FullDeployment(item)
            MODELS["restrictions"].append(full_depl)
            alpha_component = Component.find_component_by_id(full_depl.alpha_comp_id, MODELS["components"])
            alpha_component.full_deployment = True
            alpha_component.conflicts.append(alpha_component.name)

        elif item["type"] == "RequireProvide" or item["type"] == "RequireProvideDependency":
            MODELS["restrictions"].append(RequireProvide(item))
        elif item["type"] == "AlternativeComponents":
            pass
        elif item["type"] == "OneToManyDependency":
            pass
        elif item["type"] == "OneToOneDependency":
            # Collocation
            collocation = OneToOneDependency(item)
            MODELS["restrictions"].append(collocation)

            alpha_component = Component.find_component_by_id(collocation.alpha_comp_id, MODELS["components"])
            beta_component = Component.find_component_by_id(collocation.beta_comp_id, MODELS["components"])

            alpha_component.collocations.append(beta_component.name)
        else:
            raise Exception(f"Unknown restriction: {item}")
    logger.info(f"Loaded {len(MODELS['restrictions'])} restriction models")


def models_to_kubernetes():
    i = 1
    path = f"{Config.OUTPUT_DIR}{MODELS['name']}"
    Path(path).mkdir(parents=True, exist_ok=True)
    _clear_dir(path)

    for component in MODELS["components"]:
        if not len(component.nodes): continue

        yaml = component.render_jinja("deployment.yaml.j2")

        with open(f"{path}/{i}_{component.name}.yaml", "w+") as f:
            f.write(yaml)
        i += 1

    logger.info("Transformed SAGE models to yaml k8s objects")

    i = 1
    path = f"{Config.OUTPUT_DIR_K8S}{MODELS['name']}"
    Path(path).mkdir(parents=True, exist_ok=True)
    _clear_dir(path)

    for component in MODELS["components"]:
        if not len(component.nodes): continue

        yaml = component.render_jinja("raw_deployment.yaml.j2")

        with open(f"{path}/{i}_{component.name}.yaml", "w+") as f:
            f.write(yaml)
        i += 1

    logger.info("Written raw k8s files")

    i = 1
    path = f"{Config.OUTPUT_DIR_BOREAS}{MODELS['name']}"
    Path(path).mkdir(parents=True, exist_ok=True)
    _clear_dir(path)

    # Boreas reduction 100m CPU
    value = 100 // len(MODELS["components"])
    for component in MODELS["components"]:
        if not len(component.nodes): continue

        yaml = component.render_jinja("raw_deployment.yaml.j2", {"boreas": True, "cpu_reduction": value})

        with open(f"{path}/{i}_{component.name}.yaml", "w+") as f:
            f.write(yaml)
        i += 1

    logger.info("Written Boreas files")


def run():
    input_to_models()
    InfraManager(MODELS).deploy_digital_ocean_cluster()
    models_to_kubernetes()
