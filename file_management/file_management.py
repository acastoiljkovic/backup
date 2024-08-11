import logging
from datetime import timedelta
from timeit import default_timer as timer
from utils import utils

logger = logging.getLogger("backup_logger")


def decrypt_data(file_name, password):
    """
    It decrypts the file using the provided password

    :param file_name: The name of the file to be encrypted
    :param password: The password used to encrypt the file
    :return: The name of the file without the .enc extension.
    """

    enc_cmd = ('openssl enc -aes-256-cbc -d -in ' + file_name + ' -out ' +
               file_name[:len(file_name) - 4] + ' -pass pass:' + password)
    logger.info("---------------------------------------")
    logger.info("start description")
    logger.info("---------------------------------------")
    start = timer()
    code, out, err = utils.run(enc_cmd)
    end = timer()
    if code > 0:
        logger.error("Error while decrypting file, status code: " + str(code) +
                     " , standard output: " + out + ", standard error: " + err)
        return
    else:
        logger.info("Time took for decrypting :" +
                    str(timedelta(seconds=end - start)))
        logger.debug("Standard output: " + out)
        utils.run('rm ' + file_name)
        return file_name[:len(file_name) - 4]


def encrypt_data(file_name, password):
    """
    It encrypts the file using the provided password

    :param file_name: The name of the file to be encrypted
    :param password: The password used to encrypt the file
    :return: The encrypted file name is being returned.
    """

    enc_cmd = ('openssl ' + 'enc ' + '-aes-256-cbc ' + '-in ' + file_name + ' ' +
               '-out ' + file_name + '.enc ' + '-pass pass:' + password)
    enc_cmd_log = ('openssl ' + 'enc ' + '-aes-256-cbc ' + '-in ' + file_name + ' ' +
                   '-out ' + file_name + '.enc ' + '-pass pass:***************')
    logger.info("---------------------------------------")
    logger.info("start encryption")
    logger.info("---------------------------------------")
    start = timer()
    code, out, err = utils.run(enc_cmd, enc_cmd_log)
    end = timer()
    if code > 0:
        logger.error("Error while encrypting file, status code: " + str(code) +
                     " , standard output: " + out + ", standard error: " + err)
        return
    else:
        logger.info("Time took for encrypting :" +
                    str(timedelta(seconds=end - start)))
        logger.debug("Standard output: " + out)
        utils.run('rm ' + file_name)
        return file_name + '.enc'


def encrypt_data_remote(host, file_name, password):
    """
    It encrypts the file on the remote host using the provided password

    :param host: The hostname or IP address of the remote machine
    :param file_name: The name of the file to be encrypted
    :param password: The password used to encrypt the file
    :return: The encrypted file name.
    """

    enc_cmd = ('openssl ' + 'enc ' + '-aes-256-cbc ' + '-in ' + file_name + ' ' +
               '-out ' + file_name + '.enc ' + '-pass pass:' + password)
    enc_cmd_log = ('openssl ' + 'enc ' + '-aes-256-cbc ' + '-in ' + file_name + ' ' +
                   '-out ' + file_name + '.enc ' + '-pass pass:****************')
    logger.info("---------------------------------------")
    logger.info("start encryption")
    logger.info("---------------------------------------")
    start = timer()
    code, out, err = utils.run_remote(enc_cmd, host, enc_cmd_log)
    end = timer()
    if code > 0:
        logger.error("Error while encrypting file, status code: " + str(code) +
                     " , standard output: " + out + ", standard error: " + err)
        return
    else:
        logger.info("Time took for encrypting :" +
                    str(timedelta(seconds=end - start)))
        logger.debug("Standard output: " + out)
        utils.run_remote('rm ' + file_name, host)
        return file_name + '.enc'


