import logging
import utils
import file_management
from datetime import timedelta
from timeit import default_timer as timer

logger = logging.getLogger("backup_logger")


def Mysqldump(database, user, password, dest, encrypt, encPassword, noCopies, oneDrive=None, oneDriveDir=None):
    try:
        fileName = 'mysqldump_' + database + \
                   '_' + utils.GetCurrDateTime() + '.sql'

        mysqldump = ('/usr/bin/mysqldump -u ' + user +
                     ' -p' + password +
                     ' --single-transaction --quick --lock-tables=false ' +
                     database + ' > "' +
                     dest + '/' + fileName + '"')
        logger.info("---------------------------------------")
        logger.info("start mysqldump")
        logger.info("---------------------------------------")
        start = timer()
        code, out, err = utils.Run(mysqldump)
        end = timer()
        if code > 0:
            logger.error("Mysqldump failed with status code: " + str(code) + " Standard Error: " + err +
                         ', Stanadrd Output: ' + out)
        else:
            logger.info("Time took for mysqldump :" +
                        str(timedelta(seconds=end - start)))
            logger.info("Created file: " + fileName)
            logger.debug("Directory for primary backup :" + dest)
            if encrypt == 'True':
                file_management.EncryptData(
                    fileName=dest + '/' + fileName,
                    password=encPassword
                )

            file_management.Rmold(
                dir=dest,
                name='mysqldump_' + database,
                noCopies=noCopies,
                encrypt=encrypt
            )

        if oneDrive is not None:
            oneDrive.UploadFile(oneDriveDir=oneDriveDir,
                                localDir=dest, fileName=fileName)
            oneDrive.RemoveOldFiles(
                fileName='mysqldump_' + database, oneDriveDir=oneDriveDir, encrypt=encrypt, noCopies=noCopies)

    except Exception as e:
        logger.error(e)
