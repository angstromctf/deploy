import os
import yaml
import typing

from . import problem


def search(path: str) -> typing.List[problem.HostedProblem]:
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
    for category in os.listdir(path):
        if category.startswith("_"):
            continue
        category_path = os.path.join(path, category)
        for problem in os.listdir(category_path):
            problem_path = os.path.join(category_path, problem)
            problem_file_path = os.path.join(problem_path, "problem.yml")
            if os.path.isfile():
                with open(problem_file_path) as file:
                    config = yaml.load(file)
                problems.append(problem.load(config))
