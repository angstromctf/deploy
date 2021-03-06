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
export_parser.add_argument("static", help="static files directory")
export_parser.add_argument("--url", help="URL to point static CTF files to", default=os.environ.get("CTF_URL", ""))

docker_parser = subparsers.add_parser("docker", help="deploy docker problems")
docker_parser.add_argument("path", help="the path to search")

group = docker_parser.add_mutually_exclusive_group(required=True)
group.add_argument('--all', action='store_true')
group.add_argument('--problem')

namespace = parser.parse_args()

if namespace.command == "search":
    frequency = collections.Counter()

    print("\nSearch Issues\n" + "-"*30)
    problems = deploy.search(namespace.path)

    print("\nCurrent Problems\n" + "-"*30)
    for id, problem in problems.items():
        print(id)
        frequency[problem.category] += 1

    print("\nStatistics\n" + "-"*30)
    print("Total: {}".format(len(problems)))
    for category in frequency:
        print("  {}: {}".format(category.capitalize(), frequency[category]))


elif namespace.command == "export":
    print("\nSearching...")

    problems = deploy.search(namespace.path)

    out = []
    url = namespace.url
    count = 0

    print("\nDeploying...")

    for problem in problems.values():
        out.append(problem.export(url=namespace.url, static=namespace.static))
        count += 1

    with open(namespace.out, "w") as file:
        json.dump(out, file, indent=4)

    print("Exported {} problems to {}.".format(count, namespace.out))


elif namespace.command == "docker":
    print("\nSearching...")

    problems = deploy.search(namespace.path)

    print("\nDeploying...")

    if namespace.all:
        for problem in problems.values():
            if not problem.enabled or type(problem) != deploy.DockerProblem:
                continue
            try:
                problem.deploy()
                print("Deployed", problem.id)
            except Exception as e:
                print(e)
    else:
        problem = problems[namespace.problem]

        try:
            problem.deploy()
            print("Deployed", problem.id)
        except Exception as e:
            print(e)
