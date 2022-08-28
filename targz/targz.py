#!/usr/bin/python3

from os.path import exists
from utils import utils
import logging
from file_management import file_management
from datetime import timedelta
from timeit import default_timer as timer

logger = logging.getLogger("backup_logger")


def Targz(paths, destination, encrypt, encPass, noCopies=3, oneDrive=None, oneDriveDir=None):
    for dir2compress in paths:
        logger.info("---------------------------------------")
        logger.info("start targz")
        logger.info("---------------------------------------")
        logger.info("Targz provided directories :" +
                    dir2compress)
        filePrefix = dir2compress.replace(
            '/',
            '-',
        )
        if filePrefix[0] == '-':
            filePrefix = filePrefix[1:len(filePrefix)]
        filePrefix = filePrefix + "full"
        fileName = filePrefix + '-' + utils.get_curr_date_time() + '.tar.gz'
        fn = fileName
        fileName = destination[0] + '/' + fileName
        targzCmd = (
            'tar -czvf ' + fileName + ' --absolute-names ' + dir2compress
        )
        start = timer()
        code, out, err = utils.run(targzCmd)
        if code > 0:
            logger.error(err)
            logger.debug("Status code: "+str(code)+"\tStandard Output: "
                         + out+"\tStandard Error: "+err)
            return

        logger.info("Directory is compressed. File :" +
                    fileName + " successfully created.")
        end = timer()
        logger.info("Time took for targz :" +
                    str(timedelta(seconds=end - start)))

        if str(encrypt).upper() == 'TRUE':
            fileName = file_management.encrypt_data(
                fileName, encPass)
            fn = fn + '.enc'

        if oneDrive is not None:
            oneDrive.upload_file(one_drive_dir=oneDriveDir,
                                 local_dir=destination[0], file_name=fn)
            oneDrive.remove_old_files(
                file_name=filePrefix, one_drive_dir=oneDriveDir, encrypt=encrypt, no_copies=noCopies)
        if len(destination) > 1:
            for i in range(0, len(destination)):
                if i != 0:
                    file_management.copy(fileName, destination[i], fn)
                file_management.rmold(
                    dir=destination[i], name=filePrefix, encrypt=encrypt, noCopies=noCopies)


def TargzIncremental(paths, destination, encrypt, encPass, oneDrive=None, oneDriveDir=None):
    for dir2compress in paths:
        logger.info("---------------------------------------")
        logger.info("start targz incremental")
        logger.info("---------------------------------------")
        logger.info("Targz provided directories :" +
                    dir2compress)
        filePrefix = dir2compress.replace(
            '/',
            '-',
        )
        if filePrefix[0] == '-':
            filePrefix = filePrefix[1:len(filePrefix)]
        filePrefix = filePrefix + "inc"
        fileName = filePrefix + '-' + utils.get_curr_date_time() + '.tar.gz'
        fn = fileName
        fileName = destination[0] + '/' + fileName
        snapFile = destination[0] + '/' + filePrefix + '.snap'
        targzCmd = (
            'tar -czPg ' + snapFile + ' -f ' + fileName +
            ' --absolute-names ' + dir2compress
        )
        start = timer()
        code, out, err = utils.run(targzCmd)
        if code > 0:
            logger.error(err)
            logger.debug("Status code: "+str(code)+"\tStandard Output: "
                         + out+"\tStandard Error: "+err)
            return
        logger.info("Directory is compressed. File :" +
                    fileName + " successfully created.")
        end = timer()
        logger.info("Time took for targz :" +
                    str(timedelta(seconds=end - start)))

        if str(encrypt).upper() == 'TRUE':
            fileName = file_management.encrypt_data(
                fileName, encPass)
            fn = fn + '.enc'

        if oneDrive is not None:
            oneDrive.upload_file(one_drive_dir=oneDriveDir,
                                 local_dir=destination[0], file_name=fn)
            oneDrive.upload_file(one_drive_dir=oneDriveDir,
                                 local_dir=destination[0], file_name=filePrefix + '.snap')
        if len(destination) > 1:
            for i in range(1, len(destination)):
                file_management.copy(fileName, destination[i], fn)
                file_management.copy(
                    snapFile, destination[i], filePrefix + '.snap')


def TargzDifferential(paths, destination, encrypt, encPass, oneDrive=None, oneDriveDir=None):
    for dir2compress in paths:
        logger.info("---------------------------------------")
        logger.info("start targz differential")
        logger.info("---------------------------------------")
        logger.info("Targz provided directories :" +
                    dir2compress)
        filePrefix = dir2compress.replace(
            '/',
            '-',
        )
        if filePrefix[0] == '-':
            filePrefix = filePrefix[1:len(filePrefix)]
        filePrefix = filePrefix + "diff"
        fileName = filePrefix + '-' + utils.get_curr_date_time() + '.tar.gz'
        fn = fileName
        fileName = destination[0] + '/' + fileName
        snapFile = destination[0] + '/' + filePrefix + '.snap'
        snapFileBak = destination[0] + '/' + filePrefix + '.snap.bak'
        targzCmd = (
            'tar -czPg ' + snapFile + ' -f ' + fileName +
            ' --absolute-names ' + dir2compress
        )
        start = timer()
        code, out, err = utils.run(targzCmd)
        if code > 0:
            logger.error(err)
            logger.debug("Status code: "+str(code)+"\tStandard Output: "
                         + out+"\tStandard Error: "+err)
            return
        logger.info("Directory is compressed. File :" +
                    fileName + " successfully created.")

        if not exists(snapFileBak):
            utils.run("cp " + snapFile + " " + snapFileBak)
        else:
            utils.run("cp " + snapFileBak + " " + snapFile)

        end = timer()
        logger.info("Time took for targz :" +
                    str(timedelta(seconds=end - start)))

        if str(encrypt).upper() == 'TRUE':
            fileName = file_management.encrypt_data(
                fileName, encPass)
            fn = fn + '.enc'

        if oneDrive is not None:
            oneDrive.upload_file(one_drive_dir=oneDriveDir,
                                 local_dir=destination[0], file_name=fn)
            oneDrive.upload_file(one_drive_dir=oneDriveDir,
                                 local_dir=destination[0], file_name=filePrefix + '.snap')
            oneDrive.upload_file(one_drive_dir=oneDriveDir,
                                 local_dir=destination[0], file_name=filePrefix + '.snap.bak')
            oneDrive.keep_only_oldest_and_newest(
                file_name=filePrefix, one_drive_dir=oneDriveDir, encrypt=encrypt)

        if len(destination) > 1:
            for i in range(0, len(destination)):
                if i != 0:
                    file_management.copy(fileName, destination[i], fn)
                    file_management.copy(
                        snapFile, destination[i], filePrefix + '.snap')
                    file_management.copy(
                        snapFileBak, destination[i], filePrefix + '.snap.bak')
                file_management.keep_only_oldest_and_newest(
                    dir=destination[i], name=filePrefix, encrypt=encrypt)
