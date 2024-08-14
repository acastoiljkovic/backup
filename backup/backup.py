from config import config
import logging.handlers
import schedule
from one_drive import one_drive

conf_data = None
config_data = None
logger = logging.getLogger("backup_logger")
onedrive = None
log_level = None
log_path = None
exec_time = None
one_drive_general = None
include = None
no_copies = 3
config_file_path = '/etc/backup/backup.cnf'


def mysql_module(mysql_conf):
    from mysql import mysql
    if mysql_conf.host is None or \
            mysql_conf.host == '' or mysql_conf.host == '127.0.0.1' or mysql_conf.host == 'localhost':
        if mysql_conf.upload_to_onedrive.upper() == 'TRUE' and onedrive is not None:
            mysql.mysqldump(
                database=mysql_conf.database,
                user=mysql_conf.user,
                password=mysql_conf.password,
                dest=mysql_conf.destination,
                encrypt=mysql_conf.encrypt,
                enc_password=mysql_conf.enc_pass,
                no_copies=mysql_conf.no_copies,
                one_drive=onedrive,
                one_drive_dir=mysql_conf.drive_dir
            )
        else:
            mysql.mysqldump(
                database=mysql_conf.database,
                user=mysql_conf.user,
                password=mysql_conf.password,
                dest=mysql_conf.destination,
                encrypt=mysql_conf.encrypt,
                enc_password=mysql_conf.enc_pass,
                no_copies=mysql_conf.no_copies,
                one_drive=None,
                one_drive_dir=None
            )
    else:
        if mysql_conf.upload_to_onedrive.upper() == 'TRUE' and onedrive is not None:
            mysql.mysqldump_remote(
                host=mysql_conf.host,
                user=mysql_conf.user,
                password=mysql_conf.password,
                database=mysql_conf.database,
                encrypt=mysql_conf.encrypt,
                enc_pass=mysql_conf.enc_pass,
                one_drive=onedrive,
                one_drive_dir=mysql_conf.drive_dir,
                destination=mysql_conf.destination,
                no_copies=mysql_conf.no_copies
            )
        else:
            mysql.mysqldump_remote(
                host=mysql_conf.host,
                user=mysql_conf.user,
                password=mysql_conf.password,
                database=mysql_conf.database,
                encrypt=mysql_conf.encrypt,
                enc_pass=mysql_conf.enc_pass,
                one_drive=None,
                one_drive_dir=None,
                destination=mysql_conf.destination,
                no_copies=mysql_conf.no_copies
            )


def rsync_module(sync):
    from file_management import file_management
    if sync.host is None or sync.host == '' or sync.host == '127.0.0.1' or sync.host == 'localhost':
        file_management.sync(sync.src, sync.dst)
    else:
        file_management.sync_remote(
            host=sync.host,
            source=sync.src,
            destination=sync.dst
        )


def elastic_module(elast):
    from elastic import elastic
    elastic.create_repo(
        es_url=elast.url,
        repo_name=elast.repo,
        location=elast.location,
        auth=(elast.user, elast.password)
    )

    if elast.index is not None and elast.full.upper() == "FALSE":
        elastic.create_snapshot_of_index(
            es_url=elast.url,
            repo=elast.repo,
            index=elast.index,
            auth=(elast.user, elast.password)
        )

    if elast.full.upper() == "TRUE":
        elastic.create_snapshot_full(
            es_url=elast.url,
            repo=elast.repo,
            auth=(elast.user, elast.password)
        )

    if elast.remove_old.upper() == "TRUE":
        elastic.remove_old_snapshots(
            es_url=elast.url,
            repo=elast.repo,
            index=elast.index,
            auth=(elast.user, elast.password)
        )


