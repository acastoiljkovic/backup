#!/usr/bin/python3

from os.path import exists
import utils
import logging
import file_management
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
        fileName = filePrefix + '-' + utils.GetCurrDateTime() + '.tar.gz'
        fn = fileName
        fileName = destination[0] + '/' + fileName
        targzCmd = (
            'tar -czvf ' + fileName + ' --absolute-names ' + dir2compress
        )
        start = timer()
        code, out, err = utils.Run(targzCmd)
        if code > 0:
            logger.error(err)
            logger.debug("Status code: "+str(code)+"\tStandard Output: "
                         + out+"\tStandard Error: "+err)
            return

        logger.info("Directory is compressed. File :" +
                    fileName + " succesfully created.")
        end = timer()
        logger.info("Time took for targz :" +
                    str(timedelta(seconds=end - start)))

        if str(encrypt).upper() == 'TRUE':
            fileName = file_management.EncryptData(
                fileName, encPass)
            fn = fn + '.enc'
        oneDrive.UploadFile(oneDriveDir=oneDriveDir,
                            localDir=destination[0], fileName=fn)
        oneDrive.RemoveOldFiles(
            fileName=filePrefix, oneDriveDir=oneDriveDir, encrypt=encrypt, noCopies=noCopies)
        if len(destination) > 1:
            for i in range(0, len(destination)):
                if i != 0:
                    file_management.Copy(fileName, destination[i], fn)
                file_management.Rmold(
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
        fileName = filePrefix + '-' + utils.GetCurrDateTime() + '.tar.gz'
        fn = fileName
        fileName = destination[0] + '/' + fileName
        snapFile = destination[0] + '/' + filePrefix + '.snap'
        targzCmd = (
            'tar -czPg ' + snapFile + ' -f ' + fileName +
            ' --absolute-names ' + dir2compress
        )
        start = timer()
        code, out, err = utils.Run(targzCmd)
        if code > 0:
            logger.error(err)
            logger.debug("Status code: "+str(code)+"\tStandard Output: "
                         + out+"\tStandard Error: "+err)
            return
        logger.info("Directory is compressed. File :" +
                    fileName + " succesfully created.")
        end = timer()
        logger.info("Time took for targz :" +
                    str(timedelta(seconds=end - start)))

        if str(encrypt).upper() == 'TRUE':
            fileName = file_management.EncryptData(
                fileName, encPass)
            fn = fn + '.enc'
        oneDrive.UploadFile(oneDriveDir=oneDriveDir,
                            localDir=destination[0], fileName=fn)
        oneDrive.UploadFile(oneDriveDir=oneDriveDir,
                            localDir=destination[0], fileName=filePrefix + '.snap')
        if len(destination) > 1:
            for i in range(1, len(destination)):
                file_management.Copy(fileName, destination[i], fn)
                file_management.Copy(
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
        filePrefix = filePrefix + "inc"
        fileName = filePrefix + '-' + utils.GetCurrDateTime() + '.tar.gz'
        fn = fileName
        fileName = destination[0] + '/' + fileName
        snapFile = destination[0] + '/' + filePrefix + '.snap'
        snapFileBak = destination[0] + '/' + filePrefix + '.snap.bak'
        targzCmd = (
            'tar -czPg ' + snapFile + ' -f ' + fileName +
            ' --absolute-names ' + dir2compress
        )
        start = timer()
        code, out, err = utils.Run(targzCmd)
        if code > 0:
            logger.error(err)
            logger.debug("Status code: "+str(code)+"\tStandard Output: "
                         + out+"\tStandard Error: "+err)
            return
        logger.info("Directory is compressed. File :" +
                    fileName + " succesfully created.")

        if not exists(snapFileBak):
            utils.Run("cp "+snapFile+" "+snapFileBak)
        else:
            utils.Run("cp "+snapFileBak+" "+snapFile)

        end = timer()
        logger.info("Time took for targz :" +
                    str(timedelta(seconds=end - start)))

        if str(encrypt).upper() == 'TRUE':
            fileName = file_management.EncryptData(
                fileName, encPass)
            fn = fn + '.enc'
        oneDrive.UploadFile(oneDriveDir=oneDriveDir,
                            localDir=destination[0], fileName=fn)

        if len(destination) > 1:
            for i in range(0, len(destination)):
                if i != 0:
                    file_management.Copy(fileName, destination[i], fn)
                    file_management.Copy(
                        snapFile, destination[i], filePrefix + '.snap')
                    file_management.Copy(
                        snapFileBak, destination[i], filePrefix + '.snap.bak')
                file_management.KeepOnlyOldestAndNewest(
                    dir=destination[i], name=filePrefix, encrypt=encrypt)
