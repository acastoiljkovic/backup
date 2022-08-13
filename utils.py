#!/usr/bin/python3
import logging
import subprocess
from datetime import datetime

logger = logging.getLogger("backup_logger")

def Run(cmd):
    """Execute provided command

    Args:
        cmd (array): Array that contanins command and it's arguments

    Returns: (consists of 3 variables)
        int : return code after executing cmd
        string : standard output
        string : strandard error
    """
    try:
        logger.info('Executing: '+str(cmd))
        proc = subprocess.Popen(
            cmd,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        stdout, stderr = proc.communicate()
        return proc.returncode, str(stdout,"utf-8"), str(stderr,"utf-8")
    except Exception as e:
        logger.error("Error while executing comand, with exception: "+str(e))

def GetCurrDateTime():
    """Generate string of current time in format : YYYYmmDDHHMMSS    

    Returns:
        string : current time 
    """
    return datetime.now().strftime("%Y%m%d%H%M%S")
