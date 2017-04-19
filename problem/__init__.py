import os
import yaml
import markdown

from .doquer import DockerProblem
from .base import Problem


REQUIRED = {
    "name": str,
    "value": int,
    "text": markdown.markdown,
    "hint": markdown.markdown,
    "flag": str}
OPTIONAL = {
    "author": str}


def load(category: str, path: str) -> Problem or None:
    """Load a problem from its directory."""

    directory = os.path.dirname(path)
    reference = os.sep.join(directory.split(os.sep)[-2:])
    config = {"category": category}

    with open(path) as file:
        raw = yaml.load(file)

    for field, cast in REQUIRED.items():
        if field not in raw or raw[field] is None:
            print("Problem missing name in {}.".format(reference))
            return None
        config[field] = cast(raw[field])

    for field, cast in OPTIONAL.items():
        if field in raw:
            config[field] = cast(raw[field])

    if "files" in raw:
        files = raw["files"]
        if not isinstance(files, list):
            print("Problem files for {} are not in list format.".format(reference))
            return None
        for file in files:
            file = str(file)
            if not os.path.isfile(os.path.join(directory, file)):
                print("Problem file not found in {}: {}".format(reference, file))
                return None
        config["files"] = files

    if raw.get("enabled") is False:
        config["enabled"] = False

    return Problem(**config)
