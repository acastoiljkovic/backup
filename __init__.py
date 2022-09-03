import sys
from backup import backup

if __name__ == "__main__":
    path = '/etc/backup/config.cnf'
    if len(sys.argv) > 1:
        path = str(sys.argv[1])
    backup.init_logger(path=path)
    backup.run()
