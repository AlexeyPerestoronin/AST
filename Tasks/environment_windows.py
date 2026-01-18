import commandcript


@commandcript.script_task()
def prepare(ctx):
    """
    Preparing OS (Windows) for the Project development
    """

    command = []

    commandcript.ScriptExecutor(ctx.script_dir, False)\
        .add_command(command)\
        .execute("environment-prepare.log")