#!/usr/bin/python3

import configparser
import os


# > This class is used to store configuration data for the application
class ConfigurationData:
    """Class that load configuration from file
    """

    def __init__(
            self,
            no_copies=0,
            log_level='INFO',
            log_path='/var/log/backup/',
            exec_time=None,
            remote_mysql=None,
            remote_sync=None,
            remote_backup_dirs=None,
            backup_mysql=False,
            user_mysql=None,
            password_mysql=None,
            database=None,
            dump_dest=None,
            file_prefix=None,
            encrypt_mysql=False,
            encrypt_mysql_password='e!f@k',
            onedrive_mysql_dir=None,
            backup_dirs=False,
            paths=None,
            destination=None,
            encrypt_dirs=False,
            encrypt_dirs_password='e!f@k',
            backup_type='Full',
            onedrive_backup_dir=None,
            backup_es=False,
            es_url=None,
            es_full=False,
            es_index=None,
            es_location=None,
            es_repo=None,
            es_user=None,
            es_password=None,
            es_remove_old=False,
            es_restore=False,
            sync_dirs=False,
            src=None,
            dst=None,
            upload_to_onedrive=False,
            client_secret=None,
            client_id=None,
            tenant_id=None,
            scopes=None,
            tokens_file=None,
            sync_hosts=None,
            sync_remote_src=None,
            sync_remote_dst=None,
            mysqldump_hosts=None,
            mysqldump_users=None,
            mysqldump_passwords=None,
            mysqldump_databases=None,
            mysqldump_dump_dest=None,
            mysqldump_file_prefixes=None,
            mysqldump_encrypt=None,
            mysqldump_encrypt_passwords=None,
            mysqldump_one_drive_dirs=None,
            dirs2backup_hosts=None,
            dirs2backup_paths=None,
            dirs2backup_destinations=None,
            dirs2backup_encrypt=None,
            dirs2backup_encrypt_passwords=None,
            dirs2backup_backup_type=None,
            dirs2backup_one_drive_dirs=None,
            mysqldump_exec_time=None,
            dirs2backup_exec_time=None,
            elasticsearch_exec_time=None,
            sync_exec_time=None,
            mysqldump_remote_exec_time=None,
            sync_remote_exec_time=None,
            dirs2backup_remote_exec_time=None,
    ):

        """
        A constructor for the class.

        :param no_copies: Number of backup copies to keep, defaults to 0 (optional)
        :param log_level: The level of logging, defaults to INFO (optional)
        :param backup_mysql: Do you want to backup a mysql database?, defaults to False (optional)
        :param user_mysql: The user to connect to the MySQL database
        :param password_mysql: Password for mysql
        :param database: The name of the database to backup
        :param dump_dest: The destination for the mysqldump file
        :param file_prefix: This is the prefix of the file name
        :param encrypt_mysql: If True, the mysqldump will be encrypted with the password in encrypt_mysql_password, defaults
        to False (optional)
        :param encrypt_mysql_password: Password for encrypting the mysqldump file, defaults to e!f@k (optional)
        :param onedrive_mysql_dir: The directory on OneDrive where the mysqldump will be uploaded
        :param backup_dirs: If True, the directories specified in the paths parameter will be backed up, defaults to False
        (optional)
        :param paths: The paths to backup
        :param destination: The destination directory for the backup
        :param encrypt_dirs: If True, the backup will be encrypted, defaults to False (optional)
        :param encrypt_dirs_password: Password for encrypting directories, defaults to e!f@k (optional)
        :param backup_type: Full, Incremental, Differential, defaults to Full (optional)
        :param onedrive_backup_dir: The directory on OneDrive where you want to store the backup
        :param backup_es: If True, Elasticsearch will be backed up, defaults to False (optional)
        :param es_url: The URL of the Elasticsearch cluster
        :param es_full: If True, the entire Elasticsearch database will be backed up. If False, only the specified index
        will be backed up, defaults to False (optional)
        :param es_index: The name of the index to backup
        :param es_location: The location where the Elasticsearch backup will be stored
        :param es_repo: The name of the repository to create
        :param es_user: Elasticsearch user
        :param es_password: Password for elasticsearch
        :param es_remove_old: If you want to remove old backups from the elasticsearch repository, defaults to False
        (optional)
        :param es_restore: If you want to restore an elasticsearch backup, set this to True, defaults to False (optional)
        :param sync_dirs: If True, the script will sync the src and dst directories, defaults to False (optional)
        :param src: The source directory to sync from
        :param dst: The destination directory for the sync
        :param upload_to_onedrive: If True, the script will upload the backup files to OneDrive, defaults to False
        (optional)
        :param client_secret: The client secret you got from the app registration portal
        :param client_id: The client ID of your app
        :param tenant_id: The ID of the Azure Active Directory tenant that you want to use for authentication
        :param scopes: The scopes for which you want to get an access token
        :param tokens_file: The file where the tokens are stored
        :param sync_hosts: List of hosts to sync
        :param sync_remote_src: The source directory on the remote host
        :param sync_remote_dst: The destination directory on the remote host
        :param mysqldump_hosts: List of hosts to do mysqldump on
        :param mysqldump_users: List of users for mysqldump
        :param mysqldump_passwords: The password for the mysql user
        :param mysqldump_databases: The databases to backup
        :param mysqldump_dump_dest: The destination for the mysqldump
        :param mysqldump_file_prefixes: The prefix for the mysqldump file
        :param mysqldump_encrypt: If True, the mysqldump will be encrypted
        :param mysqldump_encrypt_passwords: The password to encrypt the mysqldump file
        :param mysqldump_one_drive_dirs: The directory on OneDrive where the mysqldump will be uploaded
        :param dirs2backup_hosts: List of hosts to backup directories from
        :param dirs2backup_paths: The directories to backup
        :param dirs2backup_destinations: The destination directory for the backup
        :param dirs2backup_encrypt: If True, the backup will be encrypted
        :param dirs2backup_encrypt_passwords: The password to use for encrypting the backup
        :param dirs2backup_backup_type: This is the type of backup to be done. It can be either 'Full' or 'Incremental'
        :param dirs2backup_one_drive_dirs: The directory on OneDrive where the backup will be uploaded
        """
        # GENERAL
        #
        if sync_hosts is None:
            sync_hosts = []
        if sync_remote_src is None:
            sync_remote_src = []
        if sync_remote_dst is None:
            sync_remote_dst = []
        if mysqldump_hosts is None:
            mysqldump_hosts = []
        if mysqldump_users is None:
            mysqldump_users = []
        if mysqldump_passwords is None:
            mysqldump_passwords = []
        if mysqldump_databases is None:
            mysqldump_databases = []
        if mysqldump_dump_dest is None:
            mysqldump_dump_dest = []
        if mysqldump_file_prefixes is None:
            mysqldump_file_prefixes = []
        if mysqldump_encrypt is None:
            mysqldump_encrypt = []
        if mysqldump_encrypt_passwords is None:
            mysqldump_encrypt_passwords = []
        if mysqldump_one_drive_dirs is None:
            mysqldump_one_drive_dirs = []
        if dirs2backup_hosts is None:
            dirs2backup_hosts = []
        if dirs2backup_paths is None:
            dirs2backup_paths = []
        if dirs2backup_destinations is None:
            dirs2backup_destinations = []
        if dirs2backup_encrypt is None:
            dirs2backup_encrypt = []
        if dirs2backup_encrypt_passwords is None:
            dirs2backup_encrypt_passwords = []
        if dirs2backup_backup_type is None:
            dirs2backup_backup_type = []
        if dirs2backup_one_drive_dirs is None:
            dirs2backup_one_drive_dirs = []
        self.no_copies = no_copies
        self.backup_mysql = backup_mysql
        self.backup_dirs = backup_dirs
        self.sync_dirs = sync_dirs
        self.upload_to_onedrive = upload_to_onedrive
        self.log_level = log_level
        self.log_path = log_path
        self.remote_backup_dirs = remote_backup_dirs
        self.remote_sync = remote_sync
        self.remote_mysql = remote_mysql
        self.exec_time = exec_time

        # MYSQL
        #
        self.user_mysql = user_mysql
        self.password_mysql = password_mysql
        self.database = database
        self.dump_destination = dump_dest
        self.file_prefix = file_prefix
        self.encrypt_mysql = encrypt_mysql
        self.encrypt_mysql_password = encrypt_mysql_password
        self.onedrive_mysql_dir = onedrive_mysql_dir
        self.mysqldump_exec_time = mysqldump_exec_time

        # DIRS2BACKUP
        #
        self.paths = paths
        self.destination = destination
        self.encrypt_dirs = encrypt_dirs
        self.encrypt_dirs_password = encrypt_dirs_password
        self.backup_type = backup_type
        self.onedrive_backup_dir = onedrive_backup_dir
        self.dirs2backup_exec_time = dirs2backup_exec_time

        # ELASTICSEARCH
        #
        self.backup_es = backup_es
        self.es_url = es_url
        self.es_full = es_full
        self.es_index = es_index
        self.es_location = es_location
        self.es_repo = es_repo
        self.es_user = es_user
        self.es_password = es_password
        self.es_remove_old = es_remove_old
        self.es_restore = es_restore
        self.elasticsearch_exec_time = elasticsearch_exec_time

        # SYNC
        #
        self.src = src
        self.dst = dst
        self.sync_exec_time = sync_exec_time

        # ONEDRIVE
        #
        self.client_secret = client_secret
        self.client_id = client_id
        self.tenant_id = tenant_id
        self.scopes = scopes
        self.tokens_file = tokens_file

        # SYNC REMOTE
        #
        self.sync_hosts = sync_hosts
        self.sync_remote_src = sync_remote_src
        self.sync_remote_dst = sync_remote_dst
        self.sync_remote_exec_time = sync_remote_exec_time

        # MYSQLDUMP REMOTE
        #
        self.mysqldump_hosts = mysqldump_hosts
        self.mysqldump_users = mysqldump_users
        self.mysqldump_passwords = mysqldump_passwords
        self.mysqldump_databases = mysqldump_databases
        self.mysqldump_dump_dest = mysqldump_dump_dest
        self.mysqldump_file_prefixes = mysqldump_file_prefixes
        self.mysqldump_encrypt = mysqldump_encrypt
        self.mysqldump_encrypt_passwords = mysqldump_encrypt_passwords
        self.mysqldump_one_drive_dirs = mysqldump_one_drive_dirs
        self.mysqldump_remote_exec_time = mysqldump_remote_exec_time

        # DIRS2BACKUP REMOTE
        #
        self.dirs2backup_hosts = dirs2backup_hosts
        self.dirs2backup_paths = dirs2backup_paths
        self.dirs2backup_destinations = dirs2backup_destinations
        self.dirs2backup_encrypt = dirs2backup_encrypt
        self.dirs2backup_encrypt_passwords = dirs2backup_encrypt_passwords
        self.dirs2backup_backup_type = dirs2backup_backup_type
        self.dirs2backup_one_drive_dirs = dirs2backup_one_drive_dirs
        self.dirs2backup_remote_exec_time = dirs2backup_remote_exec_time

    def load_data(self, path):
        """Load data from file at path provided as argument of this method

        Args:
            path (string): absolute or relative path to the configuration file
        """
        print("\nConfig file: " + path)
        if not os.path.exists(path):
            print("ERROR: configuration file '" + path + "' doesn't exists!\n")
            print("Exiting the application...")
            quit()
        config_parser = configparser.RawConfigParser()
        config_parser.read(path)
        for s in config_parser.get('general', 'no_copies', fallback="0").split():
            if s.isdigit():
                self.no_copies = s
        if not self.no_copies:
            self.no_copies = 1

        self.log_level = config_parser.get(
            'general', 'log_level', fallback='INFO')
        self.log_path = config_parser.get(
            'general', 'log_path', fallback='INFO')
        self.remote_mysql = config_parser.get(
            'general', 'remote_mysql', fallback='False')
        self.remote_sync = config_parser.get(
            'general', 'remote_sync', fallback='False')
        self.remote_backup_dirs = config_parser.get(
            'general', 'remote_backup_dirs', fallback='False')
        self.exec_time = config_parser.get(
            'general', 'exec_time', fallback='INFO')

        # MYSQL
        #
        self.backup_mysql = config_parser.get(
            'general', 'backup_mysql', fallback='False')
        self.user_mysql = config_parser.get('mysql', 'user', fallback=None)
        self.password_mysql = config_parser.get(
            'mysql', 'password', fallback=None)
        self.database = config_parser.get('mysql', 'database', fallback=None)
        self.dump_destination = config_parser.get(
            'mysql', 'destination', fallback="")
        self.file_prefix = config_parser.get(
            'mysql', 'file_prefix', fallback=None)
        self.encrypt_mysql = config_parser.get(
            'mysql', 'encrypt', fallback=False)
        self.encrypt_mysql_password = config_parser.get(
            'mysql', 'enc_pass', fallback=None)
        self.onedrive_mysql_dir = config_parser.get(
            'mysql', 'drive_dir', fallback=None)
        self.mysqldump_exec_time = config_parser.get(
            'mysql', 'exec_time', fallback=None)

        # DIRS2BACKUP
        #
        self.backup_dirs = config_parser.get(
            'general', 'backup_dirs', fallback=False)
        self.paths = config_parser.get(
            'dirs2backup', 'path', fallback="").split(';')
        self.destination = config_parser.get('dirs2backup',
                                             'destination', fallback="").split(';')
        self.encrypt_dirs = config_parser.get(
            'dirs2backup', 'encrypt', fallback=False)
        self.encrypt_dirs_password = config_parser.get(
            'dirs2backup', 'enc_pass', fallback=None)
        self.backup_type = config_parser.get(
            'dirs2backup', 'backup_type', fallback='fUll')
        self.onedrive_backup_dir = config_parser.get(
            'dirs2backup', 'drive_dir', fallback=None)
        self.dirs2backup_exec_time = config_parser.get(
            'dirs2backup', 'exec_time', fallback=None)

        # ELASTICSEARCH
        #
        self.backup_es = config_parser.get(
            'general', 'backup_es', fallback=False)
        self.es_url = config_parser.get(
            'elasticsearch', 'es_url', fallback="127.0.0.1:9200")
        self.es_full = config_parser.get('elasticsearch', 'full', fallback=False)
        self.es_index = config_parser.get('elasticsearch', 'index', fallback="")
        self.es_location = config_parser.get(
            'elasticsearch', 'location', fallback="/tmp")
        self.es_repo = config_parser.get('elasticsearch', 'repo', fallback="")
        self.es_user = config_parser.get(
            'elasticsearch', 'user', fallback="elastic")
        self.es_password = config_parser.get(
            'elasticsearch', 'password', fallback="")
        self.es_remove_old = config_parser.get(
            'elasticsearch', 'remove_old', fallback=False)
        self.es_restore = config_parser.get(
            'elasticsearch', 'restore', fallback=False)
        self.elasticsearch_exec_time = config_parser.get(
            'elasticsearch', 'exec_time', fallback=None)

        # SYNC
        #
        self.sync_dirs = config_parser.get(
            'general', 'sync_dirs', fallback=False)
        self.src = config_parser.get('sync', 'src', fallback=None)
        self.dst = config_parser.get('sync', 'dst', fallback=None)
        self.sync_exec_time = config_parser.get(
            'sync', 'exec_time', fallback=None)

        # ONEDRIVE
        #
        self.upload_to_onedrive = config_parser.get(
            'general', 'up2onedrive', fallback=False)
        self.client_secret = config_parser.get(
            'onedrive', 'client_secret', fallback=None)
        self.client_id = config_parser.get(
            'onedrive', 'client_id', fallback=None)
        self.tenant_id = config_parser.get(
            'onedrive', 'tenant_id', fallback=None)
        self.scopes = config_parser.get(
            'onedrive', 'scopes', fallback="").split(';')
        self.tokens_file = config_parser.get(
            'onedrive', 'tokens_file', fallback='./tokens.json')

        # SYNC REMOTE
        #
        self.sync_hosts = config_parser.get(
            'sync_remote', 'hosts', fallback=[]).strip().split(';')
        self.sync_remote_src = config_parser.get(
            'sync_remote', 'src', fallback=[]).split(';')
        self.sync_remote_dst = config_parser.get(
            'sync_remote', 'dst', fallback=[]).split(';')
        self.sync_remote_exec_time = config_parser.get(
            'sync_remote', 'exec_time', fallback=None)

        # MYSQLDUMP REMOTE
        #
        self.mysqldump_hosts = config_parser.get(
            'mysqldump_remote', 'hosts', fallback=[]).strip().split(';')
        self.mysqldump_users = config_parser.get(
            'mysqldump_remote', 'user', fallback=[]).split(';')
        self.mysqldump_passwords = config_parser.get(
            'mysqldump_remote', 'password', fallback=[]).split(';')
        self.mysqldump_databases = config_parser.get(
            'mysqldump_remote', 'database', fallback=[]).split(';')
        self.mysqldump_dump_dest = config_parser.get(
            'mysqldump_remote', 'destination', fallback=[]).split(';')
        self.mysqldump_file_prefixes = config_parser.get(
            'mysqldump_remote', 'file_prefix', fallback=[]).split(';')
        self.mysqldump_encrypt = config_parser.get(
            'mysqldump_remote', 'encrypt', fallback=[]).split(';')
        self.mysqldump_encrypt_passwords = config_parser.get(
            'mysqldump_remote', 'enc_pass', fallback=[]).split(';')
        self.mysqldump_one_drive_dirs = config_parser.get(
            'mysqldump_remote', 'drive_dir', fallback=[]).split(';')
        self.mysqldump_remote_exec_time = config_parser.get(
            'mysqldump_remote', 'exec_time', fallback=None)

        # DIRS2BACKUP REMOTE
        #
        self.dirs2backup_hosts = config_parser.get('dirs2backup_remote', 'hosts', fallback=[]).strip().split(';')
        self.dirs2backup_paths = config_parser.get('dirs2backup_remote', 'path', fallback=[]).split(';')
        self.dirs2backup_destinations = config_parser.get('dirs2backup_remote', 'destination', fallback=[]).split(';')
        self.dirs2backup_encrypt = config_parser.get('dirs2backup_remote', 'encrypt', fallback=[]).split(';')
        self.dirs2backup_encrypt_passwords = config_parser.get('dirs2backup_remote', 'enc_pass', fallback=[]).split(';')
        self.dirs2backup_backup_type = config_parser.get('dirs2backup_remote', 'backup_type', fallback=[]).split(';')
        self.dirs2backup_one_drive_dirs = config_parser.get('dirs2backup_remote', 'drive_dir', fallback=[]).split(';')
        self.dirs2backup_remote_exec_time = config_parser.get('dirs2backup_remote', 'exec_time', fallback=None)

        print("\nConfiguration data loaded successfully!\n")

    def get_all_formatted(self):
        formatted = """
        [general]
        no_copies           = {0}
        backup_mysql        = {1}
        backup_dirs         = {2}
        backup_es           = {3}
        sync_dir            = {4}
        up2onedrive         = {5}
        remote_sync         = {46}
        remote_mysql        = {47}
        remote_backup_dirs  = {48}
        log_level           = {6}
        log_path            = {49}
        exec_time           = {50}

        [mysql]
        user        = {7}
        password    = ************
        database    = {8}
        mysqldump   = {9}
        file_prefix = {10}
        encrypt     = {11}
        enc_pass    = ************
        driveDir    = {12}
        exec_time   = {51}

        [dirs2backup]
        path        = {13}
        destination = {14}
        encrypt     = {15}
        backup_type = {16}
        enc_pass    = ************
        driveDir    = {17}
        exec_time   = {52}

        [elasticsearch]
        es_url      = {18}
        index       = {19}
        location    = {20}
        repo        = {21}
        user        = {22} 
        password    = ************
        remove_old  = {23}
        exec_time   = {53}

        [sync]
        src         = {24}
        dst         = {25}
        exec_time   = {54}

        [onedrive]
        client_secret   = ************************
        client_id       = {26}
        tenant_id       = {27}
        scopes          = {28}
        tokens_file     = {29}
        
        [sync_remote]
        hosts       = {30}
        src         = {31}
        dst         = {32}
        exec_time   = {55}
        
        [mysqldump_remote]
        hosts       = {33}
        user 	 	= {34}
        password 	= **********************
        database 	= {35}
        destination	= {36}
        file_prefix	= {37}
        encrypt		= {38}
        enc_pass	= ***************
        driveDir    = {39}
        exec_time   = {56}
        
        [dirs2backup_remote]
        hosts       = {40}
        paths   	= {41}
        destination	= {42}
        encrypt		= {43}
        enc_pass	= ***************
        backup_type = {44}
        driveDir    = {45}
        exec_time   = {57}
        
        """.format(self.no_copies,
                   self.backup_mysql,
                   self.backup_dirs,
                   self.backup_es,
                   self.sync_dirs,
                   self.upload_to_onedrive,
                   self.log_level,
                   self.user_mysql,
                   self.database,
                   self.dump_destination,
                   self.file_prefix,
                   self.encrypt_mysql,
                   self.onedrive_mysql_dir,
                   self.paths,
                   self.destination,
                   self.encrypt_dirs,
                   self.backup_type,
                   self.onedrive_backup_dir,
                   self.es_url,
                   self.es_index,
                   self.es_location,
                   self.es_repo,
                   self.es_user,
                   self.es_remove_old,
                   self.src,
                   self.dst,
                   self.client_id,
                   self.tenant_id,
                   self.scopes,
                   self.tokens_file,
                   self.sync_hosts,
                   self.sync_remote_src,
                   self.sync_remote_dst,
                   self.mysqldump_hosts,
                   self.mysqldump_users,
                   self.mysqldump_databases,
                   self.mysqldump_dump_dest,
                   self.mysqldump_file_prefixes,
                   self.mysqldump_encrypt,
                   self.mysqldump_one_drive_dirs,
                   self.dirs2backup_hosts,
                   self.dirs2backup_paths,
                   self.dirs2backup_destinations,
                   self.dirs2backup_encrypt,
                   self.dirs2backup_backup_type,
                   self.dirs2backup_one_drive_dirs,
                   self.remote_sync,
                   self.remote_mysql,
                   self.remote_backup_dirs,
                   self.log_path,
                   self.exec_time,
                   self.mysqldump_exec_time,
                   self.dirs2backup_exec_time,
                   self.elasticsearch_exec_time,
                   self.sync_exec_time,
                   self.sync_remote_exec_time,
                   self.mysqldump_remote_exec_time,
                   self.dirs2backup_remote_exec_time,
                   )
        return formatted
