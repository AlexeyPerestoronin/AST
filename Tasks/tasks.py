import os
import pathlib

import invoke
import commandcript
from commandcript import ENV_CONTEXT


ENV_CONTEXT\
    .add_env_var('PROJECT_GIT_DIR', f'{__file__}/../../')\
    .add_env_var('TASKS_DIR', f'{ENV_CONTEXT.PROJECT_GIT_DIR}/Tasks')\
    .add_env_var('COMMANDSCRIPT_SCRIPT_DIR', f'{ENV_CONTEXT.PROJECT_GIT_DIR}/.generated')\


@commandcript.script_task()
def get_info(ctx):
    """
    Print to console information about active configuration of invoke-tasks
    """
    from prettytable import PrettyTable

    table = PrettyTable()
    table.align = "l"
    table.field_names = ["ENV-name", "ENV-value"]
    for key, value in ENV_CONTEXT.items():
        table.add_row([key, value])

    commandcript.INFO\
        .log_line("Active environment configuration:") \
        .log_line(f"{table}")


@commandcript.script_task()
def yapf(ctx):
    """
    Format python files with script-tasks
    """

    def collect_file(dir):
        files = []
        for item in os.listdir(dir):
            item = pathlib.Path(os.path.join(f'{dir}', item))
            if item.is_file():
                if item.name.endswith('.py'):
                    files.append(f'"{item.as_posix()}"')
            elif item.is_dir():
                if not item.name.startswith('.'):
                    files.extend(collect_file(f'{item.as_posix()}'))
        return files

    commandcript.ScriptExecutor(ctx.script_dir, ctx.launch)\
        .add_cwd(ENV_CONTEXT.PROJECT_GIT_DIR)\
        .add_command([
                f'yapf',
                f'--style {ENV_CONTEXT.TASKS_DIR}/.style.yapf',
                f'--verbose',
                f'--in-place',
                *collect_file(f'{ENV_CONTEXT.PROJECT_GIT_DIR}')
            ])\
        .execute(log='yapf.log')


namespace = invoke.Collection()
namespace.add_task(get_info, name="get-info")
namespace.add_task(yapf, name="yapf")

if os.name == "nt":
    import environment_windows as environment
elif os.name == "posix":
    import environment_linux as environment
else:
    raise Exception("unsupported operation system!")

namespace.add_collection(invoke.Collection.from_module(environment, name="environment"))

import project

namespace.add_collection(project.collection)
