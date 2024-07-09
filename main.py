import signal
import sys
from backup import backup
import logging

logger = logging.getLogger("backup_logger")


def catch_hup(signal_umber, frame):
    if signal_umber == signal.SIGHUP:
        backup.reload()


if __name__ == "__main__":
    path = '/etc/backup/backup.cnf'
    if len(sys.argv) > 1:
        path = str(sys.argv[1])
    signal.signal(signal.SIGHUP, catch_hup)
    backup.run(path)
