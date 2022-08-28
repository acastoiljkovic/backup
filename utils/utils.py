#!/usr/bin/python3
import logging
import subprocess
from datetime import datetime
from sys import stdout
from typing import List

logger = logging.getLogger("backup_logger")


def Run(cmd):
    """Execute provided command

    Args:
        cmd (array): Array that contains command and it's arguments

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
        # stdout = proc.stdout.readlines()
        # stderr = proc.stderr.readlines()
        stdout, stderr = proc.communicate()
        return proc.returncode, str(stdout, "utf-8"), str(stderr, "utf-8")
    except Exception as e:
        logger.error("Error while executing comand, with exception: " + str(e))


def GetCurrDateTime():
    """Generate string of current time in format : YYYYmmDDHHMMSS    

    Returns:
        string : current time 
    """
    return datetime.now().strftime("%Y%m%d%H%M%S")


def RunRemote(cmd, host):
    try:
        logger.info("Executing command: " + str(cmd) + " on remote host: " + host)
        command = ""
        if len(cmd) >= 1:
            for c in cmd:
                command += str(c)
        logger.debug("Command as string: " + command)

        proc = subprocess.Popen(
            ["ssh", "%s" % host, command],
            shell=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE)

        # stdout = proc.stdout.readlines()
        # stderr = proc.stderr.readlines()

        stdout, stderr = proc.communicate()
        if stdout == []:
            logger.error(proc.stderr.readlines())
        else:
            return proc.returncode, str(stdout, "utf-8"), str(stderr, "utf-8")
    except Exception as e:
        logger.error("Error while executing command, with exception: " + str(e))
