#!/usr/bin/python2

import os
import re
import sys
import shlex
import subprocess

GIT_BINS_PATH = "/usr/bin/" # also "/usr/local/git/bin/"

SSH_ORIGINAL_COMMAND = os.environ.get("SSH_ORIGINAL_COMMAND")

sys.stdout.write(SSH_ORIGINAL_COMMAND)
sys.stdout.write(str(sys.argv))

# ACL WITH REPOSITORY
def get_permission(username, repository):
    """Get the permissions "R" or "W" for the user on a given repository"""
    # TODO
    return "R" # "W"

if SSH_ORIGINAL_COMMAND is None:
    sys.stderr.write("SSH not allowed to the git account.")
    sys.exit(1)

if len(sys.argv) != 2:
    sys.stderr.write("Authorised keys file misconfigured, username not specified correctly.")
    sys.exit(1)

username = sys.argv[1]

if not re.match(r"^[A-Za-z0-9]+$", username):
    sys.stderr.write("Authorised keys file misconfigured, username contains invalid characters: " + username)
    sys.exit(1)

commands_regex = [r"^git[ -]upload-archive", r"^git[ -]upload-pack", r"^git[ -]receive-pack"]

if not any(map(lambda x: re.match(x, SSH_ORIGINAL_COMMAND), commands_regex)):
    sys.stderr.write("Only git commands are allowed.")
    sys.exit(1)

repository = " ".join(SSH_ORIGINAL_COMMAND.split(" ")[1:])

if not re.match(r'.*', repository):
    sys.stderr.write("Repository parameter incorrect.")
    sys.exit(2)

perms =  get_permission(username, repository)

if ((perms == "R" and re.match(r"^git[ -]upload-pack", SSH_ORIGINAL_COMMAND)) or
    perms == "W"):
    sys.stderr.flush()

    retcode = subprocess.call(shlex.split(GIT_BINS_PATH + SSH_ORIGINAL_COMMAND.replace("/", "")),
                             env={"GIT_SHELL_REPOSITORY": repository})
    if retcode == 0:
       sys.exit(0)

sys.stderr.write("You do not have permission to complete this operation")
sys.exit(5)
