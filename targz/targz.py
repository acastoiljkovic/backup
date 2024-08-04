#!/usr/bin/python3
import time
from os.path import exists
from utils import utils
import logging
from file_management import file_management
from datetime import timedelta
from timeit import default_timer as timer

logger = logging.getLogger("backup_logger")


def targz(paths, destinations, encrypt, enc_pass, no_copies=3, one_drive=None, one_drive_dir=None):
    """
    It compresses the provided directories and encrypts the compressed file if the encrypt parameter is set to True

    # 
    :param paths: a list of directories to compress
    :param destinations: a list of directories to copy the backup to
    :param encrypt: True/False
    :param enc_pass: The password to encrypt the file with
    :param no_copies: The number of copies to keep, defaults to 3 (optional)
    :param one_drive: the OneDrive object
    :param one_drive_dir: The directory on OneDrive where you want to store the backup
    :return: Nothing is being returned.
    """

    for dir2compress in paths:
        logger.info("---------------------------------------")
        logger.info("start targz full")
        logger.info("---------------------------------------")
        logger.info("Targz provided directories :" +
                    dir2compress)
        file_prefix = dir2compress.replace(
            '/',
            '-',
        )
        if file_management.path_exists(dir2compress):
            if file_prefix[0] == '-':
                file_prefix = file_prefix[1:len(file_prefix)]
            if file_prefix[len(file_prefix)-1] == '-':
                file_prefix = file_prefix[:len(file_prefix)-1]
            file_prefix = file_prefix + "-full"
            file_name = file_prefix + '-' + utils.get_curr_date_time() + '.tar.gz'
            fn = file_name
            file_name = destinations[0] + '/' + file_name

            if exists(file_name):
                logger.warning("File already exist, waiting 2 seconds!")
                time.sleep(2)
                file_name = file_prefix + '-' + utils.get_curr_date_time() + '.tar.gz'
                fn = file_name
                file_name = destinations[0] + '/' + file_name

            targz_cmd = (
                    'tar -czvf ' + file_name + ' --absolute-names ' + dir2compress
            )
            start = timer()
            code, out, err = utils.run(targz_cmd)
            if code > 0:
                logger.error(err)
                logger.debug("Status code: " + str(code) + "\tStandard Output: "
                             + out + "\tStandard Error: " + err)
                return

            logger.info("Directory is compressed. File :" +
                        file_name + " successfully created.")
            end = timer()
            logger.info("Time took for targz :" +
                        str(timedelta(seconds=end - start)))

            if str(encrypt).upper() == 'TRUE':
                file_name = file_management.encrypt_data(
                    file_name, enc_pass)
                fn = fn + '.enc'

            if one_drive is not None:
                one_drive.upload_file(one_drive_dir=one_drive_dir,
                                      local_dir=destinations[0], file_name=fn)
                one_drive.remove_old_files(
                    file_name=file_prefix, one_drive_dir=one_drive_dir, encrypt=encrypt, no_copies=no_copies)
            if len(destinations) > 1:
                for i in range(0, len(destinations)):
                    if i != 0:
                        file_management.copy(file_name, destinations[i], fn)
                    file_management.rmold(
                        directory=destinations[i], name=file_prefix, encrypt=encrypt, no_copies=no_copies)
        else:
            logger.error("Path: " + dir2compress + " , doesn't exists!")