def copy(file, destination, file_name):
    """
    It copies a file from one location to another

    :param file: The file you want to copy
    :param destination: The destination folder where the file will be copied to
    :param file_name: The name of the file you want to copy
    :return: the time it took to copy the file.
    """

    cp_cmd = 'cp ' + file + ' ' + destination + '/' + file_name
    logger.info("---------------------------------------")
    logger.info("start coping files")
    logger.info("---------------------------------------")
    start = timer()
    code, out, err = utils.run(cp_cmd)
    end = timer()
    if code > 0:
        logger.error(err)
        return
    else:
        logger.info("File successfully copied to: " + destination)
        logger.info("Time took for coping: " +
                    str(timedelta(seconds=end - start)))
        logger.debug("Standard output: " + out)


def sync(src, dst):
    """
    It synchronizes the source and destination directories

    :param src: The source directory to be synchronized
    :param dst: The destination directory
    :return: the code, out, and err.
    """

    logger.info("---------------------------------------")
    logger.info("start synchronizing")
    logger.info("---------------------------------------")
    logger.info("Synchronizing directories: " +
                src + " Dst: " + dst)
    if src[-1] != '/':
        src = src + '/'
    rsync_cmd = 'rsync -a --delete ' + src + ' ' + dst
    start = timer()
    code, out, err = utils.run(rsync_cmd)
    if code > 0:
        logger.error("Error while synchronizing directories, \
                     standard Error: " + err + ", Standard output: " + out)
        return
    else:
        logger.debug("Directories " + src + ' and ' +
                     dst + " are successfully synchronized")
        end = timer()
        logger.info("Time took for synchronization: " +
                    str(timedelta(seconds=end - start)))


def sync_remote(host, source, destination):
    """
    It uses rsync to synchronize the contents of two directories

    :param host: The hostname of the remote machine
    :param source: The source directory to be synchronized
    :param destination: The destination directory on the remote machine
    :return: the code, out, and err.
    """

    logger.info("---------------------------------------")
    logger.info("start synchronizing on remote machines")
    logger.info("---------------------------------------")

    logger.info("Host: " + str(host))
    logger.info("Synchronizing directories: " +
                source + " Dst: " + destination)
    if source[-1] != '/':
        source = source + '/'
    rsync_cmd = 'rsync -a --delete ' + source + ' ' + destination
    start = timer()
    code, out, err = utils.run_remote(rsync_cmd, host)
    if code > 0:
        logger.error("Error while synchronizing directories, \
                     standard Error: " + err + ", Standard output: " + out)
        return
    else:
        logger.debug("Directories " + source + ' and ' +
                     destination + " are successfully synchronized")
        end = timer()
        logger.info("Time took for synchronization: " +
                    str(timedelta(seconds=end - start)))


def rmold(directory, name, no_copies, encrypt):
    """
    It deletes all but the most recent N files in a directory

    :param directory: The directory where the files are located
    :param name: The name of the file to be backed up
    :param no_copies: The number of copies to keep
    :param encrypt: True/False
    """

    logger.info("---------------------------------------")
    logger.info("start delete")
    logger.info("---------------------------------------")
    logger.info("Deleting files from directory: " + str(directory))
    logger.debug("Number of files to save: " + str(no_copies))
    if encrypt.upper() == "FALSE":
        list_cmd = 'ls -t ' + directory + ' | grep \'' + name + '\' | grep -v \'.enc$\''
    else:
        list_cmd = 'ls -t ' + directory + ' | grep -E \'' + name + '.*.enc*\''
    code, out, err = utils.run(list_cmd)
    if code == 0:
        line = out.split('\n')
        logger.debug("Number of files: " + str(len(line) - 1))
        logger.debug("Number of files for deletion: " +
                     str(len(line) - int(no_copies) - 1))
        for i in range(int(no_copies), len(line) - 1):
            f = directory + '/' + line[i].split(' ')[0]
            rm_cmd = 'rm ' + f
            code, out, err = utils.run(rm_cmd)
            if code > 0:
                logger.error("Error while removing file: " + f +
                             ", Standard Error: " + err + ", Standard output: " + out)
            else:
                logger.debug("File " + f + " successfully deleted")

        logger.info("Finished deleting files from directory: " + directory)
    else:
        logger.error("Error while listing files with error: " + err +
                     " out: " + out + " code: " + str(code))


