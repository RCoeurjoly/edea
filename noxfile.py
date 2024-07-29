import nox


@nox.session(python=["3.10", "3.12"], venv_params=["--system-site-packages"])
def tests(session: nox.Session):
    session.run("poetry", "install", external=True)
    # Reset the modules after tests
    session.run("git", "restore", "tests/kicad_projects", external=True)
    session.run("git", "clean", "-fd", "tests/kicad_projects", external=True)
    session.run("pytest", *session.posargs)