def targz_incremental(paths, destinations, encrypt, enc_pass, one_drive=None, one_drive_dir=None):
    """
    It takes a list of directories, compresses them in incremental way, encrypts them, and uploads them to OneDrive
    
    :param paths: A list of directories to compress
    :param destinations: a list of directories to copy the backup to
    :param encrypt: True/False
    :param enc_pass: The password to encrypt the file with
    :param one_drive: the OneDrive object
    :param one_drive_dir: The directory on OneDrive where you want to store the backup
    :return: Nothing is being returned.
    """

    for dir2compress in paths:
        logger.info("---------------------------------------")
        logger.info("start targz incremental")
        logger.info("---------------------------------------")
        logger.info("Targz provided directories :" +
                    dir2compress)
        file_prefix = dir2compress.replace(
            '/',
            '-',
        )
        if file_management.path_exists(dir2compress):
            if file_prefix[0] == '-':
                file_prefix = file_prefix[1:len(file_prefix)]
            if file_prefix[len(file_prefix)-1] == '-':
                file_prefix = file_prefix[:len(file_prefix)-1]
            file_prefix = file_prefix + "-inc"
            file_name = file_prefix + '-' + utils.get_curr_date_time() + '.tar.gz'
            fn = file_name
            file_name = destinations[0] + '/' + file_name
            snap_file = destinations[0] + '/' + file_prefix + '.snap'

            if exists(file_name):
                logger.warning("File already exist, waiting 2 seconds!")
                time.sleep(2)
                file_name = file_prefix + '-' + utils.get_curr_date_time() + '.tar.gz'
                fn = file_name
                file_name = destinations[0] + '/' + file_name

            targz_cmd = (
                    'tar -czPg ' + snap_file + ' -f ' + file_name +
                    ' --absolute-names ' + dir2compress
            )
            start = timer()
            code, out, err = utils.run(targz_cmd)
            if code > 0:
                logger.error(err)
                logger.debug("Status code: " + str(code) + "\tStandard Output: "
                             + out + "\tStandard Error: " + err)
                return
            logger.info("Directory is compressed. File :" +
                        file_name + " successfully created.")
            end = timer()
            logger.info("Time took for targz :" +
                        str(timedelta(seconds=end - start)))

            if str(encrypt).upper() == 'TRUE':
                file_name = file_management.encrypt_data(
                    file_name, enc_pass)
                fn = fn + '.enc'

            if one_drive is not None:
                one_drive.upload_file(one_drive_dir=one_drive_dir,
                                      local_dir=destinations[0], file_name=fn)
                one_drive.upload_file(one_drive_dir=one_drive_dir,
                                      local_dir=destinations[0], file_name=file_prefix + '.snap')
            if len(destinations) > 1:
                for i in range(1, len(destinations)):
                    file_management.copy(file_name, destinations[i], fn)
                    file_management.copy(
                        snap_file, destinations[i], file_prefix + '.snap')
        else:
            logger.error("Path: " + dir2compress + " , doesn't exists!")


