#!/usr/bin/python3
import sys
import configparser
import os
import logging
import logging.handlers
import utils.utils
import glob

logger = logging.getLogger("backup_logger")


# > This class is used to store configuration data for the application
class ConfigurationData:

    def __init__(
            self,
            no_copies=3,
            log_file='/var/log/backup',
            log_level='INFO',
            exec_time='* * * *',
            mysql_config=None,
            elastic_config=None,
            dirs_config=None,
            rsync_config=None,
            onedrive_config=None
    ):
        """
        This class contains all important data for doing backup.

        :param no_copies: number of copies to keep, defaults to 3 (optional)
        :param log_file: The path to the log file, defaults to /var/log/backup (optional)
        :param log_level: The level of logging, defaults to INFO (optional)
        :param exec_time: The time when the backup should be executed, defaults to * * * * (optional)
        :param mysql_config: a list of dictionaries, each dictionary containing the following keys:
        :param elastic_config: A list of Elasticsearch instances to backup
        :param dirs_config: a list of dictionaries, each dictionary contains the following keys:
        :param rsync_config: This is a list of dictionaries. Each dictionary contains the following keys:
        :param onedrive_config: This is the configuration for the onedrive client
        """
        self.no_copies = no_copies
        self.log_file = log_file
        self.log_level = log_level
        self.exec_time = exec_time
        self.onedrive_config = onedrive_config
        if mysql_config is None:
            self.mysql_config = []
        if elastic_config is None:
            self.elastic_config = []
        if dirs_config is None:
            self.dirs_config = []
        if rsync_config is None:
            self.rsync_config = []
        self.logger = logging.getLogger("backup_logger")

    def load_config(self, path):
        """
        It reads a config file and populates the object with the values

        :param path: The path to the configuration file
        """
        self.logger.info("Config file: " + path)
        if not os.path.exists(path):
            self.logger.error("Configuration file '" + path + "' doesn't exists!")
            self.logger.info("Exiting the application...")
            quit()
        config_parser = configparser.RawConfigParser()
        config_parser.read(path)

        if config_parser.has_section('mysqldump_remote'):
            self.logger.debug("Contains mysqldump_remote")
            mysql_config = MysqlConfig()
            mysql_config.no_copies = config_parser.get(
                'mysqldump_remote', 'no_copies', fallback=self.no_copies)
            mysql_config.host = config_parser.get(
                'mysqldump_remote', 'host', fallback=None)
            if mysql_config.host is not None:
                mysql_config.host.strip()
            mysql_config.user = config_parser.get(
                'mysqldump_remote', 'user', fallback=None)
            mysql_config.password = config_parser.get(
                'mysqldump_remote', 'password', fallback=None)
            mysql_config.database = config_parser.get(
                'mysqldump_remote', 'database', fallback=None)
            mysql_config.destination = config_parser.get(
                'mysqldump_remote', 'destination', fallback='')
            mysql_config.encrypt = config_parser.get(
                'mysqldump_remote', 'encrypt', fallback='')
            mysql_config.enc_pass = config_parser.get(
                'mysqldump_remote', 'enc_pass', fallback='')
            mysql_config.upload_to_onedrive = config_parser.get(
                'mysqldump_remote', 'upload_to_onedrive', fallback='False')
            mysql_config.drive_dir = config_parser.get(
                'mysqldump_remote', 'drive_dir', fallback='')
            mysql_config.exec_time = config_parser.get(
                'mysqldump_remote', 'exec_time', fallback=self.exec_time)
            self.mysql_config.append(mysql_config)

        if config_parser.has_section("mysql"):
            self.logger.debug("Contains mysql")
            mysql_config = MysqlConfig()
            mysql_config.no_copies = config_parser.get(
                'mysql', 'no_copies', fallback=self.no_copies)
            mysql_config.user = config_parser.get(
                'mysql', 'user', fallback=None)
            mysql_config.password = config_parser.get(
                'mysql', 'password', fallback=None)
            mysql_config.database = config_parser.get(
                'mysql', 'database', fallback=None)
            mysql_config.destination = config_parser.get(
                'mysql', 'destination', fallback='')
            mysql_config.encrypt = config_parser.get(
                'mysql', 'encrypt', fallback='')
            mysql_config.enc_pass = config_parser.get(
                'mysql', 'enc_pass', fallback='')
            mysql_config.upload_to_onedrive = config_parser.get(
                'mysql', 'upload_to_onedrive', fallback='False')
            mysql_config.drive_dir = config_parser.get(
                'mysql', 'drive_dir', fallback='')
            mysql_config.exec_time = config_parser.get(
                'mysql', 'exec_time', fallback=self.exec_time)
            self.mysql_config.append(mysql_config)

        if config_parser.has_section('sync_remote'):
            self.logger.debug("Contains sync_remote")
            rsync_config = RsyncConfig()
            rsync_config.host = config_parser.get(
                'sync_remote', 'host', fallback='')
            if rsync_config.host is not None:
                rsync_config.host.strip()
            rsync_config.src = config_parser.get(
                'sync_remote', 'src', fallback='')
            rsync_config.dst = config_parser.get(
                'sync_remote', 'dst', fallback='')
            rsync_config.exec_time = config_parser.get(
                'sync_remote', 'exec_time', fallback=self.exec_time)
            self.rsync_config.append(rsync_config)

        if config_parser.has_section('sync'):
            self.logger.debug("Contains sync")
            rsync_config = RsyncConfig()
            rsync_config.src = config_parser.get(
                'sync', 'src', fallback='')
            rsync_config.dst = config_parser.get(
                'sync', 'dst', fallback='')
            rsync_config.exec_time = config_parser.get(
                'sync', 'exec_time', fallback=self.exec_time)
            self.rsync_config.append(rsync_config)

        if config_parser.has_section('dirs2backup_remote'):
            self.logger.debug("Contains dirs2backup_remote")
            dirs_config = DirConfig()
            dirs_config.no_copies = config_parser.get(
                'dirs2backup_remote', 'no_copies', fallback=self.no_copies)
            dirs_config.host = config_parser.get(
                'dirs2backup_remote', 'host', fallback='')
            if dirs_config.host is not None:
                dirs_config.host.strip()
            dirs_config.path = config_parser.get(
                'dirs2backup_remote', 'path', fallback='')
            dirs_config.destination = config_parser.get(
                'dirs2backup_remote', 'destination', fallback='')
            dirs_config.encrypt = config_parser.get(
                'dirs2backup_remote', 'encrypt', fallback='')
            dirs_config.enc_pass = config_parser.get(
                'dirs2backup_remote', 'enc_pass', fallback='')
            dirs_config.backup_type = config_parser.get(
                'dirs2backup_remote', 'backup_type', fallback='')
            dirs_config.upload_to_onedrive = config_parser.get(
                'dirs2backup_remote', 'upload_to_onedrive', fallback='False')
            dirs_config.drive_dir = config_parser.get(
                'dirs2backup_remote', 'drive_dir', fallback='')
            dirs_config.exec_time = config_parser.get(
                'dirs2backup_remote', 'exec_time', fallback=self.exec_time)
            self.dirs_config.append(dirs_config)

        if config_parser.has_section('dirs2backup'):
            self.logger.debug("Contains dirs2backup")
            dirs_config = DirConfig()
            dirs_config.no_copies = config_parser.get(
                'dirs2backup', 'no_copies', fallback=self.no_copies)
            dirs_config.path = config_parser.get(
                'dirs2backup', 'path', fallback='')
            dirs_config.destination = config_parser.get(
                'dirs2backup', 'destination', fallback='')
            dirs_config.encrypt = config_parser.get(
                'dirs2backup', 'encrypt', fallback='')
            dirs_config.enc_pass = config_parser.get(
                'dirs2backup', 'enc_pass', fallback='')
            dirs_config.backup_type = config_parser.get(
                'dirs2backup', 'backup_type', fallback='')
            dirs_config.upload_to_onedrive = config_parser.get(
                'dirs2backup', 'upload_to_onedrive', fallback='False')
            dirs_config.drive_dir = config_parser.get(
                'dirs2backup', 'drive_dir', fallback='')
            dirs_config.exec_time = config_parser.get(
                'dirs2backup', 'exec_time', fallback=self.exec_time)
            self.dirs_config.append(dirs_config)

        if config_parser.has_section("elasticsearch"):
            self.logger.debug("Contains elasticsearch")
            elastic_config = ElasticConfig()
            elastic_config.url = config_parser.get(
                'elasticsearch', 'url', fallback="127.0.0.1:9200")
            elastic_config.full = config_parser.get('elasticsearch', 'full', fallback="False")
            elastic_config.index = config_parser.get('elasticsearch', 'index', fallback="")
            elastic_config.location = config_parser.get(
                'elasticsearch', 'location', fallback="/tmp")
            elastic_config.repo = config_parser.get('elasticsearch', 'repo', fallback="")
            elastic_config.user = config_parser.get(
                'elasticsearch', 'user', fallback="elastic")
            elastic_config.password = config_parser.get(
                'elasticsearch', 'password', fallback="")
            elastic_config.remove_old = config_parser.get(
                'elasticsearch', 'remove_old', fallback='False')
            elastic_config.exec_time = config_parser.get(
                'elasticsearch', 'exec_time', fallback=self.exec_time)
            self.elastic_config.append(elastic_config)

        if config_parser.has_section('onedrive'):
            self.logger.debug("Contains onedrive")
            onedrive = OneDriveConfig()
            onedrive.client_secret = config_parser.get(
                'onedrive', 'client_secret', fallback='')
            onedrive.client_id = config_parser.get(
                'onedrive', 'client_id', fallback='')
            onedrive.tenant_id = config_parser.get(
                'onedrive', 'tenant_id', fallback='')
            onedrive.scopes = config_parser.get(
                'onedrive', 'scopes', fallback="").split(';')
            onedrive.tokens_file = config_parser.get(
                'onedrive', 'tokens_file', fallback='/etc/backup/tokens.json')
            if self.onedrive_config is not None:
                logger.warning("OneDrive config exists in main file and will be overwritten!")
                self.onedrive_config = onedrive
            else:
                self.onedrive_config = onedrive

    def print_formatted(self):
        """
        It prints the configuration of the object
        """
        if self.onedrive_config is not None:
            self.logger.debug(self.onedrive_config.formatted())
        if self.elastic_config is not None:
            for elastic in self.elastic_config:
                self.logger.debug(elastic.formatted())
        if self.mysql_config is not None:
            for mysql in self.mysql_config:
                self.logger.debug(mysql.formatted())
        if self.dirs_config is not None:
            for dirs in self.dirs_config:
                self.logger.debug(dirs.formatted())
        if self.rsync_config is not None:
            for rsync in self.rsync_config:
                self.logger.debug(rsync.formatted())


