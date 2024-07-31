import nox


def test_report_params(session: nox.Session) -> list[str]:
    if session.python != "3.12":
        return []
    is_doc_test = "--doctest-modules" in session.posargs
    junit_file = "doc-test-junit.xml" if is_doc_test else "junit.xml"
    test_report_params = ["--junitxml", junit_file]
    return test_report_params


@nox.session(python=["3.10", "3.12"], venv_params=["--system-site-packages"])
def tests(session: nox.Session):
    session.run("poetry", "install", external=True)
    # Reset the modules after tests
    session.run("git", "restore", "tests/kicad_projects", external=True)
    session.run("git", "clean", "-fd", "tests/kicad_projects", external=True)
    session.run("pytest", *test_report_params(session), *session.posargs)
