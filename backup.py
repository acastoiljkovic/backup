import config
import logging
import one_drive


confData = config.ConfigurationData()
confData.LoadData(path="/home/aleksandar/Elfak/diplomski/backup/config.cnf")
logger = logging.getLogger("backup_logger")
oneDrive = None

def InitLogger():
    consoleHandler =  logging.StreamHandler()
    if confData.logLevel.upper() == 'DEBUG':
        logger.setLevel(logging.DEBUG)
        consoleHandler.setLevel(logging.DEBUG)
    elif confData.logLevel.upper() == 'INFO':
        logger.setLevel(logging.INFO)
        consoleHandler.setLevel(logging.INFO)
    elif confData.logLevel.upper() == 'WARRNING':
        logger.setLevel(logging.WARNING)
        consoleHandler.setLevel(logging.WARNING)
    elif confData.logLevel.upper() == 'ERROR':
        logger.setLevel(logging.ERROR)
        consoleHandler.setLevel(logging.ERROR)
    elif confData.logLevel.upper() == 'CRITICAL':
        logger.setLevel(logging.CRITICAL)
        consoleHandler.setLevel(logging.CRITICAL)
    formatter = logging.Formatter('%(asctime)s  %(levelname)s: %(message)s')
    consoleHandler.setFormatter(formatter)
    logger.addHandler(consoleHandler)
    logger.debug(confData.GetAllFormated())

def RunElastic():
    if confData.backupES.upper() == "TRUE":
        import elastic
        
        elastic.CreateRepo(
            es_url=confData.esUrl,
            repo_name=confData.esRepo,
            location=confData.esLocation,
            auth=(confData.esUser,confData.esPassword)
            )
        
        if confData.esIndex != None:
            elastic.CreateSnapshotOfIndex(
                es_url=confData.esUrl,
                repo=confData.esRepo,
                index=confData.esIndex,
                auth=(confData.esUser,confData.esPassword)
                )
            
        if confData.esFull.upper() == "TRUE":
            elastic.CreateSnapshotFull(
                es_url=confData.esUrl,
                repo=confData.esRepo,
                auth=(confData.esUser,confData.esPassword)
                )
        
        if confData.esRemoveOld.upper() == "TRUE":
            elastic.RemoveOldSnapshots(
                es_url=confData.esUrl,
                repo=confData.esRepo,
                index=confData.esIndex,
                auth=(confData.esUser,confData.esPassword)
                )
        if confData.esRestore.upper() == "TRUE":  
            # elastic.RestoreFromSnapshot(
                es_url=confData.esUrl,
                repo=confData.esRepo,
                index=confData.esIndex,
                auth=(confData.esUser,confData.esPassword)
        

def RunTargz():
    if confData.backupDirs.upper() == "TRUE":
        import targz
        if confData.backup_type.upper() == "INCREMENTAL":
            targz.TargzIncremental(
                paths=confData.paths,
                destination=confData.destination,
                encrypt=confData.encryptDirs,
                encPass=confData.encryptDirsPassword,
                )
        elif confData.backup_type.upper() == "DIFERENTIAL": 
            targz.TargzDifferential(
                paths=confData.paths,
                destination=confData.destination,
                encrypt=confData.encryptDirs,
                encPass=confData.encryptDirsPassword,
                )
        elif confData.backup_type.upper() == "FULL": 
            targz.Targz(
                paths=confData.paths,
                destination=confData.destination,
                encrypt=confData.encryptDirs,
                encPass=confData.encryptDirsPassword,
                )
        else:
            logger.warn("Targz is True, but the specified backup_type isn't proper. Please check configuration file!")

def RunMysqldump():
    if confData.backupMysql.upper() == "TRUE":
        import mysql
        mysql.Mysqldump(
            database=confData.database,
            user=confData.userMysql,
            password=confData.passwordMysql,
            dest=confData.dumpDestination,
            encrypt=confData.encryptMysql,
            encPassword=confData.encryptMysqlPassword,
            noCopies=confData.noCopies
        )

def RunSync():
    if confData.syncDirs.upper() == "TRUE":
        import file_management
        file_management.Sync(confData.src,confData.dst)
        
def InitOneDrive():
    if confData.uploadToOnedrive.upper() == "TRUE":
        oneDrive = one_drive.OneDrive(
            clientSecret=confData.clientSecret,
            clientID=confData.clientId,
            scopes=confData.scopes,
            tokensFile=confData.tokensFile,
            tenantId=confData.tenantId,
            folderId=confData.folderId
         )
        oneDrive.CheckTokens()
        

def Run():
    InitOneDrive()
    RunElastic()
    RunMysqldump()
    RunTargz()
    RunSync()

if __name__ == "__main__":
    InitLogger()
    Run()