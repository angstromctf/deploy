import argparse
import importlib
import collections

deploy = importlib.import_module("__init__", "./__init__.py")

parser = argparse.ArgumentParser()
subparsers = parser.add_subparsers(dest="command", metavar="command")

search_parser = subparsers.add_parser("search", help="search for problems in a directory")
search_parser.add_argument("path", help="the path to search")


namespace = parser.parse_args()
if namespace.command == "search":
    frequency = collections.Counter()

    print("\nSearch Issues\n" + "-"*30)
    problems = deploy.search(namespace.path)

    print("\nCurrent Problems\n" + "-"*30)
    for problem in problems:
        print("{}/{}".format(problem.category, problem.name))
        frequency[problem.category] += 1

    print("\nStatistics\n" + "-"*30)
    print("Total: {}".format(len(problems)))
    for category in frequency:
        print("  {}: {}".format(category.capitalize(), frequency[category]))