def targz_module(dirs):
    from targz import targz
    if type(dirs.path) is str:
        dirs.path = dirs.path.split(';')
    if type(dirs.destination) is str:
        dirs.destination = dirs.destination.split(';')
    if dirs.host is not None:
        if dirs.backup_type.upper() == "INCREMENTAL":
            if dirs.upload_to_onedrive.upper() == 'TRUE' and onedrive is not None:
                targz.targz_incremental_remote(
                    host=dirs.host,
                    paths=dirs.path,
                    destinations=dirs.destination,
                    encrypt=dirs.encrypt,
                    enc_pass=dirs.enc_pass,
                    one_drive=onedrive,
                    one_drive_dir=dirs.drive_dir
                )
            else:
                targz.targz_incremental_remote(
                    host=dirs.host,
                    paths=dirs.path,
                    destinations=dirs.destination,
                    encrypt=dirs.encrypt,
                    enc_pass=dirs.enc_pass,
                    one_drive=None,
                    one_drive_dir=None
                )
        elif dirs.backup_type.upper() == "DIFFERENTIAL":
            if dirs.upload_to_onedrive.upper() == 'TRUE' and onedrive is not None:
                targz.targz_differential_remote(
                    host=dirs.host,
                    paths=dirs.path,
                    destinations=dirs.destination,
                    encrypt=dirs.encrypt,
                    enc_pass=dirs.enc_pass,
                    one_drive=onedrive,
                    one_drive_dir=dirs.drive_dir
                )
            else:
                targz.targz_differential_remote(
                    host=dirs.host,
                    paths=dirs.path,
                    destinations=dirs.destination,
                    encrypt=dirs.encrypt,
                    enc_pass=dirs.enc_pass,
                    one_drive=None,
                    one_drive_dir=None
                )
        elif dirs.backup_type.upper() == "FULL":
            if dirs.upload_to_onedrive.upper() == 'TRUE' and onedrive is not None:
                targz.targz_remote(
                    host=dirs.host,
                    paths=dirs.path,
                    destinations=dirs.destination,
                    encrypt=dirs.encrypt,
                    enc_pass=dirs.enc_pass,
                    one_drive=onedrive,
                    one_drive_dir=dirs.drive_dir
                )
            else:
                targz.targz_remote(
                    host=dirs.host,
                    paths=dirs.path,
                    destinations=dirs.destination,
                    encrypt=dirs.encrypt,
                    enc_pass=dirs.enc_pass,
                    one_drive=None,
                    one_drive_dir=None
                )
        else:
            logger.warning(
                "Remote_backup_dirs is True, "
                "but the specified backup_type isn't proper. "
                "Please check configuration file!")
    else:
        if dirs.backup_type.upper() == "INCREMENTAL":
            if dirs.upload_to_onedrive.upper() == 'TRUE' and onedrive is not None:
                targz.targz_incremental(
                    paths=dirs.path,
                    destinations=dirs.destination,
                    encrypt=dirs.encrypt,
                    enc_pass=dirs.enc_pass,
                    one_drive=onedrive,
                    one_drive_dir=dirs.drive_dir,
                )
            else:
                targz.targz_incremental(
                    paths=dirs.path,
                    destinations=dirs.destination,
                    encrypt=dirs.encrypt,
                    enc_pass=dirs.enc_pass,
                    one_drive=None,
                    one_drive_dir=None,
                )
        elif dirs.backup_type.upper() == "DIFFERENTIAL":
            if dirs.upload_to_onedrive.upper() == 'TRUE' and onedrive is not None:
                targz.targz_differential(
                    paths=dirs.path,
                    destinations=dirs.destination,
                    encrypt=dirs.encrypt,
                    enc_pass=dirs.enc_pass,
                    one_drive=onedrive,
                    one_drive_dir=dirs.drive_dir,
                )
            else:
                targz.targz_differential(
                    paths=dirs.path,
                    destinations=dirs.destination,
                    encrypt=dirs.encrypt,
                    enc_pass=dirs.enc_pass,
                    one_drive=None,
                    one_drive_dir=None,
                )
        elif dirs.backup_type.upper() == "FULL":
            if dirs.upload_to_onedrive.upper() == 'TRUE' and onedrive is not None:
                targz.targz(
                    paths=dirs.path,
                    destinations=dirs.destination,
                    encrypt=dirs.encrypt,
                    enc_pass=dirs.enc_pass,
                    one_drive=onedrive,
                    one_drive_dir=dirs.drive_dir,
                )
            else:
                targz.targz(
                    paths=dirs.path,
                    destinations=dirs.destination,
                    encrypt=dirs.encrypt,
                    enc_pass=dirs.enc_pass,
                    one_drive=None,
                    one_drive_dir=None,
                )
        else:
            logger.warning(
                "Targz is True, but the specified backup_type isn't proper. Please check configuration file!")


