import logging
from utils import utils
from file_management import file_management
from datetime import timedelta
from timeit import default_timer as timer

logger = logging.getLogger("backup_logger")


def mysqldump(database, user, password, dest, encrypt, enc_password, no_copies, one_drive=None, one_drive_dir=None):
    try:
        file_name = 'mysqldump_' + database + \
                    '_' + utils.get_curr_date_time() + '.sql'

        mysqldump_cmd = ('/usr/bin/mysqldump -u ' + user +
                         ' -p ' + password +
                         ' --single-transaction --quick --lock-tables=false ' +
                         database + ' > "' +
                         dest + '/' + file_name + '"')
        mysqldump_cmd_log = ('/usr/bin/mysqldump -u ' + user +
                             ' -p *********** --single-transaction --quick --lock-tables=false ' +
                             database + ' > "' +
                             dest + '/' + file_name + '"')
        logger.info("---------------------------------------")
        logger.info("start mysqldump")
        logger.info("---------------------------------------")
        start = timer()
        code, out, err = utils.run(mysqldump_cmd, mysqldump_cmd_log)
        end = timer()
        if code > 0:
            logger.error("Mysqldump failed with status code: " + str(code) + " Standard Error: " + err +
                         ', Standard Output: ' + out)
        else:
            logger.info("Time took for mysqldump :" +
                        str(timedelta(seconds=end - start)))
            logger.info("Created file: " + file_name)
            logger.debug("Directory for primary backup :" + dest)
            if encrypt == 'True':
                file_management.encrypt_data(
                    file_name=dest + '/' + file_name,
                    password=enc_password
                )
                file_name = file_name + '.enc'

            file_management.rmold(
                dir=dest,
                name='mysqldump_' + database,
                no_copies=no_copies,
                encrypt=encrypt
            )

        if one_drive is not None:
            one_drive.upload_file(one_drive_dir=one_drive_dir,
                                  local_dir=dest, file_name=file_name)
            one_drive.remove_old_files(
                file_name='mysqldump_' + database, one_drive_dir=one_drive_dir, encrypt=encrypt, no_copies=no_copies)

    except Exception as e:
        logger.error(e)


def mysqldump_remote(hosts, databases, users, passwords, destinations, encrypts, enc_passwords, no_copies,
                     one_drive=None, one_drive_dir=None):
    try:
        logger.info("---------------------------------------")
        logger.info("start mysqldump")
        logger.info("---------------------------------------")
        db_cnt = user_cnt = pw_cnt = dst_cnt = enc_cnt = enc_pw_cnt = odd_cnt = 0
        for host in hosts:
            file_name = 'mysqldump_' + databases[db_cnt] + \
                        '_' + utils.get_curr_date_time() + '.sql'

            mysqldump_cmd = ('/usr/bin/mysqldump -u ' + users[user_cnt] +
                             ' -p' + passwords[pw_cnt] +
                             ' --single-transaction --quick --lock-tables=false ' +
                             databases[db_cnt] + ' > "' +
                             destinations[dst_cnt] + '/' + file_name + '"')
            mysqldump_cmd_log = ('/usr/bin/mysqldump -u ' + users[user_cnt] +
                                 ' -p ************ --single-transaction --quick --lock-tables=false ' +
                                 databases[db_cnt] + ' > "' +
                                 destinations[dst_cnt] + '/' + file_name + '"')

            start = timer()
            code, out, err = utils.run_remote(mysqldump_cmd, host, mysqldump_cmd_log)
            end = timer()
            if code > 0:
                logger.error("Mysqldump failed with status code: " + str(code) + " Standard Error: " + err +
                             ', Standard Output: ' + out)
            else:
                logger.info("Time took for mysqldump :" +
                            str(timedelta(seconds=end - start)))
                logger.info("Created file: " + file_name)
                logger.debug("Directory for primary backup :" + destinations[dst_cnt])
                if encrypts[enc_cnt] == 'True':
                    file_management.encrypt_data(
                        file_name=destinations[dst_cnt] + '/' + file_name,
                        password=enc_passwords[enc_pw_cnt]
                    )
                    file_name = file_name + '.enc'

                file_management.rmold_remote(
                    host=host,
                    dir=destinations[dst_cnt],
                    name='mysqldump_' + databases[db_cnt],
                    no_copies=no_copies,
                    encrypt=encrypts[enc_cnt]
                )

            if one_drive is not None:
                one_drive.upload_file(one_drive_dir=one_drive_dir[odd_cnt],
                                      local_dir=destinations[dst_cnt], file_name=file_name)
                one_drive.remove_old_files(
                    file_name='mysqldump_' + databases[db_cnt], one_drive_dir=one_drive_dir[odd_cnt],
                    encrypt=encrypts[enc_cnt],
                    no_copies=no_copies)

            if len(hosts) == len(databases):
                db_cnt += 1
            if len(hosts) == len(users):
                user_cnt += 1
            if len(hosts) == len(passwords):
                pw_cnt += 1
            if len(hosts) == len(destinations):
                dst_cnt += 1
            if len(hosts) == len(encrypts):
                enc_cnt += 1
            if len(hosts) == len(enc_passwords):
                enc_pw_cnt += 1
            if len(hosts) == len(one_drive_dir):
                odd_cnt += 1

    except Exception as e:
        logger.error(e)
