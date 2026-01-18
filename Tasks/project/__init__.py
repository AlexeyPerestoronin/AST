import invoke
import commandcript

import os
if os.name == "nt":
    from . import core_windows as core
elif os.name == "posix":
    from . import core_linux as core
else:
    raise Exception("unsupported operation system!")


@commandcript.script_task(
    help={
        "param1": "boolean parameter",
        "param2": "text parameter",
        "param3": "digit parameter",
        "arg": "list argument - can be used multiple times in CLI",
    },
    iterable=["arg"],
)
def full_check(ctx, param1=False, param2="default text", param3=8, arg=None):
    """
    Project full check (template of combined task)!
    """
    core.task(ctx, script_dir=ctx.script_dir, launch=ctx.launch, param1=param1, param2=param2, param3=param3, arg=arg)


collection = invoke.Collection("project")
collection.add_task(full_check, name="full-check")
collection.add_collection(invoke.Collection.from_module(core, name="core"))
