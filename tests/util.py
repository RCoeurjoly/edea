"""
Test utility methods.


SPDX-License-Identifier: EUPL-1.2
"""
import os


def get_path_to_test_file(file_path):
    test_folder = os.path.dirname(os.path.realpath(__file__))
    return os.path.join(test_folder, "kicad_projects", file_path)


def get_path_to_test_project(project_name, ext="kicad_sch"):
    file_path = os.path.join(project_name, f"{project_name}.{ext}")
    return get_path_to_test_file(file_path)


def get_test_output_dir():
    test_folder = os.path.dirname(os.path.realpath(__file__))
    test_output_dir = os.path.join(test_folder, "../temp-test-output")
    os.makedirs(test_output_dir, exist_ok=True)
    return test_output_dir
