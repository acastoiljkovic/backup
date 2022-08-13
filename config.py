#!/usr/bin/python3

import configparser
import os

# KLASA KOJA
#
class ConfigurationData:
    """Class that load configiration from file 
    """
    # KONSTRUKTOR SA DEFAULTNIM VREDNOSTIMA UKOLIKO NEMAMO CONF FILE
    #
    def __init__(
        self,
        noCopies=0,
        logLevel='INFO',
        backupMysql=False,
        userMysql=None,
        passwordMysql=None,
        database=None,
        dumpDest=None,
        filePrefix=None,
        encryptMysql=False,
        encryptMysqlPassword='e!f@k',
        onedriveMysqlDir=None,
        backupDirs=False,
        paths=None,
        destination=None,
        encryptDirs=False,
        encryptDirsPassword='e!f@k',
        onedriveBackupDir=None,
        backupES=False,
        esUrl=None,
        esFull=False,
        esIndex=None,
        esLocation=None,        
        esRepo=None,
        esUser=None,
        esPassword=None,
        esRemoveOld=False,
        esRestore=False,
        syncDirs=False,
        src=None,
        dst=None,
        uploadToOnedrive=False,
        clientSecret=None,
        clientId=None,
        tenantId=None,
        folderId=None,
        scopes=None,
        tokensFile=None,
        backup_type='Full',
    ):
        """Configuration data
        
        Args:
            noCopies (int, optional): Number of backup copies. Defaults to 0.
            logLevel (str, optional): Level of logginf. Defaults to 'INFO'.
            backupMysql (bool, optional): Doing mysqldump?. Defaults to False.
            userMysql (_type_, optional): User for mysql. Defaults to None.
            passwordMysql (_type_, optional): Password for mysql. Defaults to None.
            database (_type_, optional): Mysql database. Defaults to None.
            dumpDest (_type_, optional): Destination for mysqldump. Defaults to None.
            filePrefix (_type_, optional): . Defaults to None.
            encryptMysql (bool, optional): _description_. Defaults to False.
            encryptMysqlPassword (str, optional): _description_. Defaults to 'e!f@k'.
            onedriveMysqlDir (_type_, optional): _description_. Defaults to None.
            backupDirs (bool, optional): _description_. Defaults to False.
            paths (_type_, optional): _description_. Defaults to None.
            destination (_type_, optional): _description_. Defaults to None.
            encryptDirs (bool, optional): _description_. Defaults to False.
            encryptDirsPassword (str, optional): _description_. Defaults to 'e!f@k'.
            onedriveBackupDir (_type_, optional): _description_. Defaults to None.
            syncDirs (bool, optional): _description_. Defaults to False.
            src (_type_, optional): _description_. Defaults to None.
            dst (_type_, optional): _description_. Defaults to None.
            uploadToOnedrive (bool, optional): _description_. Defaults to False.
            clientSecret (_type_, optional): _description_. Defaults to None.
            clientID (_type_, optional): _description_. Defaults to None.
            scopes (_type_, optional): _description_. Defaults to None.
            tokensFile (_type_, optional): _description_. Defaults to None.
            backup_type (string, optional): _description_. Defaults to full.
        """
        # GENERAL
        #
        self.noCopies = noCopies
        self.backupMysql = backupMysql
        self.backupDirs = backupDirs
        self.syncDirs = syncDirs
        self.uploadToOnedrive = uploadToOnedrive
        self.logLevel = logLevel

        # MYSQL
        #
        self.userMysql = userMysql
        self.passwordMysql = passwordMysql
        self.database = database
        self.dumpDestination = dumpDest
        self.filePrefix = filePrefix
        self.encryptMysql = encryptMysql
        self.encryptMysqlPassword = encryptMysqlPassword
        self.onedriveMysqlDir = onedriveMysqlDir

        # DIRS2BACKUP
        #
        self.paths = paths
        self.destination = destination
        self.encryptDirs = encryptDirs
        self.encryptDirsPassword = encryptDirsPassword
        self.backup_type = backup_type
        self.onedriveBackupDir = onedriveBackupDir

        # ELASTICSEARCH
        #
        self.backupES = backupES
        self.esUrl = esUrl
        self.esFull = esFull
        self.esIndex = esIndex
        self.esLocation = esLocation
        self.esRepo = esRepo
        self.esUser = esUser
        self.esPassword = esPassword
        self.esRemoveOld = esRemoveOld
        self.esRestore = esRestore
        # SYNC
        #
        self.src = src
        self.dst = dst

        # ONEDRIVE
        #
        self.clientSecret = clientSecret
        self.clientId = clientId
        self.tenantId = tenantId
        self.folderId = folderId
        self.scopes = scopes
        self.tokensFile = tokensFile

    def LoadData(self, path):
        """Load data from file at path provided as argument of this method

        Args:
            path (string): absolute or relative path to the configuration file
        """
        print("\nConfig file: " + path)
        if os.path.exists(path) == False:
            print("ERROR: configuration file '"+ path +"' doesn't exists!\n")
            print("Exiting the application...")
            quit()
        configParser = configparser.RawConfigParser()
        configParser.read(path)
        for s in configParser.get('general', 'no_copies', fallback="0").split():
            if s.isdigit():
                self.noCopies = s
        if not self.noCopies:
            self.noCopies = 1

        # LOG LEVEL
        #
        self.logLevel = configParser.get('general', 'log_level',fallback='INFO')
        
        # MYSQL
        #
        self.backupMysql = configParser.get('general', 'backup_mysql',fallback='False')
        self.userMysql = configParser.get('mysql', 'user',fallback=None)
        self.passwordMysql = configParser.get('mysql', 'password',fallback=None)
        self.database = configParser.get('mysql', 'database',fallback=None)
        self.dumpDestination = configParser.get('mysql','mysqldump',fallback="")
        self.filePrefix = configParser.get('mysql', 'file_prefix',fallback=None)
        self.encryptMysql = configParser.get('mysql', 'encypt',fallback=False)
        self.encryptMysqlPassword = configParser.get('mysql', 'enc_pass',fallback=None)
        self.onedriveMysqlDir = configParser.get('mysql','driveDir',fallback=None)

        # DIRS2BACKUP
        #
        self.backupDirs = configParser.get('general', 'backup_dirs',fallback=False)
        self.paths = configParser.get('dirs2backup', 'path',fallback="").split(';')
        self.destination = configParser.get('dirs2backup',
                                            'destination',fallback="").split(';')
        self.encryptDirs = configParser.get('dirs2backup', 'encypt',fallback=False)
        self.encryptDirsPassword = configParser.get('dirs2backup', 'enc_pass',fallback=None)
        self.backup_type = configParser.get('dirs2backup','backup_type',fallback='fUll')
        self.onedriveBackupDir = configParser.get('dirs2backup','driveDir',fallback=None)
        # ELASTICSEARCH
        #
        self.backupES = configParser.get('general', 'backup_es',fallback=False)
        self.esUrl = configParser.get('elasticsearch', 'es_url',fallback="127.0.0.1:9200")
        self.esFull = configParser.get('elasticsearch', 'full',fallback=False)
        self.esIndex = configParser.get('elasticsearch', 'index',fallback="")
        self.esLocation = configParser.get('elasticsearch', 'location',fallback="/tmp")
        self.esRepo = configParser.get('elasticsearch', 'repo',fallback="")
        self.esUser = configParser.get('elasticsearch', 'user',fallback="elastic")
        self.esPassword = configParser.get('elasticsearch', 'password',fallback="")
        self.esRemoveOld = configParser.get('elasticsearch', 'remove_old',fallback=False)
        self.esRestore = configParser.get('elasticsearch', 'restore',fallback=False)
        # SYNC
        #
        self.syncDirs = configParser.get('general', 'sync_dirs',fallback=False)
        self.src = configParser.get('sync', 'src',fallback=None)
        self.dst = configParser.get('sync', 'dst',fallback=None)

        # ONEDRIVE
        #
        self.uploadToOnedrive = configParser.get('general', 'up2onedrive',fallback=False)
        self.clientSecret = configParser.get('onedrive', 'client_secret',fallback=None)
        self.clientId = configParser.get('onedrive', 'client_id',fallback=None)
        self.tenantId = configParser.get('onedrive', 'tenant_id',fallback=None)
        self.folderId = configParser.get('onedrive', 'folder_id',fallback=None)
        self.scopes = configParser.get('onedrive', 'scopes',fallback="").split(';')
        self.tokensFile = configParser.get('onedrive', 'tokensFile',fallback='./tokens.json')

        print("\nConfiguration data loaded successfully!\n")

    def GetAllFormated(self):
        formated = """
        [general]
        no_copies   = {0}
        backup_mysql= {1}
        backup_dirs = {2}
        backup_es   = {3}
        sync_dir    = {4}
        up2onedrive = {5}
        log_level   = {6}

        [mysql]
        user        = {7}
        password    = ************
        database    = {8}
        mysqldump   = {9}
        file_prefix = {10}
        encypt      = {11}
        enc_pass    = ************
        driveDir    = {12}

        [dirs2backup]
        path        = {13}
        destination = {14}
        encypt      = {15}
        backup_type = {16}
        enc_pass    = ************
        driveDir    = {17}

        [elasticsearch]
        es_url      = {18}
        index       = {19}
        location    = {20}
        repo        = {21}
        user        = {22} 
        password    = ************
        remove_old  = {23}

        [sync]
        src         = {24}
        dst         = {25}

        [onedrive]
        client_secret   = ************************
        client_id       = {26}
        tenant_id       = {27}
        folder_id       = {28}
        scopes          = {29}
        tokensFile      = {30}
        """.format(self.noCopies,
                   self.backupMysql,
                   self.backupDirs,
                   self.backupES,
                   self.syncDirs,
                   self.uploadToOnedrive,
                   self.logLevel,
                   self.userMysql,
                   self.database,
                   self.dumpDestination,
                   self.filePrefix,
                   self.encryptMysql,
                   self.onedriveMysqlDir,
                   self.paths,
                   self.destination,
                   self.encryptDirs,
                   self.backup_type,
                   self.onedriveBackupDir,
                   self.esUrl,
                   self.esIndex,
                   self.esLocation,
                   self.esRepo,
                   self.esUser,
                   self.esRemoveOld,
                   self.src,
                   self.dst,
                   self.clientId,
                   self.tenantId,
                   self.folderId,
                   self.scopes,
                   self.tokensFile
                   )
        return formated