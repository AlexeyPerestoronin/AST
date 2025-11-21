import os
import pandas
from invoke import task
from pathlib import Path


def get_env_context():
    """
    Gets table of env-variables needing for tasks launching
    """

    context = {"Env": [], "Val": []}

    def setup_dir_via_env(env_variable_name: str, default_value: str = None):
        ctx_attr = env_variable_name.lower()
        value = os.environ.get(env_variable_name)
        if not value:
            if default_value:
                value = Path(os.path.abspath(default_value)).as_posix()
            else:
                raise Exception(f"env-variable {env_variable_name} is not set!")
        else:
            value = Path(os.path.abspath(os.environ[env_variable_name])).as_posix()

        context["Env"].append(env_variable_name)
        context["Val"].append(value)

        return value

    # work-spaces
    fuzz_dir = setup_dir_via_env("FUZZ_DIR", f"{__file__}/../")
    git_dir = setup_dir_via_env("GIT_DIR", f"{fuzz_dir}/..")
    setup_dir_via_env("CURRENT_INSTANCE_LOG", f"{fuzz_dir}/.generated")

    # add here additional env-variables which will be available via ctx (context) on each task

    return pandas.DataFrame(context)


@task()
def setup_context(ctx):
    """
    Performs initial adjustment of invoke context before any tasks will running
    """

    context = get_env_context()

    for _idx, row in context.iterrows():
        attr_name = str(row["Env"]).lower()
        attr_value = str(row["Val"])
        setattr(ctx, attr_name, attr_value)
