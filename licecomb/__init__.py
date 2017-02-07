#!/usr/bin/env python
from __future__ import print_function, division, absolute_import, unicode_literals
import github
import argparse
import sys
import xml.etree.ElementTree as ET



# TODO Put this somewhere better
import os
gh = github.Github(
    login_or_token=os.environ.get('GITHUB_USERNAME', None) or os.environ.get('GITHUB_OAUTH_TOKEN', None),
    password=os.environ.get('GITHUB_PASSWORD', None),
)


def licecomb(owner, repository_names, **options):
    repositories = get_repositories(owner, repository_names)

    status = {}
    for repository in repositories:
        if options['ignore_forks'] and repository.fork:
            continue

        sys.stderr.write("Checking %s\n" % repository.name)
        status[repository.name] = (
            repository_has_license(repository),
            repository_has_readme(repository)
        )

    return status


def get_repositories(owner, repository_names):
    for repo in gh.get_user(owner).get_repos():
        yield repo

def repository_has_readme(repository):
    try:
        repository.get_file_contents('README.md')
        return True
    except Exception:
        try:
            repository.get_file_contents('README.rst')
            return True
        except Exception:
            return False

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

    passing = 0
    failing = 0

    root = ET.Element("testsuite", name='licecomb', tests=str(passing + failing), errors=str(failing), failures="0", skip="0")
    className = 'licecomb.%s' % args.owner
    for repo in status:
        has_license, has_readme = status[repo]
        license_test = ET.SubElement(root, 'testcase', classname=className + '.license', name=repo, time='0')

        if not has_license:
            ET.SubElement(license_test, 'error', type='exceptions.MissingLicense', message='Repository is missing a LICENSE')

        readme_test = ET.SubElement(root, 'testcase', classname=className + '.readme', name=repo, time='0')
        if not has_readme:
            ET.SubElement(readme_test, 'error', type='exceptions.MissingReadme', message='Repository is missing a README.md')

    tree = ET.ElementTree(root)
    tree.write('xunit.xml')


    sys.exit(0)

if __name__ == '__main__':
    main()
