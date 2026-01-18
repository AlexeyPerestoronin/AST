import commandcript


def activate_VS2019_environment():
    return [
        "call",
        "\"C:/Program Files (x86)/Microsoft Visual Studio/2019/Community/Common7/Tools/vsdevcmd\"",
        "-arch=x64",
    ]


@commandcript.script_task(
    help={
        "param1": "boolean parameter",
        "param2": "text parameter",
        "param3": "digit parameter",
        "arg": "list argument - can be used multiple times in CLI",
    },
    iterable=["arg"],
)
def task(ctx, param1=False, param2="default text", param3=8, arg=None):
    """
    Task template (on windows)!
    """

    command = [
        "echo",
        f"param1={param1}",
        f"param2={param2}",
        f"param3={param3}",
    ]

    if arg:
        for a in arg:
            command.append(f"arg={a}")

    commandcript.ScriptExecutor(ctx.script_dir, ctx.launch)\
        .add_command(activate_VS2019_environment())\
        .add_command(command).execute("project-task.log")
