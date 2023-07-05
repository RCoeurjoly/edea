import nox


@nox.session(python=["3.11", "3.10"], venv_params=["--system-site-packages"])
def tests(session: nox.Session):
    session.run("poetry", "install", external=True)
    session.run("pytest", *session.posargs)
