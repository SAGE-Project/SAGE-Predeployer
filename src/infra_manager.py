import logging
import random
import subprocess
from time import sleep

from kubernetes import client, config

logger = logging.getLogger(__name__)


class InfraManager:
    def __init__(self, models):
        self.models = models
        self.pools = self._create_vm_pools()

    def deploy_digital_ocean_cluster(self):
        pools_args = ""

        for pool in self.pools:
            count = len(self.pools[pool])
            pools_args += f'--node-pool "name={pool}-pool;size={pool};count={count}" '

        command = (
            f"doctl kubernetes cluster create sage-{random.randint(1,10)} --region fra1 {pools_args}".strip()
        )
        logger.info(f"Executing command: {command}")
        logger.info(subprocess.check_output(command.split()))
        logger.info("Waiting 60 sec for the cluster to become online...")
        sleep(60)

        self.label_nodes()

    def label_nodes(self):
        for pool in self.pools:
            nodes_indexes = [node.index for node in self.pools[pool]]
            for node in self._get_nodes(f"node.kubernetes.io/instance-type={pool}"):
                self.add_node_label(node, "index", str(nodes_indexes.pop()))

    def _create_vm_pools(self):
        pools = {}

        for vm in self.models["vms"]:
            if vm.type.name in pools:
                pools[vm.type.name].append(vm)
            else:
                pools[vm.type.name] = [vm]

        return pools

    def _get_nodes(self, label_selector):
        config.load_kube_config()
        v1 = client.CoreV1Api()
        nodes = v1.list_node(label_selector=label_selector).items
        return [node.metadata.name for node in nodes]

    def add_node_label(self, node_name: str, label_key: str, label_value: str):
        config.load_kube_config()
        v1 = client.CoreV1Api()
        logger.info(f"Adding label {label_key}:{label_value} for {node_name}")
        node = v1.read_node(node_name)
        node_labels = node.metadata.labels or {}
        node_labels[label_key] = label_value
        patch = {"metadata": {"labels": node_labels}}
        v1.patch_node(node_name, patch)
