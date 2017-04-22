import os
import re
import yaml
import shutil
import markdown
import typing
import docker
import hashlib


REQUIRED = {"title": str, "value": int, "text": str, "hint": str, "flag": str}
OPTIONAL = {"author": str}


class Problem:
    """Default problem with an empty deployment method."""

    def __init__(self, directory: str, category: str, name: str, **config):
        """Initialize the problem based on the configuration."""

        self.directory = directory
        self.category = category
        self.name = name
        self.title = config["title"]
        self.value = int(config["value"])
        self.text = config["text"]
        self.hint = config["hint"]
        self.flag = config["flag"].strip()
        self.author = config.get("author")
        self.files = config.get("files")
        self.enabled = config.get("enabled", True)
        self.settings = config.get("deploy", {})

        self.replace = {}
        if self.files:
            for path in self.files:
                basename = os.path.basename(path)
                self.replace[os.path.basename(path)] = "/static/" + os.path.join(category, name, basename).replace(os.sep, "/")

    def export(self, url="", static=""):
        """Export to a model corresponding to the Django API."""

        text = self.text
        for path, to in self.replace.items():
            text = re.sub("\\{\\{\s*" + path + "\s*\\}\\}", url.rstrip("/") + to, text)
        text = markdown.markdown(text)
        hint = markdown.markdown(self.hint)

        if self.files:
            directory = os.path.join(static, self.category)
            to = os.path.join(directory, self.name)
            if not os.path.isdir(to):
                os.makedirs(to, exist_ok=True)
            print("Copying files to {}".format(to))
            for file in self.files:
                shutil.copy(file, to)

        return {
            "name": self.name,
            "title": self.title,
            "text": text,
            "value": self.value,
            "hint": hint,
            "category": self.category,
            "flag": hashlib.sha512(self.flag.encode()).hexdigest(),
            "enabled": self.enabled}

    def deploy(self, path: str):
        """Deploy a normal, static problem. Moves files."""

        pass


class DockerProblem(Problem):
    """Docker wrapper for isolated problems."""

    def __init__(self, directory: str, category: str, name: str, **config):
        """Initialize a docker problem."""

        super().__init__(directory, category, name, **config)
        #print("Created a docker problem.")

    def deploy(self, path: str):
        """Deploy the docker problem."""

        client = docker.DockerClient()
        name = self.category + "-" + self.name

        try:
            info = client.containers.get(name)
            for container in client.containers.list(filters={"ancestor": name}, all=True):
                container.remove(force=True)
            client.images.remove(name)
            print("Removed existing docker image and containers.")
        except Exception as e:
            print(e)

        response = client.images.build(path=self.directory, rm=True, tag=name, quiet=True)
        print("Built image.")

        client.containers.run(name, name=name, ports=self.settings["ports"], detach=True)
        print("Started container.")


class ShellProblem(Problem):
    """Shell problem model."""

    def __init__(self, directory: str, category: str, name: str, **config):
        """Initialize a shell problem."""

        super().__init__(directory, category, name, **config)
        #print("Created a shell problem.")

    def deploy(self, path: str):
        """Deploy the problem to a directory."""

        super().deploy(path)
        # Shell problems were installed manually


PROBLEM = {
    "docker": DockerProblem,
    "shell": ShellProblem,
}


def load(path: str) -> Problem or None:
    """Load a problem from its problem file path."""

    directory = os.path.dirname(path)
    reference = os.sep.join(directory.split(os.sep)[-2:])
    category, name = reference.split(os.sep)

    with open(path) as file:
        raw = yaml.load(file)
    
    config = {"deploy": raw.get("deploy")}

    for field, cast in REQUIRED.items():
        if field not in raw or raw[field] is None:
            print("Problem missing title in {}.".format(reference))
            return None
        config[field] = cast(raw[field])

    for field, cast in OPTIONAL.items():
        if field in raw:
            config[field] = cast(raw[field])

    if "files" in raw:
        files = []
        if not isinstance(raw["files"], list):
            print("Problem files for {} are not in list format.".format(reference))
            return None
        for file in raw["files"]:
            file = str(file)
            full = os.path.join(directory, file)
            if not os.path.isfile(full):
                print("Problem file not found in {}: {}".format(reference, file))
                return None
            files.append(full)
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

    return cast(directory, category, name, **config)


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
                problem_object = load(problem_path)
                if problem_object:
                    problems.append(problem_object)

    return problems
