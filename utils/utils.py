#!/usr/bin/python3
import logging
import subprocess
from datetime import datetime

import paramiko
import schedule
from paramiko import SSHClient,AutoAddPolicy

logger = logging.getLogger("backup_logger")


def run(cmd, cmd_log=None):
    """
    It runs a command and returns the return code, stdout, and stderr

    :param cmd: The command to be executed
    :param cmd_log: This is the command that will be logged
    :return: The return code, stdout, and stderr.
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
    """
    It returns the current date and time in the format YYYYMMDDHHMMSS
    :return: The current date and time in the format of YYYYMMDDHHMMSS
    """

    return datetime.now().strftime("%Y%m%d%H%M%S")


def get_curr_date_time_log_format():
    """
    It returns the current date and time in the format: `YYYY-MM-DD HH:MM:SS,FFF`

    The `FFF` part is the milliseconds
    :return: The current date and time in the format of YYYY-MM-DD HH:MM:SS,FFF
    """

    return datetime.now().strftime("%Y-%m-%d %H:%M:%S,%f")[:-3]


def run_remote(cmd, host, cmd_log=None):
    """
    It executes a command on a remote host and returns the output

    :param cmd: The command to be executed on the remote host
    :param host: The hostname or IP address of the remote server
    :param cmd_log: This is the command that will be logged
    :return: The return value is a tuple of three values:
    """

    try:
        if cmd_log is None:
            cmd_log = cmd
        client = SSHClient()
        client.set_missing_host_key_policy(AutoAddPolicy())
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
        out = ""
        err = ""
        try:
            out = str(stdout.read(), "utf-8")
        except:
            logger.debug("There is no stdout")
        client.close()
        return 0, out, err
    except Exception as e:
        logger.error("Error while executing command, with exception: " + str(e))


def parse_time(exec_time):
    """
    It takes a string of the form "* * * *" and returns a tuple of the form (seconds, minutes, hours, days)

    :param exec_time: The time at which the job should be executed
    :return: seconds, minutes, hours, days
    """

    seconds = 0
    minutes = 0
    hours = 0
    days = 0
    try:
        logger.debug("Parsing execution time: " + exec_time)
        times = exec_time.split(" ")
        if times[0] == '*':
            seconds = 0
        elif int(times[0]) < 0 or int(times[0]) > 59:
            seconds = 0
            logger.warning("Wrong number for seconds, system will use 0 !")
        else:
            seconds = int(times[0])
        if times[1] == '*':
            minutes = 0
        elif int(times[1]) < 0 or int(times[1]) > 59:
            minutes = 0
            logger.warning("Wrong number for minutes, system will use 0 !")
        else:
            minutes = int(times[1])
        if times[2] == '*':
            hours = 0
        elif int(times[2]) < 0 or int(times[2]) > 23:
            hours = 0
            logger.warning("Wrong number for hours, system will use 0 !")
        else:
            hours = int(times[2])
        if times[3] == '*':
            days = 0
        elif int(times[3]) < 0:
            days = 0
            logger.warning("Wrong number for days, system will use 0!")
        else:
            days = int(times[3])
        return seconds, minutes, hours, days
    except Exception as e:
        logger.error(str(e))
        return seconds, minutes, hours, days


def schedule_job(func_name, seconds, minutes, hours, days, args):
    """
    If the value of the parameter is 0, then the function will run every time the unit of time is incremented

    :param func_name: The function to be scheduled
    :param seconds: 0 - 59
    :param minutes: 0 - 59
    :param hours: 0-23
    :param days: The number of days to wait
    :param args: The arguments to pass to the function
    """

    logger.info("Scheduling job for function: " + str(func_name.__name__))
    logger.debug(
        "Integer: Days: " + str(days) + " Hours: " + str(hours) + " Minutes: " + str(minutes) + " Seconds: " + str(
            seconds))
    seconds = str(seconds)
    minutes = str(minutes)
    hours = str(hours)
    days = str(days)
    if len(seconds) == 1:
        seconds = '0' + seconds
    if len(minutes) == 1:
        minutes = '0' + minutes
    if len(hours) == 1:
        hours = '0' + hours

    logger.info("Days: " + days + " Hours: " + hours + " Minutes: " + minutes + " Seconds: " + seconds)

    if days == '0':
        if hours == '00':
            if minutes == '00':
                if seconds == '00':
                    schedule.every().second.do(func_name, args)
                else:
                    schedule.every(int(seconds)).seconds.do(func_name, args)
            else:
                if seconds == '00':
                    schedule.every(int(minutes)).minutes.do(func_name, args)
                else:
                    schedule.every(int(minutes)).minutes.at(':' + seconds).do(func_name, args)
        else:
            if minutes == '00':
                if seconds == '00':
                    schedule.every(int(hours)).hours.do(func_name, args)
                else:
                    schedule.every(int(hours)).hours.at(':' + seconds).do(func_name, args)
            else:
                if seconds == '00':
                    schedule.every(int(hours)).hours.at(minutes + ':00').do(func_name, args)
                else:
                    schedule.every(int(hours)).hours.at(minutes + ':' + seconds).do(func_name, args)
    else:
        if hours == '00':
            if minutes == '00':
                if seconds == '00':
                    schedule.every(int(days)).days.do(func_name, args)
                else:
                    schedule.every(int(days)).days.at('00:00:' + seconds).do(func_name, args)
            else:
                if seconds == '00':
                    schedule.every(int(days)).days.at('00:' + minutes + ':00').do(func_name, args)
                else:
                    schedule.every(int(days)).days.at('00:' + minutes + ':' + seconds).do(func_name, args)
        else:
            if minutes == '00':
                if seconds == '00':
                    schedule.every(int(days)).days.at(hours + ':00:00').do(func_name, args)
                else:
                    schedule.every(int(days)).days.at(hours + ':00:' + seconds).do(func_name, args)
            else:
                if seconds == '00':
                    schedule.every(int(days)).days.at(hours + ':' + minutes + ':00').do(func_name, args)
                else:
                    schedule.every(int(days)).days.at(hours + ':' + minutes + ':' + seconds).do(func_name, args)
