import logging
from datetime import timedelta
from timeit import default_timer as timer
import utils

logger = logging.getLogger("backup_logger")


def DecryptData(fileName, password):
    """Method to decryp encrypted file using aes-256 algorithm. 
    As a result, provided file will be removed, and new file 
    will be without extension .enc.

    Args:
        fileName (string): Full path to the file with .enc extension
        password (string): Salt that is used to encrypt file

    Returns:
        string: Path to the decrypted file
    """
    encCmd = ('openssl enc -aes-256-cbc -d -in ' + fileName + ' -out ' +
              fileName[:len(fileName)-4] + ' -pass pass:' + password)
    logger.info("---------------------------------------")
    logger.info("start decription")
    logger.info("---------------------------------------")
    start = timer()
    code, out, err = utils.Run(encCmd)
    end = timer()
    if code > 0:
        logger.error("Error while decrypting file, status code: "+str(code) +
                     " , standard output: "+out+", standard error: "+err)
        return
    else:
        logger.info("Time took for decrypting :" +
                    str(timedelta(seconds=end - start)))
        logger.debug("Standard output: "+out)
        utils.Run('rm ' + fileName)
        return fileName[:len(fileName)-4]


def EncryptData(fileName, password):
    """Method to encryp provided file using aes-256 algorithm. 
    As a result, provided file will be removed, and new file
    will have extension .enc.

    Args:
        fileName (string): Full path to the file
        password (string): Salt for encryption

    Returns:
        string: Path to the encrypted file
    """
    encCmd = ('openssl '+'enc '+'-aes-256-cbc '+'-in ' + fileName + ' ' +
              '-out ' + fileName + '.enc ' + '-pass pass:' + password)
    logger.info("---------------------------------------")
    logger.info("start encryption")
    logger.info("---------------------------------------")
    start = timer()
    code, out, err = utils.Run(encCmd)
    end = timer()
    if code > 0:
        logger.error("Error while encrypting file, status code: "+str(code) +
                     " , standard output: "+out+", standard error: "+err)
        return
    else:
        logger.info("Time took for encrypting :" +
                    str(timedelta(seconds=end - start)))
        logger.debug("Standard output: "+out)
        utils.Run('rm ' + fileName)
        return fileName + '.enc'


def Copy(file, destination, fileName):
    """Copy file to the new destination with new fileName

    Args:
        file (string): file name
        destination (string): path where to copy file
        fileName (string): new file name
    """
    cpCmd = 'cp ' + file + ' ' + destination + '/' + fileName
    logger.info("---------------------------------------")
    logger.info("start coping files")
    logger.info("---------------------------------------")
    start = timer()
    code, out, err = utils.Run(cpCmd)
    end = timer()
    if code > 0:
        logger.error(err)
        return
    else:
        logger.info("File succesfully copied to: "+destination)
        logger.info("Time took for coping: " +
                    str(timedelta(seconds=end - start)))
        logger.debug("Standard output: "+out)


def Sync(src, dst):
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
    rsyncCmd = 'rsync -a --delete ' + src + ' ' + dst
    start = timer()
    code, out, err = utils.Run(rsyncCmd)
    if code > 0:
        logger.error("Error while synchronizing directories, \
                     standard Error: "+err+", Standard output: "+out)
        return
    else:
        logger.debug("Directories " + src + ' and ' +
                     dst + " are successfully synchronized")
        end = timer()
        logger.info("Time took for synchronization: " +
                    str(timedelta(seconds=end - start)))


def Rmold(dir, name, noCopies, encrypt):
    """From provided directory, remove files that contains 'name' 
        in file name if there is more than 'noCopies' files.

    Args:
        dir (string): Directory that containes backups
        name (string): Part of the file name
        noCopies (integer): Number of files that will persist in dir
    """
    logger.info("---------------------------------------")
    logger.info("start delete")
    logger.info("---------------------------------------")
    logger.info("Deleting files from directory: " + str(dir))
    logger.debug("Number of files to save: "+str(noCopies))
    if encrypt.upper() == "FALSE":
        listCmd = 'ls -t ' + dir + ' | grep \'' + name + '\' | grep -v \'.enc$\''
    else:
        listCmd = 'ls -t ' + dir + ' | grep -E \'' + name + '.*.enc*\''
    code, out, err = utils.Run(listCmd)
    if code == 0:
        line = out.split('\n')
        logger.debug("Number of files: " + str(len(line) - 1))
        logger.debug("Number of files for deletition: " +
                     str(len(line) - int(noCopies) - 1))
        for i in range(int(noCopies), len(line) - 1):
            f = dir + '/' + line[i].split(' ')[0]
            rmCmd = 'rm ' + f
            code, out, err = utils.Run(rmCmd)
            if code > 0:
                logger.error("Error while removing file: "+f +
                             ", Standard Error: "+err+", Standard output: "+out)
            else:
                logger.debug("File "+f+" successfully deleted")

        logger.info("Finished deleting files from directory: " + dir)
    else:
        logger.error("Error wihle listing files with error: "+err +
                     " out: "+out+" code: "+str(code))


def KeepOnlyOldestAndNewest(dir, name, encrypt):
    logger.info("---------------------------------------")
    logger.info("start delete")
    logger.info("---------------------------------------")
    logger.info("Deleting files from directory: " + dir)
    if encrypt.upper() == "FALSE":
        listCmd = 'ls -t ' + dir + ' | grep \'' + name + \
        '\' | grep -v \'.enc$\' | grep -v \'.snap$\' | grep -v \'.snap.bak$\''
    else:
        listCmd = 'ls -t ' + dir + ' | grep -E \'' + name + '.*.enc*\''
    code, out, err = utils.Run(listCmd)
    if code == 0:
        line = out.split('\n')
        logger.debug("Number of files: " + str(len(line) - 1))
        for i in range(1, len(line)-2):
            f = dir + '/' + line[i].split(' ')[0]
            rmCmd = 'rm ' + f
            code, out, err = utils.Run(rmCmd)
            if code > 0:
                logger.error("Error while removing file: "+f +
                             ", Standard Error: "+err+", Standard output: "+out)
            else:
                logger.debug("File "+f+" successfully deleted")
    else:
        logger.error("Error while listing files: "+err)
