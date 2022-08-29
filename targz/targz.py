#!/usr/bin/python3

from os.path import exists
from utils import utils
import logging
from file_management import file_management
from datetime import timedelta
from timeit import default_timer as timer

logger = logging.getLogger("backup_logger")


def targz(paths, destination, encrypt, enc_pass, no_copies=3, one_drive=None, one_drive_dir=None):
    for dir2compress in paths:
        logger.info("---------------------------------------")
        logger.info("start targz")
        logger.info("---------------------------------------")
        logger.info("Targz provided directories :" +
                    dir2compress)
        file_prefix = dir2compress.replace(
            '/',
            '-',
        )
        if file_prefix[0] == '-':
            file_prefix = file_prefix[1:len(file_prefix)]
        file_prefix = file_prefix + "full"
        file_name = file_prefix + '-' + utils.get_curr_date_time() + '.tar.gz'
        fn = file_name
        file_name = destination[0] + '/' + file_name
        targz_cmd = (
            'tar -czvf ' + file_name + ' --absolute-names ' + dir2compress
        )
        start = timer()
        code, out, err = utils.run(targz_cmd)
        if code > 0:
            logger.error(err)
            logger.debug("Status code: "+str(code)+"\tStandard Output: "
                         + out+"\tStandard Error: "+err)
            return

        logger.info("Directory is compressed. File :" +
                    file_name + " successfully created.")
        end = timer()
        logger.info("Time took for targz :" +
                    str(timedelta(seconds=end - start)))

        if str(encrypt).upper() == 'TRUE':
            file_name = file_management.encrypt_data(
                file_name, enc_pass)
            fn = fn + '.enc'

        if one_drive is not None:
            one_drive.upload_file(one_drive_dir=one_drive_dir,
                                  local_dir=destination[0], file_name=fn)
            one_drive.remove_old_files(
                file_name=file_prefix, one_drive_dir=one_drive_dir, encrypt=encrypt, no_copies=no_copies)
        if len(destination) > 1:
            for i in range(0, len(destination)):
                if i != 0:
                    file_management.copy(file_name, destination[i], fn)
                file_management.rmold(
                    dir=destination[i], name=file_prefix, encrypt=encrypt, no_copies=no_copies)


def targz_incremental(paths, destination, encrypt, enc_pass, one_drive=None, one_drive_dir=None):
    for dir2compress in paths:
        logger.info("---------------------------------------")
        logger.info("start targz incremental")
        logger.info("---------------------------------------")
        logger.info("Targz provided directories :" +
                    dir2compress)
        file_prefix = dir2compress.replace(
            '/',
            '-',
        )
        if file_prefix[0] == '-':
            file_prefix = file_prefix[1:len(file_prefix)]
        file_prefix = file_prefix + "inc"
        file_name = file_prefix + '-' + utils.get_curr_date_time() + '.tar.gz'
        fn = file_name
        file_name = destination[0] + '/' + file_name
        snap_file = destination[0] + '/' + file_prefix + '.snap'
        targz_cmd = (
            'tar -czPg ' + snap_file + ' -f ' + file_name +
            ' --absolute-names ' + dir2compress
        )
        start = timer()
        code, out, err = utils.run(targz_cmd)
        if code > 0:
            logger.error(err)
            logger.debug("Status code: "+str(code)+"\tStandard Output: "
                         + out+"\tStandard Error: "+err)
            return
        logger.info("Directory is compressed. File :" +
                    file_name + " successfully created.")
        end = timer()
        logger.info("Time took for targz :" +
                    str(timedelta(seconds=end - start)))

        if str(encrypt).upper() == 'TRUE':
            file_name = file_management.encrypt_data(
                file_name, enc_pass)
            fn = fn + '.enc'

        if one_drive is not None:
            one_drive.upload_file(one_drive_dir=one_drive_dir,
                                  local_dir=destination[0], file_name=fn)
            one_drive.upload_file(one_drive_dir=one_drive_dir,
                                  local_dir=destination[0], file_name=file_prefix + '.snap')
        if len(destination) > 1:
            for i in range(1, len(destination)):
                file_management.copy(file_name, destination[i], fn)
                file_management.copy(
                    snap_file, destination[i], file_prefix + '.snap')


def targz_differential(paths, destination, encrypt, enc_pass, one_drive=None, one_drive_dir=None):
    for dir2compress in paths:
        logger.info("---------------------------------------")
        logger.info("start targz differential")
        logger.info("---------------------------------------")
        logger.info("Targz provided directories :" +
                    dir2compress)
        file_prefix = dir2compress.replace(
            '/',
            '-',
        )
        if file_prefix[0] == '-':
            file_prefix = file_prefix[1:len(file_prefix)]
        file_prefix = file_prefix + "diff"
        file_name = file_prefix + '-' + utils.get_curr_date_time() + '.tar.gz'
        fn = file_name
        file_name = destination[0] + '/' + file_name
        snap_file = destination[0] + '/' + file_prefix + '.snap'
        snap_file_bak = destination[0] + '/' + file_prefix + '.snap.bak'
        targz_cmd = (
            'tar -czPg ' + snap_file + ' -f ' + file_name +
            ' --absolute-names ' + dir2compress
        )
        start = timer()
        code, out, err = utils.run(targz_cmd)
        if code > 0:
            logger.error(err)
            logger.debug("Status code: "+str(code)+"\tStandard Output: "
                         + out+"\tStandard Error: "+err)
            return
        logger.info("Directory is compressed. File :" +
                    file_name + " successfully created.")

        if not exists(snap_file_bak):
            utils.run("cp " + snap_file + " " + snap_file_bak)
        else:
            utils.run("cp " + snap_file_bak + " " + snap_file)

        end = timer()
        logger.info("Time took for targz :" +
                    str(timedelta(seconds=end - start)))

        if str(encrypt).upper() == 'TRUE':
            file_name = file_management.encrypt_data(
                file_name, enc_pass)
            fn = fn + '.enc'

        if one_drive is not None:
            one_drive.upload_file(one_drive_dir=one_drive_dir,
                                  local_dir=destination[0], file_name=fn)
            one_drive.upload_file(one_drive_dir=one_drive_dir,
                                  local_dir=destination[0], file_name=file_prefix + '.snap')
            one_drive.upload_file(one_drive_dir=one_drive_dir,
                                  local_dir=destination[0], file_name=file_prefix + '.snap.bak')
            one_drive.keep_only_oldest_and_newest(
                file_name=file_prefix, one_drive_dir=one_drive_dir, encrypt=encrypt)

        if len(destination) > 1:
            for i in range(0, len(destination)):
                if i != 0:
                    file_management.copy(file_name, destination[i], fn)
                    file_management.copy(
                        snap_file, destination[i], file_prefix + '.snap')
                    file_management.copy(
                        snap_file_bak, destination[i], file_prefix + '.snap.bak')
                file_management.keep_only_oldest_and_newest(
                    dir=destination[i], name=file_prefix, encrypt=encrypt)
