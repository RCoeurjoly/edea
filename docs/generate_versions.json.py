import os
import sys
from json import dump

from packaging import version as semver


def get_versions():
    dir_path = "public"
    return [
        dir
        for dir in os.listdir(dir_path)
        if os.path.isdir(os.path.join(dir_path, dir)) and dir != "latest"
    ]


sorted_versions = sorted(get_versions(), key=semver.parse, reverse=True)

sorted_versions_urls = [
    {
        "key": f"{version}{' (latest)' if i == 0 else ''}",
        "url": f"https://edea-dev.gitlab.io/edea/{version}",
    }
    for i, version in enumerate(sorted_versions)
]

with open(sys.argv[1], "w") as f:
    dump(sorted_versions_urls, f, indent=4)