def targz_differential(paths, destinations, encrypt, enc_pass, one_drive=None, one_drive_dir=None):
    """
    It creates a tar.gz file of the provided directory, and then compares it to the previous tar.gz file,
    and only keeps the new files

    :param paths: a list of paths to compress
    :param destinations: a list of directories where the backup will be stored
    :param encrypt: True/False
    :param enc_pass: The password to use for encryption
    :param one_drive: the OneDrive object
    :param one_drive_dir: The directory on OneDrive where you want to store the backup
    :return: Nothing is being returned.
    """

    for dir2compress in paths:
        logger.info("---------------------------------------")
        logger.info("start targz differential")
        logger.info("---------------------------------------")
        logger.info("Targz provided directories :" +
                    dir2compress)
        file_prefix = dir2compress.replace(
            '/',
            '-',
        )
        if file_management.path_exists(dir2compress):
            if file_prefix[0] == '-':
                file_prefix = file_prefix[1:len(file_prefix)]
            if file_prefix[len(file_prefix)-1] == '-':
                file_prefix = file_prefix[:len(file_prefix)-1]
            file_prefix = file_prefix + "-diff"
            file_name = file_prefix + '-' + utils.get_curr_date_time() + '.tar.gz'
            fn = file_name
            file_name = destinations[0] + '/' + file_name
            snap_file = destinations[0] + '/' + file_prefix + '.snap'
            snap_file_bak = destinations[0] + '/' + file_prefix + '.snap.bak'

            if exists(file_name):
                logger.warning("File already exist, waiting 2 seconds!  ")
                time.sleep(2)
                file_name = file_prefix + '-' + utils.get_curr_date_time() + '.tar.gz'
                fn = file_name
                file_name = destinations[0] + '/' + file_name

            targz_cmd = (
                    'tar -czPg ' + snap_file + ' -f ' + file_name +
                    ' --absolute-names ' + dir2compress
            )
            start = timer()
            code, out, err = utils.run(targz_cmd)
            if code > 0:
                logger.error(err)
                logger.debug("Status code: " + str(code) + "\tStandard Output: "
                             + out + "\tStandard Error: " + err)
                return
            logger.info("Directory is compressed. File :" +
                        file_name + " successfully created.")

            if not exists(snap_file_bak):
                utils.run("cp " + snap_file + " " + snap_file_bak)
            else:
                utils.run("cp " + snap_file_bak + " " + snap_file)

            end = timer()
            logger.info("Time took for targz :" +
                        str(timedelta(seconds=end - start)))

            if str(encrypt).upper() == 'TRUE':
                file_name = file_management.encrypt_data(
                    file_name, enc_pass)
                fn = fn + '.enc'

            if one_drive is not None:
                one_drive.upload_file(one_drive_dir=one_drive_dir,
                                      local_dir=destinations[0], file_name=fn)
                one_drive.upload_file(one_drive_dir=one_drive_dir,
                                      local_dir=destinations[0], file_name=file_prefix + '.snap')
                one_drive.upload_file(one_drive_dir=one_drive_dir,
                                      local_dir=destinations[0], file_name=file_prefix + '.snap.bak')
                one_drive.keep_only_oldest_and_newest(
                    file_name=file_prefix, one_drive_dir=one_drive_dir, encrypt=encrypt)

            if len(destinations) >= 1:
                for i in range(0, len(destinations)):
                    if i != 0:
                        file_management.copy(file_name, destinations[i], fn)
                        file_management.copy(
                            snap_file, destinations[i], file_prefix + '.snap')
                        file_management.copy(
                            snap_file_bak, destinations[i], file_prefix + '.snap.bak')
                    file_management.keep_only_oldest_and_newest(
                        directory=destinations[i], name=file_prefix, encrypt=encrypt)
        else:
            logger.error("Path: " + dir2compress + " , doesn't exists!")


def targz_remote(host, paths, destinations, encrypt, enc_pass, no_copies=3, one_drive=None, one_drive_dir=None):
    """
    It takes a list of directories, compresses them, encrypts them, uploads them to OneDrive, and then deletes the old
    copies and all of that is done one the remote host

    :param host: The hostname or IP address of the remote server
    :param paths: A list of paths to be compressed
    :param destinations: a list of directories where the backup will be stored
    :param encrypt: True/False
    :param enc_pass: The password to encrypt the file with
    :param no_copies: The number of copies to keep, defaults to 3 (optional)
    :param one_drive: the OneDrive object
    :param one_drive_dir: The directory in OneDrive where you want to store the backup
    :return: Nothing is being returned.
    """

    for path in paths:
        logger.info("---------------------------------------")
        logger.info("start targz full remote")
        logger.info("---------------------------------------")
        logger.info("Targz provided directory :" +
                    path)
        file_prefix = path.replace(
            '/',
            '-',
        )
        if file_management.path_exists(path, host):
            if file_prefix[0] == '-':
                file_prefix = file_prefix[1:len(file_prefix)]
            if file_prefix[len(file_prefix)-1] == '-':
                file_prefix = file_prefix[:len(file_prefix)-1]
            file_prefix = file_prefix + "-full-" + host
            file_name = file_prefix + '-' + utils.get_curr_date_time() + '.tar.gz'
            fn = file_name
            file_name = destinations[0] + '/' + file_name

            if exists(file_name):
                logger.warning("File already exist, waiting 2 seconds!")
                time.sleep(2)
                file_name = file_prefix + '-' + utils.get_curr_date_time() + '.tar.gz'
                fn = file_name
                file_name = destinations[0] + '/' + file_name

            targz_cmd = (
                    'tar -czvf ' + file_name + ' --absolute-names ' + path
            )
            start = timer()
            code, out, err = utils.run_remote(targz_cmd, host)
            if code > 0:
                logger.error(err)
                logger.debug("Status code: " + str(code) + "\tStandard Output: "
                             + out + "\tStandard Error: " + err)
                return

            logger.info("Directory is compressed. File :" +
                        file_name + " successfully created.")
            end = timer()
            logger.info("Time took for targz :" +
                        str(timedelta(seconds=end - start)))

            if str(encrypt).upper() == 'TRUE':
                file_name = file_management.encrypt_data(
                    file_name, enc_pass)
                fn = fn + '.enc'

            if one_drive is not None:
                one_drive.upload_file(
                    one_drive_dir=one_drive_dir,
                    local_dir=destinations[0],
                    file_name=fn)

                one_drive.remove_old_files(
                    file_name=file_prefix,
                    one_drive_dir=one_drive_dir,
                    encrypt=encrypt,
                    no_copies=no_copies)

                file_management.rmold(
                    directory=destinations[0],
                    name=file_prefix,
                    encrypt=encrypt,
                    no_copies=no_copies)

            if len(destinations) >= 1:
                for i in range(0, len(destinations)):
                    if i != 0:
                        file_management.copy(file_name, destinations[i], fn)
                    file_management.rmold(
                        directory=destinations[i], name=file_prefix, encrypt=encrypt, no_copies=no_copies)
        else:
            logger.error("Path: " + path + " , doesn't exists!")