def run_modules(conf):
    for dirs in conf.dirs_config:
        targz_module(dirs)
    for elast in conf.elastic_config:
        elastic_module(elast)
    for sync in conf.rsync_config:
        rsync_module(sync)
    for mysql_conf in conf.mysql_config:
        mysql_module(mysql_conf)


def schedule_modules(conf):
    from utils import utils
    for dirs in conf.dirs_config:
        if type(dirs.path) is str:
            dirs.path = dirs.path.split(';')
        if type(dirs.destination) is str:
            dirs.destination = dirs.destination.split(';')
        seconds, minutes, hours, days = utils.parse_time(dirs.exec_time)
        utils.schedule_job(func_name=targz_module,
                           seconds=seconds,
                           minutes=minutes,
                           hours=hours,
                           days=days,
                           args=dirs)

    for elast in conf.elastic_config:
        seconds, minutes, hours, days = utils.parse_time(elast.exec_time)
        utils.schedule_job(func_name=elastic_module,
                           seconds=seconds,
                           minutes=minutes,
                           hours=hours,
                           days=days,
                           args=elast)

    for sync in conf.rsync_config:
        seconds, minutes, hours, days = utils.parse_time(sync.exec_time)
        utils.schedule_job(func_name=rsync_module,
                           seconds=seconds,
                           minutes=minutes,
                           hours=hours,
                           days=days,
                           args=sync)

    for mysql_conf in conf.mysql_config:
        seconds, minutes, hours, days = utils.parse_time(mysql_conf.exec_time)
        utils.schedule_job(func_name=mysql_module,
                           seconds=seconds,
                           minutes=minutes,
                           hours=hours,
                           days=days,
                           args=mysql_conf)


def run(path):
    global config_file_path
    config_file_path = path
    run_or_schedule_based_on_config(config_file_path)


def run_scheduled():
    import time
    schedule.run_all()
    while True:
        schedule.run_pending()
        time.sleep(10)


def reload():
    logger.info("Reloading configuration !")
    for job in schedule.get_jobs():
        schedule.cancel_job(job)
    global config_file_path
    run_or_schedule_based_on_config(config_file_path)


def run_or_schedule_based_on_config(path):
    global config_data
    global log_level
    global no_copies
    global log_path
    global exec_time
    global onedrive
    global one_drive_general
    global include

    config_data, no_copies, log_level, log_path, exec_time, include, onedrive_config = config.load_configuration(path)
    scheduled_exists = 0
    for conf in config_data:
        if conf.onedrive_config is not None:
            onedrive = one_drive.OneDrive(
                client_secret=conf.onedrive_config.client_secret,
                client_id=conf.onedrive_config.client_id,
                scopes=conf.onedrive_config.scopes,
                tokens_file=conf.onedrive_config.tokens_file,
                tenant_id=conf.onedrive_config.tenant_id,
            )
        elif onedrive_config is not None:
            onedrive = one_drive.OneDrive(
                client_secret=onedrive_config.client_secret,
                client_id=onedrive_config.client_id,
                scopes=onedrive_config.scopes,
                tokens_file=onedrive_config.tokens_file,
                tenant_id=onedrive_config.tenant_id,
            )
        if onedrive is not None:
            onedrive.check_tokens()
        if conf.exec_time is None:
            run_modules(conf)
        else:
            schedule_modules(conf)
            scheduled_exists = 1
    if scheduled_exists == 1:
        run_scheduled()
