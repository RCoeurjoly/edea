#!/usr/bin/env python

"""
Exit with 0 if the current version is the latest version in the docs directory.
"""

import os
import sys
from importlib.metadata import distribution

from packaging import version as semver


def main():
    dir_path = sys.argv[1] if len(sys.argv) > 1 else "public"
    current_version = distribution("edea").metadata["version"]
    versions = [
        dir
        for dir in os.listdir(dir_path)
        if os.path.isdir(os.path.join(dir_path, dir)) and dir != "latest"
    ]
    for version in versions:
        if semver.parse(version) > semver.parse(current_version):
            return False

    return True


if __name__ == "__main__":
    if main():
        sys.exit(0)
    else:
        sys.exit(1)
