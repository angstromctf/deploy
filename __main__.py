import os
import argparse
import importlib
import collections
import json

init = os.path.join(os.path.dirname(os.path.abspath(__file__)), "__init__.py")
deploy = importlib.import_module("__init__", init)

parser = argparse.ArgumentParser()
subparsers = parser.add_subparsers(dest="command", metavar="command")

search_parser = subparsers.add_parser("search", help="search for problems in a directory")
search_parser.add_argument("path", help="the path to search")

export_parser = subparsers.add_parser("export", help="export problems to a JSON file")
export_parser.add_argument("path", help="the path to search")
export_parser.add_argument("out", help="the JSON file path to write to")
export_parser.add_argument("--url", help="URL to point static CTF files to", default=os.environ.get("CTF_URL", ""))


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


if namespace.command == "export":

    print("\nExporting...")
    problems = deploy.search(namespace.path)
    out = []
    url = namespace.url
    count = 0
    for problem in problems:
        if problem.enabled:
            out.append(problem.export(url=namespace.url))
            count += 1
    with open(namespace.out, "w") as file:
        json.dump(out, file, indent=4)
    print("Exported {} problems to {}.".format(count, namespace.out))