def targz_incremental_remote(host, paths, destinations, encrypt, enc_pass, one_drive=None, one_drive_dir=None):
    """
    It takes a list of paths, and creates a tar.gz file of each path, and then uploads the tar.gz file to OneDrive

    :param host: The hostname or IP address of the remote server
    :param paths: A list of paths to be compressed
    :param destinations: This is a list of directories where you want to store the backup
    :param encrypt: True/False
    :param enc_pass: The password to encrypt the file with
    :param one_drive: the OneDrive object
    :param one_drive_dir: The directory in OneDrive where you want to store the backup files
    :return: The return value is a tuple (status, output)
    """

    for path in paths:
        logger.info("---------------------------------------")
        logger.info("start targz incremental remote")
        logger.info("---------------------------------------")
        logger.info("Targz provided directory :" +
                    path)
        file_prefix = path.replace(
            '/',
            '-',
        )
        if file_management.path_exists(path, host):
            if file_prefix[0] == '-':
                file_prefix = file_prefix[1:len(file_prefix)]
            if file_prefix[len(file_prefix)-1] == '-':
                file_prefix = file_prefix[:len(file_prefix)-1]
            file_prefix = file_prefix + "-inc-" + host
            file_name = file_prefix + '-' + utils.get_curr_date_time() + '.tar.gz'
            fn = file_name
            file_name = destinations[0] + '/' + file_name
            snap_file = destinations[0] + '/' + file_prefix + '.snap'

            if exists(file_name):
                logger.warning("File already exist, waiting 2 seconds!")
                time.sleep(2)
                file_name = file_prefix + '-' + utils.get_curr_date_time() + '.tar.gz'
                fn = file_name
                file_name = destinations[0] + '/' + file_name

            targz_cmd = (
                    'tar -czPg ' + snap_file + ' -f ' + file_name +
                    ' --absolute-names ' + path + " && echo 'done'"
            )
            start = timer()
            code, out, err = utils.run_remote(targz_cmd, host)
            if code > 0:
                logger.error(err)
                logger.debug("Status code: " + str(code) + "\tStandard Output: "
                             + out + "\tStandard Error: " + err)
                return
            logger.info("Directory is compressed. File :" +
                        file_name + " successfully created.")
            end = timer()
            logger.info("Time took for targz :" +
                        str(timedelta(seconds=end - start)))

            if str(encrypt).upper() == 'TRUE':
                file_name = file_management.encrypt_data(
                    file_name, enc_pass)
                fn = fn + '.enc'

            if one_drive is not None:
                one_drive.upload_file(one_drive_dir=one_drive_dir,
                                      local_dir=destinations[0], file_name=fn)
                one_drive.upload_file(one_drive_dir=one_drive_dir,
                                      local_dir=destinations[0], file_name=file_prefix + '.snap')
            if len(destinations) >= 1:
                for i in range(1, len(destinations)):
                    file_management.copy(file_name, destinations[i], fn)
                    file_management.copy(
                        snap_file, destinations[i], file_prefix + '.snap')
        else:
            logger.error("Path: " + path + " , doesn't exists!")


