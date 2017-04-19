import abc


class AbstractProblem(abc.ABC, metaclass=abc.ABCMeta):
    """Base class for a problem hosted on the server."""

    @abc.abstractmethod
    def export(self):
        """Export to a simple format for the main server."""

    @abc.abstractmethod
    def deploy(self):
        """Deploy the problem to the server."""


class Problem(AbstractProblem):
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

    def deploy(self):
        return
