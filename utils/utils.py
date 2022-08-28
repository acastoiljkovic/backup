#!/usr/bin/python3
import logging
import subprocess
from datetime import datetime
from paramiko import SSHClient

logger = logging.getLogger("backup_logger")


def run(cmd):
    """Execute provided command

    Args:
        cmd (string): Array that contains command and it's arguments

    Returns: (consists of 3 variables)
        int : return code after executing cmd
        string : standard output
        string : standard error
    """
    try:
        logger.info('Executing: ' + str(cmd))
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


def run_remote(cmd, host):
    try:
        client = SSHClient()
        client.load_system_host_keys()
        # if logger.level == logging.DEBUG:
            # client.set_log_channel(name='backup_logger')
        logger.info("Executing command: " + str(cmd) + " on remote host: " + host)
        command = ""
        if len(cmd) >= 1:
            for c in cmd:
                command += str(c)
        logger.debug("Command as string: " + command)

        # proc = subprocess.Popen(
        #     "ssh root@"+host + " "+command,
        #     shell=True,
        #     stdout=subprocess.PIPE,
        #     stderr=subprocess.PIPE)

        client.connect(hostname=host, username='root')
        stdin, stdout, stderr = client.exec_command(
            command=command,
            timeout=10,
            bufsize=-1)
        # client.close()
        # stdout, stderr = proc.communicate()

        if not stdout:
            logger.error(stderr)
        else:
            return 0, str(stdout.read(), "utf-8"), str(stderr.read(), "utf-8")
    except Exception as e:
        logger.error("Error while executing command, with exception: " + str(e))