class MysqlConfig:

    def __init__(
            self,
            no_copies=3,
            host=None,
            user=None,
            password=None,
            database=None,
            destination=None,
            encrypt='False',
            enc_pass=None,
            upload_to_onedrive='False',
            drive_dir=None,
            exec_time='* * * *',
            onedrive=None
    ):
        self.no_copies = no_copies
        self.host = host
        self.user = user
        self.password = password
        self.database = database
        self.destination = destination
        self.encrypt = encrypt
        self.enc_pass = enc_pass
        self.upload_to_onedrive = upload_to_onedrive
        self.drive_dir = drive_dir
        self.exec_time = exec_time
        self.onedrive = onedrive

    def formatted(self):
        if self.host is not None:
            formatted = """
        [mysqldump_remote]
        no_copies           = {0}
        host                = {1}
        user                = {2}
        password            = **********************
        database            = {3}
        destination         = {4}
        encrypt             = {5}
        enc_pass            = ***************
        upload_to_onedrive  = {6}
        drive_dir           = {7}
        exec_time           = {8}
            """.format(
                self.no_copies,
                self.host,
                self.user,
                self.database,
                self.destination,
                self.encrypt,
                self.upload_to_onedrive,
                self.drive_dir,
                self.exec_time
            )
        else:
            formatted = """
        [mysql]
        no_copies           = {0}
        user                = {1}
        password            = **********************
        database            = {2}
        destination         = {3}
        encrypt             = {4}
        enc_pass            = ***************
        upload_to_onedrive  = {5}
        drive_dir           = {6}
        exec_time           = {7}
            """.format(
                self.no_copies,
                self.user,
                self.database,
                self.destination,
                self.encrypt,
                self.upload_to_onedrive,
                self.drive_dir,
                self.exec_time
            )
        return formatted


