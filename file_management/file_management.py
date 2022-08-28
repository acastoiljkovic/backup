import logging
from datetime import timedelta
from timeit import default_timer as timer
from utils import utils

logger = logging.getLogger("backup_logger")


def decrypt_data(file_name, password):
    """Method to decrypt encrypted file using aes-256 algorithm.
    As a result, provided file will be removed, and new file 
    will be without extension .enc.

    Args:
        file_name (string): Full path to the file with .enc extension
        password (string): Salt that is used to encrypt file

    Returns:
        string: Path to the decrypted file
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
    """Method to encrypt provided file using aes-256 algorithm.
    As a result, provided file will be removed, and new file
    will have extension .enc.

    Args:
        file_name (string): Full path to the file
        password (string): Salt for encryption

    Returns:
        string: Path to the encrypted file
    """
    enc_cmd = ('openssl ' + 'enc ' + '-aes-256-cbc ' + '-in ' + file_name + ' ' +
               '-out ' + file_name + '.enc ' + '-pass pass:' + password)
    logger.info("---------------------------------------")
    logger.info("start encryption")
    logger.info("---------------------------------------")
    start = timer()
    code, out, err = utils.run(enc_cmd)
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
    """Method to encrypt provided file using aes-256 algorithm.
    As a result, provided file will be removed, and new file
    will have extension .enc.

    Args:
        file_name (string): Full path to the file
        password (string): Salt for encryption

    Returns:
        string: Path to the encrypted file
    """
    enc_cmd = ('openssl ' + 'enc ' + '-aes-256-cbc ' + '-in ' + file_name + ' ' +
               '-out ' + file_name + '.enc ' + '-pass pass:' + password)
    logger.info("---------------------------------------")
    logger.info("start encryption")
    logger.info("---------------------------------------")
    start = timer()
    code, out, err = utils.run_remote(enc_cmd,host)
    end = timer()
    if code > 0:
        logger.error("Error while encrypting file, status code: " + str(code) +
                     " , standard output: " + out + ", standard error: " + err)
        return
    else:
        logger.info("Time took for encrypting :" +
                    str(timedelta(seconds=end - start)))
        logger.debug("Standard output: " + out)
        utils.run_remote('rm ' + file_name,host)
        return file_name + '.enc'


def copy(file, destination, file_name):
    """Copy file to the new destination with new file_name

    Args:
        file (string): file name
        destination (string): path where to copy file
        file_name (string): new file name
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
    """Using rsync to synchronize content of provided directories.
        Destination directory will contain the same data as source
        directory after execution.

    Args:
        src (string): Source directory
        dst (string): Destination directory
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


def sync_remote(hosts, sources, destinations):
    """
    It takes a list of hosts, a list of sources and a list of destinations and synchronizes the sources with the
    destinations on the hosts

    :param hosts: a list of hosts to run the command on
    :param sources: The source directory to be synchronized
    :param destinations: The destination directory on the remote machine
    :return: the code, out, and err.
    """
    logger.info("---------------------------------------")
    logger.info("start synchronizing on remote machines")
    logger.info("---------------------------------------")

    i = 0
    j = 0
    for host in hosts:
        logging.info("Host: " + str(host))
        logger.info("Synchronizing directories: " +
                    sources[i] + " Dst: " + destinations[j])
        if sources[-1] != '/':
            sources = sources + '/'
        rsync_cmd = 'rsync -a --delete ' + sources + ' ' + destinations
        start = timer()
        code, out, err = utils.run_remote(rsync_cmd, host)
        if code > 0:
            logger.error("Error while synchronizing directories, \
                         standard Error: " + err + ", Standard output: " + out)
            return
        else:
            logger.debug("Directories " + sources + ' and ' +
                         destinations + " are successfully synchronized")
            end = timer()
            logger.info("Time took for synchronization: " +
                        str(timedelta(seconds=end - start)))

        if len(hosts) == len(sources):
            i += 1
        if len(hosts) == len(destinations):
            j += 1


def rmold(dir, name, noCopies, encrypt):
    """From provided directory, remove files that contain 'name'
        in file name if there is more than 'no_copies' files.

    Args:
        encrypt:
        dir (string): Directory that contains backups
        name (string): Part of the file name
        noCopies (integer): Number of files that will persist in dir
    """
    logger.info("---------------------------------------")
    logger.info("start delete")
    logger.info("---------------------------------------")
    logger.info("Deleting files from directory: " + str(dir))
    logger.debug("Number of files to save: " + str(noCopies))
    if encrypt.upper() == "FALSE":
        list_cmd = 'ls -t ' + dir + ' | grep \'' + name + '\' | grep -v \'.enc$\''
    else:
        list_cmd = 'ls -t ' + dir + ' | grep -E \'' + name + '.*.enc*\''
    code, out, err = utils.run(list_cmd)
    if code == 0:
        line = out.split('\n')
        logger.debug("Number of files: " + str(len(line) - 1))
        logger.debug("Number of files for deletion: " +
                     str(len(line) - int(noCopies) - 1))
        for i in range(int(noCopies), len(line) - 1):
            f = dir + '/' + line[i].split(' ')[0]
            rm_cmd = 'rm ' + f
            code, out, err = utils.run(rm_cmd)
            if code > 0:
                logger.error("Error while removing file: " + f +
                             ", Standard Error: " + err + ", Standard output: " + out)
            else:
                logger.debug("File " + f + " successfully deleted")

        logger.info("Finished deleting files from directory: " + dir)
    else:
        logger.error("Error while listing files with error: " + err +
                     " out: " + out + " code: " + str(code))


def rmold_remote(host, dir, name, noCopies, encrypt):
    """From provided directory, remove files that contain 'name'
        in file name if there is more than 'no_copies' files.

    Args:
        encrypt:
        dir (string): Directory that contains backups
        name (string): Part of the file name
        noCopies (integer): Number of files that will persist in dir
    """
    logger.info("---------------------------------------")
    logger.info("start delete remotely")
    logger.info("---------------------------------------")
    logger.info("Deleting files on host: " + host)
    logger.info("Deleting files from directory: " + str(dir))
    logger.debug("Number of files to save: " + str(noCopies))
    if encrypt.upper() == "FALSE":
        list_cmd = 'ls -t ' + dir + ' | grep \'' + name + '\' | grep -v \'.enc$\''
    else:
        list_cmd = 'ls -t ' + dir + ' | grep -E \'' + name + '.*.enc*\''
    code, out, err = utils.run_remote(list_cmd,host)
    if code == 0:
        line = out.split('\n')
        logger.debug("Number of files: " + str(len(line) - 1))
        logger.debug("Number of files for deletion: " +
                     str(len(line) - int(noCopies) - 1))
        for i in range(int(noCopies), len(line) - 1):
            f = dir + '/' + line[i].split(' ')[0]
            rm_cmd = 'rm ' + f
            code, out, err = utils.run_remote(rm_cmd,host)
            if code > 0:
                logger.error("Error while removing file: " + f +
                             ", Standard Error: " + err + ", Standard output: " + out)
            else:
                logger.debug("File " + f + " successfully deleted")

        logger.info("Finished deleting files from directory: " + dir)
    else:
        logger.error("Error while listing files with error: " + err +
                     " out: " + out + " code: " + str(code))



def keep_only_oldest_and_newest(dir, name, encrypt):
    logger.info("---------------------------------------")
    logger.info("start delete")
    logger.info("---------------------------------------")
    logger.info("Deleting files from directory: " + dir)
    if encrypt.upper() == "FALSE":
        list_cmd = 'ls -t ' + dir + ' | grep \'' + name + \
                   '\' | grep -v \'.enc$\' | grep -v \'.snap$\' | grep -v \'.snap.bak$\''
    else:
        list_cmd = 'ls -t ' + dir + ' | grep -E \'' + name + '.*.enc*\''
    code, out, err = utils.run(list_cmd)
    if code == 0:
        line = out.split('\n')
        logger.debug("Number of files: " + str(len(line) - 1))
        for i in range(1, len(line) - 2):
            f = dir + '/' + line[i].split(' ')[0]
            rm_cmd = 'rm ' + f
            code, out, err = utils.run(rm_cmd)
            if code > 0:
                logger.error("Error while removing file: " + f +
                             ", Standard Error: " + err + ", Standard output: " + out)
            else:
                logger.debug("File " + f + " successfully deleted")
    else:
        logger.error("Error while listing files: " + err)
