from logging import Logger
from sys import exit

import ansible_runner as ansible
import click
from ansible_runner import Runner
from openbsd_run.playbook import path as playbook_path
from openbsd_run.utils.log import Log


@click.command(name="pkg_add", short_help="Add or update packages")
@click.option(
    "-D",
    default="",
    help="Force package install, waiving the specified failsafe",
    type=str,
)
@click.option(
    "-u",
    default=False,
    help="Update named packages, installing any missing packages",
    is_flag=True,
    type=bool,
)
@click.argument("packages", required=False)
@click.pass_context
def pkg_add(context, d: str, packages: list[str], u: bool) -> None:
    log: Logger = Log("openbsd-run: pkg")

    extra_vars: dict = {}
    host_pattern = context.obj["host_pattern"]
    inventory_contents: dict = context.obj["inventory_contents"]
    quiet: bool = context.obj["quiet"]
    verbose: bool = context.obj["verbose"]

    if d and d not in [
        "allversions",
        "arch",
        "checksum",
        "dontmerge",
        "donttie",
        "downgrade",
        "installed",
        "nonroot",
        "paranoid",
        "repair",
        "scripts",
        "SIGNER",
        "snap",
        "snapshot",
        "unassigned",
        "updatedepends",
    ]:
        log.error("'%s' is not a valid failsafe to waive.")
        exit(1)

    if d:
        extra_vars["pkg_force"] = d

    if packages:
        extra_vars["pkg_packages"] = packages

    if u:
        extra_vars["pkg_state"] = "latest"
    else:
        extra_vars["pkg_state"] = "present"

    result: Runner = ansible.run(
        extravars=extra_vars,
        inventory=inventory_contents,
        limit=host_pattern,
        playbook="%s/site-pkg.yml" % playbook_path,
        project_dir=playbook_path,
        quiet=quiet,
        suppress_ansible_output=True,
        verbosity=3 if verbose else None,
    )

    if result.rc != 0 or result.errored or result.canceled:
        log.error("update failed!")
        exit(1)