class DirConfig:

    def __init__(
            self,
no_copies=3,
path=None,
host=None,
destination=None,
backup_type='full',
encrypt='False',
enc_pass=None,
upload_to_onedrive='False',
drive_dir=None,
exec_time='* * * *',
onedrive=None
    ):
        self.no_copies = no_copies
        self.path = path
        self.host = host
        self.destination = destination
        self.backup_type = backup_type
        self.encrypt = encrypt
        self.enc_pass = enc_pass
        self.upload_to_onedrive = upload_to_onedrive
        self.drive_dir = drive_dir
        self.exec_time = exec_time
        self.onedrive = onedrive

    def formatted(self):
        if self.host is not None:
            formatted = """
        [dirs2backup_remote]
        no_copies           = {0}
        host                = {1}
        host                = {2}
        destination         = {3}
        encrypt             = {4}
        enc_pass            = ***************
        backup_type         = {5}
        upload_to_onedrive  = {6}
        drive_dir           = {7}
        exec_time           = {8}
            """.format(
                self.no_copies,
                self.host,
                self.path,
                self.destination,
                self.encrypt,
                self.backup_type,
                self.upload_to_onedrive,
                self.drive_dir,
                self.exec_time
            )
        else:
            formatted = """
        [dirs2backup]
        no_copies           = {0}
        path                = {1}
        destination         = {2}
        encrypt             = {3}
        enc_pass            = ***************
        backup_type         = {4}
        upload_to_onedrive  = {5}
        drive_dir           = {6}
        exec_time           = {7}
            """.format(
                self.no_copies,
                self.path,
                self.destination,
                self.encrypt,
                self.backup_type,
                self.upload_to_onedrive,
                self.drive_dir,
                self.exec_time
            )

        return formatted