def rmold_remote(host, directory, name, no_copies, encrypt):
    """
    It deletes old files from a remote host

    :param host: The hostname or IP address of the remote host
    :param directory: The directory where the files are located
    :param name: The name of the file to be backed up
    :param no_copies: The number of copies to keep
    :param encrypt: This is a boolean value that tells the script
                    whether to encrypt the backup
    """

    logger.info("---------------------------------------")
    logger.info("start delete remotely")
    logger.info("---------------------------------------")
    logger.info("Deleting files on host: " + host)
    logger.info("Deleting files from directory: " + str(directory))
    logger.debug("Number of files to save: " + str(no_copies))
    if encrypt.upper() == "FALSE":
        list_cmd = 'ls -t ' + directory + ' | grep \'' + name + '\' | grep -v \'.enc$\''
    else:
        list_cmd = 'ls -t ' + directory + ' | grep -E \'' + name + '.*.enc*\''
    code, out, err = utils.run_remote(list_cmd, host)
    if code == 0:
        line = out.split('\n')
        logger.debug("Number of files: " + str(len(line) - 1))
        logger.debug("Number of files for deletion: " +
                     str(len(line) - int(no_copies) - 1))
        for i in range(int(no_copies), len(line) - 1):
            f = directory + '/' + line[i].split(' ')[0]
            rm_cmd = 'rm ' + f
            code, out, err = utils.run_remote(rm_cmd, host)
            if code > 0:
                logger.error("Error while removing file: " + f +
                             ", Standard Error: " + err + ", Standard output: " + out)
            else:
                logger.debug("File " + f + " successfully deleted")

        logger.info("Finished deleting files from directory: " + directory)
    else:
        logger.error("Error while listing files with error: " + err +
                     " out: " + out + " code: " + str(code))


def keep_only_oldest_and_newest(directory, name, encrypt):
    """
    It deletes all but the newest and oldest files in a directory

    :param directory: The directory where the files are located
    :param name: The name of the file to be deleted
    :param encrypt: This is a boolean value that tells the script
                    whether to encrypt the file
    """

    logger.info("---------------------------------------")
    logger.info("start delete")
    logger.info("---------------------------------------")
    logger.info("Deleting files from directory: " + directory)
    if encrypt.upper() == "FALSE":
        list_cmd = 'ls -t ' + directory + ' | grep \'' + name + \
                   '\' | grep -v \'.enc$\' | grep -v \'.snap$\' | grep -v \'.snap.bak$\''
    else:
        list_cmd = 'ls -t ' + directory + ' | grep -E \'' + name + '.*.enc*\''
    code, out, err = utils.run(list_cmd)
    if code == 0:
        line = out.split('\n')
        logger.debug("Number of files: " + str(len(line) - 1))
        for i in range(1, len(line) - 2):
            f = directory + '/' + line[i].split(' ')[0]
            rm_cmd = 'rm ' + f
            code, out, err = utils.run(rm_cmd)
            if code > 0:
                logger.error("Error while removing file: " + f +
                             ", Standard Error: " + err + ", Standard output: " + out)
            else:
                logger.debug("File " + f + " successfully deleted")
    else:
        logger.error("Error while listing files: " + err)


def path_exists(path, host=None):
    path_check_command = (
            '[ -d "' + path + '" ] && echo "true" || echo "false"'
    )
    logger.debug("Check path command: "+path_check_command)
    if host is not None:
        logger.debug("Checking path: " + path + " on host: " + host)
        path_cmd_code, path_cmd_out, path_cmd_err = utils.run_remote(path_check_command, host)
        logger.debug("path_cmd_code: " + str(path_cmd_code) + " path_cmd_out: " + str(path_cmd_out) +
                     " path_cmd_err: " + str(path_cmd_err))
    else:
        logger.debug("Checking path: " + path + " locally")
        path_cmd_code, path_cmd_out, path_cmd_err = utils.run(path_check_command)
        logger.debug("path_cmd_code: " + str(path_cmd_code) + " path_cmd_out: " + str(path_cmd_out) +
                     " path_cmd_err: " + str(path_cmd_err))
    if path_cmd_out:
        return path_cmd_out.strip().lower() == 'true'
    return False
