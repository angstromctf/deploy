import os
import yaml
import markdown
import typing


REQUIRED = {
    "name": str,
    "value": int,
    "text": markdown.markdown,
    "hint": markdown.markdown,
    "flag": str}
OPTIONAL = {
    "author": str}


class Problem:
    """Default problem with an empty deployment method."""

    def __init__(self, **config):
        """Initialize the problem based on the configuration."""

        self.name = config["name"]
        self.category = config["category"]
        self.value = int(config["value"])
        self.text = config["text"]
        self.hint = config["hint"]
        self.flag = config["flag"]
        self.author = config.get("author")
        self.files = config.get("files")
        self.enabled = config.get("enabled", True)

    def export(self):
        pass

    def deploy(self, *args, **kwargs):
        pass


class DockerProblem(Problem):
    """Docker wrapper for isolated problems."""

    def __init__(self, **config):
        """Initialize a docker problem."""

        super().__init__(**config)
        print("Created a docker problem.")


class ShellProblem(Problem):
    """Shell problem model."""

    def __init__(self, **config):
        """Initialize a shell problem."""

        super().__init__(**config)
        print("Created a shell problem.")

    def deploy(self, path: str):
        """Deploy the problem to a directory."""

        pass


PROBLEM = {
    "docker": DockerProblem,
    "shell": ShellProblem,
}


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

    cast = Problem
    if "deploy" in raw:
        if type(raw["deploy"]) == dict:
            if "type" in raw["deploy"]:
                if raw["deploy"]["type"] in PROBLEM:
                    cast = PROBLEM[raw["deploy"]["type"]]
                else:
                    print("Invalid deploy type {} in {}.".format(raw["deploy"]["type"], reference))
                    return None
            else:
                print("No type specified in deploy in {}.".format(reference))
                return None

    return cast(**config)


def search(directory: str) -> typing.List[Problem]:
    """Parse the problems in a problem directory path.

    The parse command searches all files in the second level of the
    specified directory for `problem.yml` files, as the expected file
    structure is:

    path/
      category/
        problem/
          problem.yml

    Problems that are not enabled are still loaded, however further
    parsing is halted after this determination.
    """

    problems = []
    directory = os.path.abspath(os.path.normpath(directory))

    for category in os.listdir(directory):
        if category.startswith("_"):
            continue
        category_directory = os.path.join(directory, category)
        if not os.path.isdir(category_directory):
            continue
        for problem_name in os.listdir(category_directory):
            problem_directory = os.path.join(category_directory, problem_name)
            if not os.path.isdir(problem_directory):
                continue
            problem_path = os.path.join(problem_directory, "problem.yml")
            if os.path.isfile(problem_path):
                problem_object = load(category, problem_path)
                if problem_object:
                    problems.append(problem_object)

    return problems
