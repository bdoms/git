import os
import subprocess


def installed():
    """ detects if the system has git or not """
    try:
        subprocess.call(["git", "rev-parse"])
        return True
    except OSError:
        return False

def isRepository():
    return subprocess.check_output(["git", "rev-parse", "--is-inside-work-tree"]).replace("\n", "") == "true"

def currentBranch():
    """ gets the name of the current branch """
    return subprocess.check_output(["git", "rev-parse", "--abbrev-ref", "HEAD"]).replace("\n", "")

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
    commits = output.split('\n') # each line is surrounded by quotes (e.g. '"1234 abcd"')
    return [commit[1:-1] for commit in commits]

def commitBody(long_sha):
    body = subprocess.check_output(['git', 'log', '--pretty=format:"%B"', '-n', '1', long_sha])
    return body[1:-1].strip() # body is surrounded by quotes (e.g. '"commit message"')

def remotesWithCommit(long_sha):
    return subprocess.check_output(['git', 'branch', '-r', '--contains', long_sha])

def pushForced():
    pid = os.getppid()
    push_command = subprocess.check_output(['ps', '-ocommand=', '-p', str(pid)])
    return ('--force' in push_command or '-f' in push_command)
