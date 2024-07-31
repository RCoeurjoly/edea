import os
import re
import subprocess
import sys
from json import dump

from packaging import version as semver


def get_versions_from_pypi() -> list[str]:
    output = subprocess.run(
        [sys.executable, "-m", "pip", "index", "versions", "edea"], capture_output=True
    )
    m = re.findall(r"Available versions: (.+)\n", output.stdout.decode("utf-8"))
    assert len(m) == 1
    versions = m[0].split(", ")
    return versions


def get_versions():
    dir_path = "public"
    return [
        dir
        for dir in os.listdir(dir_path)
        if os.path.isdir(os.path.join(dir_path, dir)) and dir != "latest"
    ]


def version_label(version: str) -> str:
    if version not in published_versions:
        return f"{version} (rc)"
    if version == sorted_versions[0]:
        return f"{version} (latest)"
    return version


published_versions = get_versions_from_pypi()
sorted_versions = sorted(get_versions(), key=semver.parse, reverse=True)

sorted_versions_urls = [
    {
        "key": version_label(version),
        "url": f"https://edea-dev.gitlab.io/edea/{version}",
    }
    for i, version in enumerate(sorted_versions)
]

with open(sys.argv[1], "w") as f:
    dump(sorted_versions_urls, f, indent=4)
