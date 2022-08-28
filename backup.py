import sys

import utils.utils
from config import config
import logging

conf_data = config.ConfigurationData()
logger = logging.getLogger("backup_logger")
one_drive = None


def init_logger(path):
    conf_data.load_data(path=path)
    console_handler = logging.StreamHandler(stream=sys.stdout)
    if conf_data.log_level.upper() == 'DEBUG':
        logger.setLevel(logging.DEBUG)
        console_handler.setLevel(logging.DEBUG)
    elif conf_data.log_level.upper() == 'INFO':
        logger.setLevel(logging.INFO)
        console_handler.setLevel(logging.INFO)
    elif conf_data.log_level.upper() == 'WARNING':
        logger.setLevel(logging.WARNING)
        console_handler.setLevel(logging.WARNING)
    elif conf_data.log_level.upper() == 'ERROR':
        logger.setLevel(logging.ERROR)
        console_handler.setLevel(logging.ERROR)
    elif conf_data.log_level.upper() == 'CRITICAL':
        logger.setLevel(logging.CRITICAL)
        console_handler.setLevel(logging.CRITICAL)
    formatter = logging.Formatter('%(asctime)s  %(levelname)s: %(message)s')
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    logger.debug(conf_data.get_all_formatted())


def run_elastic():
    if conf_data.backup_es.upper() == "TRUE":
        from elastic import elastic

        elastic.create_repo(
            es_url=conf_data.es_url,
            repo_name=conf_data.es_repo,
            location=conf_data.es_location,
            auth=(conf_data.es_user, conf_data.es_password)
        )

        if conf_data.es_index is not None and conf_data.es_full.upper() == "FALSE":
            elastic.create_snapshot_of_index(
                es_url=conf_data.es_url,
                repo=conf_data.es_repo,
                index=conf_data.es_index,
                auth=(conf_data.es_user, conf_data.es_password)
            )

        if conf_data.es_full.upper() == "TRUE":
            elastic.create_snapshot_full(
                es_url=conf_data.es_url,
                repo=conf_data.es_repo,
                auth=(conf_data.es_user, conf_data.es_password)
            )

        if conf_data.es_remove_old.upper() == "TRUE":
            elastic.remove_old_snapshots(
                es_url=conf_data.es_url,
                repo=conf_data.es_repo,
                index=conf_data.es_index,
                auth=(conf_data.es_user, conf_data.es_password)
            )

        # if confData.es_restore.upper() == "TRUE":
        # elastic.RestoreFromSnapshot(
        # es_url=confData.es_url,
        # repo=confData.es_repo,
        # index=confData.es_index,
        # auth=(confData.es_user,confData.es_password)


def run_targz():
    if conf_data.backup_dirs.upper() == "TRUE":
        from targz import targz
        if conf_data.backup_type.upper() == "INCREMENTAL":
            targz.TargzIncremental(
                paths=conf_data.paths,
                destination=conf_data.destination,
                encrypt=conf_data.encrypt_dirs,
                encPass=conf_data.encrypt_dirs_password,
                oneDrive=one_drive,
                oneDriveDir=conf_data.onedrive_backup_dir,
            )
        elif conf_data.backup_type.upper() == "DIFFERENTIAL":
            targz.TargzDifferential(
                paths=conf_data.paths,
                destination=conf_data.destination,
                encrypt=conf_data.encrypt_dirs,
                encPass=conf_data.encrypt_dirs_password,
                oneDrive=one_drive,
                oneDriveDir=conf_data.onedrive_backup_dir,
            )
        elif conf_data.backup_type.upper() == "FULL":
            targz.Targz(
                paths=conf_data.paths,
                destination=conf_data.destination,
                encrypt=conf_data.encrypt_dirs,
                encPass=conf_data.encrypt_dirs_password,
                noCopies=conf_data.no_copies,
                oneDrive=one_drive,
                oneDriveDir=conf_data.onedrive_backup_dir,
            )
        else:
            logger.warning(
                "Targz is True, but the specified backup_type isn't proper. Please check configuration file!")


def run_mysqldump():
    if conf_data.backup_mysql.upper() == "TRUE":
        from mysql import mysql
        mysql.mysqldump(
            database=conf_data.database,
            user=conf_data.user_mysql,
            password=conf_data.password_mysql,
            dest=conf_data.dump_destination,
            encrypt=conf_data.encrypt_mysql,
            enc_password=conf_data.encrypt_mysql_password,
            no_copies=conf_data.no_copies,
            one_drive=one_drive,
            one_drive_dir=conf_data.onedrive_mysql_dir
        )


def run_sync():
    if conf_data.sync_dirs.upper() == "TRUE":
        from file_management import file_management
        file_management.sync(conf_data.src, conf_data.dst)


def run_mysqldump_remote():
    if conf_data.remote_mysql.upper() == "TRUE":
        from mysql import mysql
        mysql.mysqldump_remote(
            hosts=conf_data.mysqldump_hosts,
            users=conf_data.mysqldump_users,
            passwords=conf_data.mysqldump_passwords,
            databases=conf_data.mysqldump_databases,
            encrypts=conf_data.mysqldump_encrypt,
            enc_passwords=conf_data.mysqldump_encrypt_passwords,
            one_drive=one_drive,
            one_drive_dir=conf_data.mysqldump_one_drive_dirs,
            destinations=conf_data.mysqldump_dump_dest,
            no_copies=conf_data.no_copies
        )
        # user = "moodledb"
        # password = "teskasifra1"
        # database = "moodle"
        # dest = "/data"
        # file_name = "moodle-1"
        # mysqldump = ['/usr/bin/mysqldump -u ', user,
        #              ' -p' + password,
        #              ' --single-transaction --quick --lock-tables=false ',
        #              database, ' > ' +
        #              dest + '/' + file_name]
        # print(utils.utils.run_remote(cmd=mysqldump, host="157.90.114.55"))


def init_one_drive():
    global one_drive
    if conf_data.upload_to_onedrive.upper() == "TRUE":
        from one_drive import one_drive
        one_drive = one_drive.OneDrive(
            client_secret=conf_data.client_secret,
            client_id=conf_data.client_id,
            scopes=conf_data.scopes,
            tokens_file=conf_data.tokens_file,
            tenant_id=conf_data.tenant_id,
        )
        one_drive.check_tokens()


def run():
    init_one_drive()
    run_elastic()
    run_mysqldump()
    run_targz()
    run_sync()
    run_mysqldump_remote()