class RsyncConfig:

    def __init__(
            self,
            host=None,
            src=None,
            dst=None,
            exec_time='* * * *'
    ):
        self.host = host
        self.src = src
        self.dst = dst
        self.exec_time = exec_time

    def formatted(self):
        if self.host is not None:
            formatted = """
        [sync_remote]
        host                = {0}
        src                 = {1}
        dst                 = {2}
        exec_time           = {3}
            """.format(
                self.host,
                self.src,
                self.dst,
                self.exec_time
            )
        else:
            formatted = """
        [sync]
        src                 = {0}
        dst                 = {1}
        exec_time           = {2}
            """.format(
                self.src,
                self.dst,
                self.exec_time
            )
        return formatted


class OneDriveConfig:

    def __init__(
            self,
            client_secret=None,
            client_id=None,
            tenant_id='common',
            scopes=None,
            token_file='/etc/backup/tokens.json'
    ):
        self.client_secret = client_secret
        self.client_id = client_id
        self.tenant_id = tenant_id
        self.scopes = scopes
        self.token_file = token_file

    def formatted(self):
        formatted = """
        [onedrive]
        client_secret       = ************************
        client_id           = {0}
        tenant_id           = {1}
        scopes              = {2}
        tokens_file         = {3}
        """.format(
            self.client_id,
            self.tenant_id,
            self.scopes,
            self.token_file
        )
        return formatted


class ElasticConfig:

    def __init__(
            self,
            url=None,
            index=None,
            full='True',
            location=None,
            repo=None,
            user=None,
            password=None,
            remove_old='True',
            exec_time='* * * *'
    ):
        self.url = url
        self.full = full
        self.index = index
        self.location = location
        self.repo = repo
        self.user = user
        self.password = password
        self.remove_old = remove_old
        self.exec_time = exec_time

    def formatted(self):
        formatted = """
        [elasticsearch]
        url                 = {0}
        full                = {1}
        index               = {2}
        location            = {3}
        repo                = {4}
        user                = {5} 
        password            = ************
        remove_old          = {6}
        exec_time           = {7}
        """.format(
            self.url,
            self.full,
            self.index,
            self.location,
            self.repo,
            self.user,
            self.remove_old,
            self.exec_time
        )
        return formatted


