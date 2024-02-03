import logging
from utils import utils
from file_management import file_management
from datetime import timedelta
from timeit import default_timer as timer

logger = logging.getLogger("backup_logger")


def mysqldump(database, user, password, dest, encrypt="False", enc_password=None, no_copies=3, one_drive=None,
              one_drive_dir=None):
    """
    It takes a database name, user, password, destination directory, encryption password, number of copies to keep, and
    OneDrive object and directory, and then dumps the database to a file in the destination directory, encrypts it if
    encryption is enabled, and uploads it to OneDrive if OneDrive is enabled

    :param database: The name of the database you want to back up
    :param user: The user to connect to the database with
    :param password: The password for the user you're using to connect to the database
    :param dest: The directory where the backup will be stored
    :param encrypt: If you want to encrypt the backup file, set this to True, defaults to False (optional)
    :param enc_password: The password used to encrypt the backup file
    :param no_copies: The number of copies you want to keep, defaults to 3 (optional)
    :param one_drive: This is the OneDrive object that you created in the previous step
    :param one_drive_dir: The directory in OneDrive where the backup will be stored
    """

    try:
        file_name = 'mysqldump_' + database + \
                    '_' + utils.get_curr_date_time() + '.sql'

        mysqldump_cmd = ('/usr/bin/mysqldump -u ' + user +
                         ' -p' + password +
                         ' --single-transaction --quick --lock-tables=false ' +
                         database + ' > "' +
                         dest + '/' + file_name + '"')
        mysqldump_cmd_log = ('/usr/bin/mysqldump -u ' + user +
                             ' -p *********** --single-transaction --quick --lock-tables=false ' +
                             database + ' > "' +
                             dest + '/' + file_name + '"')
        logger.info("---------------------------------------")
        logger.info("start mysqldump")
        logger.info("---------------------------------------")
        start = timer()
        code, out, err = utils.run(mysqldump_cmd, mysqldump_cmd_log)
        end = timer()
        if code > 0:
            logger.error("Mysqldump failed with status code: " + str(code) + " Standard Error: " + err +
                         ', Standard Output: ' + out)
        else:
            logger.info("Time took for mysqldump :" +
                        str(timedelta(seconds=end - start)))
            logger.info("Created file: " + file_name)
            logger.debug("Directory for primary backup :" + dest)
            if encrypt == 'True':
                file_management.encrypt_data(
                    file_name=dest + '/' + file_name,
                    password=enc_password
                )
                file_name = file_name + '.enc'

            file_management.rmold(
                directory=dest,
                name='mysqldump_' + database,
                no_copies=no_copies,
                encrypt=encrypt
            )

        if one_drive is not None:
            one_drive.upload_file(one_drive_dir=one_drive_dir,
                                  local_dir=dest, file_name=file_name)
            one_drive.remove_old_files(
                file_name='mysqldump_' + database, one_drive_dir=one_drive_dir, encrypt=encrypt, no_copies=no_copies)

    except Exception as e:
        logger.error(e)


def mysqldump_remote(host, database, user, password, destination, encrypt, enc_pass, no_copies,
                     one_drive=None, one_drive_dir=None):
    """
    It takes a database name, a hostname, a username, a password, a destination directory, a boolean value for
    encryption, an encryption password, a number of copies to keep, and an optional OneDrive object and OneDrive
    directory, and it dumps the database to a file in the destination directory, encrypts it if encryption is
    enabled, removes old copies of the database dump, and uploads the file to OneDrive if the OneDrive object is
    provided

    :param host: The hostname or IP address of the remote server
    :param database: The name of the database to back up
    :param user: The user to connect to the database with
    :param password: The password for the user
    :param destination: The directory where the backup will be stored
    :param encrypt: True/False
    :param enc_pass: The password used to encrypt the backup file
    :param no_copies: The number of copies to keep
    :param one_drive: This is the OneDrive object that we created in the previous step
    :param one_drive_dir: The directory in OneDrive where the backup will be stored
    """

    try:
        logger.info("---------------------------------------")
        logger.info("start mysqldump")
        logger.info("---------------------------------------")
        file_name = 'mysqldump_' + database + '_' + host + \
                    '_' + utils.get_curr_date_time() + '.sql'

        mysqldump_cmd = ('/usr/bin/mysqldump -u ' + user +
                         ' -p' + password +
                         ' --single-transaction --quick --lock-tables=false ' +
                         database + ' > "' +
                         destination + '/' + file_name + '"')
        mysqldump_cmd_log = ('/usr/bin/mysqldump -u ' + user +
                             ' -p ************ --single-transaction --quick --lock-tables=false ' +
                             database + ' > "' +
                             destination + '/' + file_name + '"')

        start = timer()
        code, out, err = utils.run_remote(mysqldump_cmd, host, mysqldump_cmd_log)
        end = timer()
        if code > 0:
            logger.error("Mysqldump failed with status code: " + str(code) + " Standard Error: " + err +
                         ', Standard Output: ' + out)
        else:
            logger.info("Time took for mysqldump :" +
                        str(timedelta(seconds=end - start)))
            logger.info("Created file: " + file_name)
            logger.debug("Directory for primary backup :" + destination)
            if encrypt == 'True':
                file_management.encrypt_data(
                    file_name=destination + '/' + file_name,
                    password=enc_pass
                )
                file_name = file_name + '.enc'

            file_management.rmold_remote(
                host=host,
                directory=destination,
                name='mysqldump_' + database,
                no_copies=no_copies,
                encrypt=encrypt
            )

        if one_drive is not None:
            one_drive.upload_file(one_drive_dir=one_drive_dir,
                                  local_dir=destination, file_name=file_name)
            one_drive.remove_old_files(
                file_name='mysqldump_' + database, one_drive_dir=one_drive_dir,
                encrypt=encrypt,
                no_copies=no_copies)

    except Exception as e:
        logger.error(e)
