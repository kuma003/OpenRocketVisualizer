"""rocket.py"""

import pygame as pg
import numpy as np
from pathlib import Path
import orhelper
import os
import glob
import tomllib
import requests


def import_ork_file(path: str):
    """
    Import OpenRocket file and return the rocket object.

    Args:
        path (Path): path to OpenRocket file.
    Returns:
        orhelper.Rocket: rocket object.
    """
    jar_path = os.environ.get("CLASSPATH")

    if jar_path is None or not Path(jar_path).exists():
        jar_path = glob.glob("*.jar")

        if jar_path:
            jar_path = jar_path[0]
        else:
            print("OpenRocket jar file not found. Downloading...")
            with open("settings.toml", "rb") as f:
                settings = tomllib.load(f)
                url = settings["openrocket"]["url"]
                response = requests.get(url)
                jar_path = url[url.rfind("/") + 1 :]
                with open(jar_path, "wb") as f:
                    f.write(response.content)
            print("Done.")

    with orhelper.OpenRocketInstance(jar_path) as instance:
        orh = orhelper.Helper(instance)

        # read file
        doc = orh.load_doc(path)
        sim = doc.getSimulation(0)
        opts = sim.getOptions()

        return doc
