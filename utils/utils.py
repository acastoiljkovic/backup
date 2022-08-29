#!/usr/bin/python3
import logging
import subprocess
from datetime import datetime
from paramiko import SSHClient

logger = logging.getLogger("backup_logger")


def run(cmd, cmd_log=None):
    """Execute provided command

    Args:
        cmd_log (string): String that contains command for logging.
        cmd (string): String that contains command and it's arguments

    Returns: (consists of 3 variables)
        int : return code after executing cmd
        string : standard output
        string : standard error
    """
    if cmd_log is None:
        cmd_log = cmd
    try:
        logger.info('Executing: ' + str(cmd_log))
        proc = subprocess.Popen(
            cmd,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

        stdout, stderr = proc.communicate()
        return proc.returncode, str(stdout, "utf-8"), str(stderr, "utf-8")
    except Exception as e:
        logger.error("Error while executing command, with exception: " + str(e))


def get_curr_date_time():
    """Generate string of current time in format : YYYYmmDDHHMMSS    

    Returns:
        string : current time 
    """
    return datetime.now().strftime("%Y%m%d%H%M%S")


def run_remote(cmd, host, cmd_log=None):
    try:
        if cmd_log is None:
            cmd_log = cmd
        client = SSHClient()
        client.load_system_host_keys()
        logger.info("Executing command: " + str(cmd_log) + " on remote host: " + host)
        command = ""
        if len(cmd) >= 1:
            for c in cmd:
                command += str(c)
        command_log = ""
        if len(cmd_log) >= 1:
            for c in cmd_log:
                command_log += str(c)
        logger.debug("Command as string: " + command_log)

        client.connect(hostname=host, username='root')
        stdin, stdout, stderr = client.exec_command(
            command=command,
            timeout=10,
            bufsize=-1)
        client.close()

        if not stdout:
            logger.error(stderr)
        else:
            return 0, str(stdout.read(), "utf-8"), str(stderr.read(), "utf-8")
    except Exception as e:
        logger.error("Error while executing command, with exception: " + str(e))
