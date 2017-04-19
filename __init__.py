import os
import typing
import importlib

problem = importlib.import_module("problem", "./problem")


def search(directory: str) -> typing.List[problem.Problem]:
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
                problem_object = problem.load(category, problem_path)
                if problem_object:
                    problems.append(problem_object)

    return problems