def targz_differential_remote(host, paths, destinations, encrypt, enc_pass, one_drive=None, one_drive_dir=None):
    """
    It takes a directory, creates a snapshot of it, compresses the directory, encrypts it, and uploads it to OneDrive

    :param host: The hostname or IP address of the remote server
    :param paths: a list of paths to be compressed
    :param destinations: a list of directories where the backup will be stored
    :param encrypt: True/False
    :param enc_pass: The password to use for encryption
    :param one_drive: the OneDrive object
    :param one_drive_dir: The directory on OneDrive where you want to store the backup files
    :return: The return value is a tuple (status, output)
    """

    for path in paths:
        logger.info("---------------------------------------")
        logger.info("start targz differential remote")
        logger.info("---------------------------------------")
        logger.info("Targz provided directory :" +
                    path)
        file_prefix = path.replace(
            '/',
            '-',
        )
        if file_management.path_exists(path, host):
            if file_prefix[0] == '-':
                file_prefix = file_prefix[1:len(file_prefix)]
            if file_prefix[len(file_prefix)-1] == '-':
                file_prefix = file_prefix[:len(file_prefix)-1]
            file_prefix = file_prefix + "-diff-" + host
            file_name = file_prefix + '-' + utils.get_curr_date_time() + '.tar.gz'
            fn = file_name
            snap_file = destinations[0] + '/' + file_prefix + '.snap'
            file_name = destinations[0] + '/' + file_name
            snap_file_bak = destinations[0] + '/' + file_prefix + '.snap.bak'

            if exists(file_name):
                logger.warning("File already exist, waiting 2 seconds!")
                time.sleep(2)
                file_name = file_prefix + '-' + utils.get_curr_date_time() + '.tar.gz'
                fn = file_name
                file_name = destinations[0] + '/' + file_name

            targz_cmd = (
                    'tar -czPg ' + snap_file + ' -f ' + file_name +
                    ' --absolute-names ' + path + " && echo 'done'"
            )
            start = timer()
            code, out, err = utils.run_remote(targz_cmd, host)
            if code > 0:
                logger.error(err)
                logger.debug("Status code: " + str(code) + "\tStandard Output: "
                             + out + "\tStandard Error: " + err)
                return
            logger.info("Directory is compressed. File :" +
                        file_name + " successfully created.")

            if not exists(snap_file_bak):
                utils.run("cp " + snap_file + " " + snap_file_bak)
            else:
                utils.run("cp " + snap_file_bak + " " + snap_file)

            end = timer()
            logger.info("Time took for targz :" +
                        str(timedelta(seconds=end - start)))

            if str(encrypt).upper() == 'TRUE':
                file_name = file_management.encrypt_data(
                    file_name, enc_pass)
                fn = fn + '.enc'

            if one_drive is not None:
                one_drive.upload_file(one_drive_dir=one_drive_dir,
                                      local_dir=destinations[0], file_name=fn)
                one_drive.upload_file(one_drive_dir=one_drive_dir,
                                      local_dir=destinations[0], file_name=file_prefix + '.snap')
                one_drive.upload_file(one_drive_dir=one_drive_dir,
                                      local_dir=destinations[0], file_name=file_prefix + '.snap.bak')
                one_drive.keep_only_oldest_and_newest(
                    file_name=file_prefix, one_drive_dir=one_drive_dir, encrypt=encrypt)

            if len(destinations) >= 1:
                for i in range(0, len(destinations)):
                    if i != 0:
                        file_management.copy(file_name, destinations[i], fn)
                        file_management.copy(
                            snap_file, destinations[i], file_prefix + '.snap')
                        file_management.copy(
                            snap_file_bak, destinations[i], file_prefix + '.snap.bak')
                    file_management.keep_only_oldest_and_newest(
                        directory=destinations[i], name=file_prefix, encrypt=encrypt)
        else:
            logger.error("Path: " + path + " , doesn't exists!")