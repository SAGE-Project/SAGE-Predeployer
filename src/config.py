import os
import logging
import platform

current_dir = os.path.abspath(os.path.dirname(__file__))
root_dir = os.path.abspath(os.path.join(current_dir, ".."))


def configure_logging(level=logging.INFO):
    """configure logging module"""
    logging.basicConfig(
        level=level,
        format="%(asctime)s: %(levelname)7s: [%(name)s]: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )


class Config:
    INPUT_FILE = (
        f"{root_dir}/input/schema.json"
        if platform.system() != "Windows"
        else f"{root_dir}\\input\\schema.json"
    )
    TEMPLATE_DIR = (
        f"{root_dir}/templates/"
        if platform.system() != "Windows"
        else f"{root_dir}\\templates\\"
    )
    OUTPUT_DIR = (
        f"{root_dir}/output/sage/"
        if platform.system() != "Windows"
        else f"{root_dir}\\output\\sage\\"
    )
    OUTPUT_DIR_K8S = (
        f"{root_dir}/output/k8s/"
        if platform.system() != "Windows"
        else f"{root_dir}\\output\\k8s\\"
    )
    OUTPUT_DIR_BOREAS = (
        f"{root_dir}/output/boreas/"
        if platform.system() != "Windows"
        else f"{root_dir}\\output\\boreas\\"
    )