def load_configuration(path='/etc/backup/backup.cnf'):
    """
    It reads the configuration file and returns a list of objects of type ConfData

    :param path: The path to the configuration file, defaults to /etc/backup/backup.cnf (optional)
    """
    print("\n" + utils.utils.get_curr_date_time_log_format() + "  INFO: Config file: " + path)
    if not os.path.exists(path):
        print(
            utils.utils.get_curr_date_time_log_format() + "  ERROR: configuration file '" +
            path + "' doesn't exists!\n")
        print(utils.utils.get_curr_date_time_log_format() + "  INFO: Exiting the application...")
        quit()
    config_parser = configparser.RawConfigParser()
    config_parser.read(path)
    no_copies = 3
    for s in config_parser.get('general', 'no_copies', fallback="3").split():
        if s.isdigit():
            no_copies = s
    log_level = config_parser.get(
        'general', 'log_level', fallback='INFO')
    log_path = config_parser.get(
        'general', 'log_path', fallback='/var/log/backup')
    exec_time = config_parser.get(
        'general', 'exec_time', fallback='* * * *')
    include = config_parser.get(
        'general', 'include', fallback=None)
    if include is not None:
        include.strip()

    init_logger(log_level, log_path)

    onedrive = None

    if config_parser.has_section('onedrive'):
        onedrive = OneDriveConfig()
        onedrive.client_secret = config_parser.get(
            'onedrive', 'client_secret', fallback='')
        onedrive.client_id = config_parser.get(
            'onedrive', 'client_id', fallback='')
        onedrive.tenant_id = config_parser.get(
            'onedrive', 'tenant_id', fallback='')
        onedrive.scopes = config_parser.get(
            'onedrive', 'scopes', fallback="").split(';')
        onedrive.tokens_file = config_parser.get(
            'onedrive', 'tokens_file', fallback='/etc/backup/tokens.json')

    formatted = """
        [genera]
        no_copies   = {0}
        log_level   = {1}
        log_path    = {2}
        exec_time   = {3}
        include     = {4}
        """.format(
        no_copies,
        log_level,
        log_path,
        exec_time,
        include
    )

    logger.debug(formatted)

    conf_data = []

    if include is None or include == '':
        data = ConfigurationData(no_copies, log_level, log_path, exec_time, onedrive_config=onedrive)
        data.load_config(path)
        conf_data.append(data)
        data.print_formatted()
    else:
        conf_data = get_conf_data(include, no_copies, log_level, log_path, exec_time, onedrive)

    return conf_data, no_copies, log_level, log_path, exec_time, include, onedrive


def get_conf_data(include, no_copies, log_level, log_path, exec_time, onedrive):
    """
    It takes in a bunch of arguments, and returns a list of objects of type ConfigurationData

    :param include: The path to the configuration file
    :param no_copies: The number of copies to keep
    :param log_level: The level of logging to use
    :param log_path: The path to the log file
    :param exec_time: The time to execute the backup
    :param onedrive: This is the onedrive configuration data
    :return: A list of ConfigurationData objects.
    """
    conf_data = []
    if include is None or include == '':
        logger.warning("There is no include directive! ")
    else:
        for file in glob.glob(include):
            data = ConfigurationData(no_copies, log_level, log_path, exec_time, onedrive_config=onedrive)
            data.load_config(file)
            conf_data.append(data)
            data.print_formatted()

    return conf_data


def init_logger(log_level, log_path):
    """
    It initializes the logger with the given log level and log path

    :param log_level: This is the level of logging you want to do. It can be DEBUG, INFO, WARNING, ERROR, or CRITICAL
    :param log_path: The path where the log file will be created
    """
    try:
        console_handler = logging.StreamHandler(stream=sys.stdout)
        if log_level.upper() == 'DEBUG':
            logger.setLevel(logging.DEBUG)
            console_handler.setLevel(logging.DEBUG)
        elif log_level.upper() == 'INFO':
            logger.setLevel(logging.INFO)
            console_handler.setLevel(logging.INFO)
        elif log_level.upper() == 'WARNING':
            logger.setLevel(logging.WARNING)
            console_handler.setLevel(logging.WARNING)
        elif log_level.upper() == 'ERROR':
            logger.setLevel(logging.ERROR)
            console_handler.setLevel(logging.ERROR)
        elif log_level.upper() == 'CRITICAL':
            logger.setLevel(logging.CRITICAL)
            console_handler.setLevel(logging.CRITICAL)
        formatter = logging.Formatter('%(asctime)s  %(levelname)s: %(message)s')
        console_handler.setFormatter(formatter)
        rotate_handler = logging.handlers.RotatingFileHandler("{0}/{1}.log".format(log_path, "system"),
                                                              maxBytes=1048576, backupCount=5)
        rotate_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
        logger.addHandler(rotate_handler)
    except Exception as e:
        print(utils.utils.get_curr_date_time_log_format() + " ERROR: while initializing logger : " + str(e))
