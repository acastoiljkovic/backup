import signal
import sys
from backup import backup


def catch_hup(signalNumber, frame):
    if signalNumber == signal.SIGHUP:
        backup.reload()


if __name__ == "__main__":
    path = '/etc/backup/backup.cnf'
    if len(sys.argv) > 1:
        path = str(sys.argv[1])
    signal.signal(signal.SIGHUP, catch_hup)
    backup.run(path)
