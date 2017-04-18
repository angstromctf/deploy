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

    def __init__(self, category: str, name: str, config: dict):
        """Initialize the problem based on the configuration."""

        indicator = "{}/{}".format(category, name)
        if "name" not in config:
            raise SyntaxError("Problem missing name in {}.".format(indicator))
        self.name = config["name"]

    def export(self):
        pass

    def deploy(self):
        return
