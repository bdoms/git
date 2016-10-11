import os
import subprocess


def installed():
    """ detects if the system has git or not """
    try:
        subprocess.call(["git", "rev-parse"])
        return True
    except OSError:
        return False

def nonOptionArgs(args):
    return [arg for arg in args if not arg.startswith('-')]

def isRepository():
    output = subprocess.check_output(["git", "rev-parse", "--is-inside-work-tree"])
    return output.decode("utf-8").replace("\n", "") == "true"

def currentBranch():
    """ gets the name of the current branch """
    output = subprocess.check_output(["git", "rev-parse", "--abbrev-ref", "HEAD"])
    return output.decode("utf-8").replace("\n", "")

def currentUser():
    """ gets the name of the current git user """
    output = subprocess.check_output(['git', 'config', 'user.name'])
    return output.decode("utf-8").replace('\n', '')

def checkout(branch):
    """ returns True if successful, False if there was an error """
    # git is stupid and puts out the success message for the checkout command on stderr instead of stdout
    process = subprocess.Popen(["git", "checkout", branch], stderr=subprocess.PIPE)
    out, err = process.communicate()
    branch_switch = "Switched to branch '%s'" % branch
    branch_on = "Already on '%s'" % branch
    if branch_switch not in err and branch_on not in err:
        raise Exception("Could not switch to branch '%s'. Reason:\n%s" % (branch, err))

def commitDetails(formatting, commit_range):
    # see http://git-scm.com/book/ch2-3.html for formatting options
    output = subprocess.check_output(['git', 'log', '--pretty=format:"' + formatting + '"', commit_range])
    commits = output.decode("utf-8").split('\n')
    # each line is surrounded by quotes (e.g. '"1234 abcd"')
    return [commit[1:-1] for commit in commits]

def commitBody(long_sha):
    body = subprocess.check_output(['git', 'log', '--pretty=format:"%B"', '-n', '1', long_sha])
    # body is surrounded by quotes (e.g. '"commit message"')
    return body.decode("utf-8")[1:-1].strip()

def branchesWithCommit(long_sha, remote=False):
    command = ['git', 'branch']
    if remote:
        command.append('-r')
    command.extend(['--contains', long_sha])
    branches = []
    output = subprocess.check_output(command).decode("utf-8")
    if output:
        for line in output.split('\n'):
            branch = line.strip()
            if branch:
                branches.append(branch)
    return branches

def pushCommand():
    pid = os.getppid()
    output = subprocess.check_output(['ps', '-ocommand=', '-p', str(pid)])
    return output.decode("utf-8").strip()

def pushBranch():
    """ gets the name of the branch currently being pushed to """
    push_command = pushCommand()
    parts = nonOptionArgs(push_command.split(' '))
    if len(parts) > 3:
        branch = parts[3]
        if ':' in branch:
            source, branch = branch.split(':')
    else:
        branch = currentBranch()
    return branch

def pushForced():
    """ returns True if the push was forced, False otherwise """
    push_command = pushCommand()
    return ('--force' in push_command or '-f' in push_command)

def pushRemote():
    """ gets the name of the remote currently being pushed to """
    push_command = pushCommand()
    parts = nonOptionArgs(push_command.split(' '))
    if len(parts) > 2:
        remote = parts[2]
    else:
        # the remote was not included in the command so we check the configuration
        command = ['git', 'rev-parse', '--abbrev-ref', '--symbolic-full-name', '@{u}']
        output = subprocess.check_output(command).decode("utf-8").replace('\n', '')
        if 'fatal: ' not in output:
            remote = output.split('/')[0]
        else:
            raise Exception('Remote could not be found.')
    return remote

def remotes():
    output = subprocess.check_output(['git', 'remote'])
    return output.decode("utf-8").split('\n')
