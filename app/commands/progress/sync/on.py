import json
import os

import click

from app.commands.check.git import git
from app.commands.check.github import github
from app.commands.progress.constants import (
    LOCAL_FOLDER_NAME,
    PROGRESS_REPOSITORY_NAME,
    STUDENT_PROGRESS_FORK_NAME,
)
from app.utils.click_utils import error, info, success, warn
from app.utils.gh_cli_utils import (
    clone,
    clone_with_custom_name,
    fork,
    get_https_or_ssh,
    get_repo_https_url,
    get_repo_ssh_url,
    get_username,
    has_fork,
)
from app.utils.git_cli_utils import add_remote
from app.utils.gitmastery_utils import (
    GITMASTERY_CONFIG_NAME,
    generate_cds_string,
    require_gitmastery_root,
)


@click.command()
@click.pass_context
def on(ctx: click.Context) -> None:
    """
    Enables sync between your local progress and remote progress.
    """
    verbose = ctx.obj["VERBOSE"]

    gitmastery_root_path, cds, gitmastery_config = require_gitmastery_root()
    if cds != 0:
        error(
            f"Use {click.style('cd ' + generate_cds_string(cds), bold=True, italic=True)} the root of the Git-Mastery exercises folder to sync your progress."
        )

    ctx.invoke(git)
    ctx.invoke(github)

    info("Syncing progress tracker")
    info(
        f"Checking if you have fork of {click.style(PROGRESS_REPOSITORY_NAME, bold=True, italic=True)}"
    )

    username = get_username(verbose)
    fork_name = STUDENT_PROGRESS_FORK_NAME.format(username=username)

    if has_fork(fork_name, verbose):
        info("You already have a fork")
    else:
        warn("You don't have a fork yet, creating one")
        fork(PROGRESS_REPOSITORY_NAME, fork_name, verbose)

    info(
        f"Checking if you have a clone for {click.style(fork_name, bold=True, italic=True)}"
    )
    if os.path.isdir(LOCAL_FOLDER_NAME):
        info("You already have the progress repository cloned")
    else:
        warn("You don't have a clone of the progress repository yet, creating one")
        clone_with_custom_name(f"{username}/{fork_name}", LOCAL_FOLDER_NAME, verbose)

    os.chdir("progress")
    auth_type = get_https_or_ssh(verbose)
    if auth_type is None:
        error(
            "You should have been authenticated via HTTPS or SSH. Check your Github CLI installation"
        )

    origin_fork_url = (
        get_repo_ssh_url(fork_name, verbose)
        if auth_type == "ssh"
        else get_repo_https_url(fork_name, verbose)
    )
    if origin_fork_url is None:
        error("Fork URL should be present. Contact the Git-Mastery team.")

    assert origin_fork_url is not None
    add_remote("origin", origin_fork_url, verbose)

    upstream_fork_url = (
        "git@github.com:git-mastery/progress.git"
        if auth_type == "ssh"
        else "https://github.com/git-mastery/progress.git"
    )
    add_remote("upstream", upstream_fork_url, verbose)

    success("You have setup the progress tracker for Git-Mastery!")

    gitmastery_config["progress_remote"] = True
    with open(
        gitmastery_root_path / GITMASTERY_CONFIG_NAME, "w"
    ) as gitmastery_config_file:
        gitmastery_config_file.write(json.dumps(gitmastery_config))
