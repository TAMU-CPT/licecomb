#!/usr/bin/env python
from __future__ import print_function, division, absolute_import, unicode_literals
from github import Github
import argparse
import sys



# TODO Put this somewhere better
import os
gh = Github(
    login_or_token=os.environ.get('GITHUB_USERNAME', None) or os.environ.get('GITHUB_OAUTH_TOKEN', None),
    password=os.environ.get('GITHUB_PASSWORD', None),
)


def licecomb(owner, repository_names, **options):
    repositories = get_repositories(owner, repository_names)

    status = {}
    for repository in repositories:
        if options['ignore_forks'] and repository.fork:
            continue
        status[repository.name] = repository_has_license(repository)

    status2 = {True: [], False: []}
    for (repository_name, has_license) in status.items():
        status2[has_license].append(repository_name)

    return status2


def get_repositories(owner, repository_names):
    # if repository_names:
        # repositories = []
        # not_found = []
        # for repository_name in repository_names:
            # repository = gh.repository(owner, repository_name)
            # if repository:
                # repositories.append(repository)
            # else:
                # not_found.append(repository_name)
        # if not_found:
            # raise ValueError("Could not find repositories %s" % ", ".join(["%s/%s" % (owner, repository_name) for repository_name in not_found]))
    # else:
    for repo in gh.get_user(owner).get_repos():
        yield repo


def repository_has_license(repository):
    try:
        repository.get_file_contents('LICENSE')
        return True
    except Exception:
        return False


def main():
    parser = argparse.ArgumentParser(description="Check GitHub repositories for license files")
    parser.add_argument("--verbose", "-v", action="store_true")
    parser.add_argument("--ignore-forks", action="store_true")
    parser.add_argument("owner", nargs=1)
    parser.add_argument("repository_names", nargs="*", metavar="repository")
    args = parser.parse_args()

    args.owner = args.owner[0] # http://docs.python.org/2.7/library/argparse.html#nargs - "Note that nargs=1 produces a list of one item."
    status = licecomb(**vars(args))

    if args.verbose and True in status:
        for repository_name in status[True]:
            print("SUCCESS: Found a license file in %s/%s" % (args.owner, repository_name))
    if False in status:
        for repository_name in status[False]:
            print("ERROR: Could not find a license file in %s/%s" % (args.owner, repository_name), file=sys.stderr)
        sys.exit(1)

    sys.exit(0)

if __name__ == '__main__':
    main()
