from utils import utils
import requests
import logging

logger = logging.getLogger("backup_logger")


### add shared file system repo ###
# sudo echo 'path.repo: ["/mnt/es_backup"]' >> /etc/elasticsearch/elasticsearch.yml
# sudo chown -R elasticsearch: /mnt/es_backup/
# sudo systemctl restart elasticsearch


def create_repo(es_url, repo_name, location, auth):
    """Create Elasticsearch repo for storing snapshots.

    Note: it's required to set 'path.repo' in 'elasticsearch.yml' in order to use file system path as repo.

    Currently, https is not supported .

    Args:
        es_url (string): URL to Elasticsearch including port. Example: 127.0.0.1:9200 \n
        repo_name (string): Name for the repo. Example: es_backup \n
        location (string): Absolute location on file system that is also added in elasticserach.yml. Example: /mnt/backup \n
        auth (tuple): Tuple that contains username and password. Example: ('user','password')
    """
    try:
        req = requests.post(
            es_url + '/_snapshot/' + repo_name + '/_verify',
            auth=auth,
            headers={'Content-Type': 'application/json'})
        if req.status_code < 200 or req.status_code > 299:
            r = requests.put(
                es_url + '/_snapshot/' + repo_name,
                data='{ "type": "fs", "settings": { "location": "' + location + '" } }',
                auth=auth,
                headers={'Content-Type': 'application/json'})
            if 200 <= r.status_code <= 299:
                logger.info("Created Repo: " + repo_name +
                            ", with physical location: " + location)
            else:
                logger.error(r.content.decode())
        else:
            logger.info("Repo " + repo_name + " already exist!")
    except Exception as e:
        logger.error(str(e))


def create_snapshot_full(es_url, repo, auth):
    """Creating snapshot for all indices in Elasticsearch.

    Args:
        es_url (string): URL to Elasticsearch including port. Example: 127.0.0.1:9200 \n
        repo (string): Repo name where would you like to store snapshots. Example: es_backup \n
        auth (tuple): Tuple that contains username and password. Example: ('user','password')
    """
    try:
        r = requests.put(
            es_url + '/_snapshot/' + repo + '/full' +
            utils.get_curr_date_time() + '?wait_for_completion=true',
            auth=auth,
            headers={'Content-Type': 'application/json'})
        if 200 <= r.status_code <= 299:
            logger.info("Created Snapshot: " +
                        str(r.json()['snapshot']['snapshot']))
            logger.debug(str(r.json()))
        else:
            logger.error(r.content.decode())
    except Exception as e:
        logger.error(str(e))


def create_snapshot_of_index(es_url, repo, index, auth):
    """Create snapshot for provided index.

    Args:
        es_url (string): URL to Elasticsearch including port. Example: 127.0.0.1:9200 \n
        repo (string): Repo name where would you like to store snapshots. Example: es_backup \n
        index (string): Name of the index that snapshot would be created. Example: users \n
        auth (tuple): Tuple that contains username and password. Example: ('user','password')
    """
    try:
        r = requests.put(
            es_url + '/_snapshot/' + repo + '/' + index +
            utils.get_curr_date_time() + '?wait_for_completion=true',
            auth=auth,
            data='{ "indices": "' + index +
                 '", "ignore_unavailable": true, "include_global_state": false }',
            headers={'Content-Type': 'application/json'})
        if 200 <= r.status_code <= 299:
            logger.info("Created Snapshot: " +
                        str(r.json()['snapshot']['snapshot']))
            logger.debug(str(r.json()))
        else:
            logger.error(r.content.decode())
    except Exception as e:
        logger.error(str(e))


def delete_snapshot(es_url, repo, snapshot, auth):
    """Delete provided snapshot.

    Args:
        es_url (string): URL to Elasticsearch including port. Example: 127.0.0.1:9200 \n
        repo (string): Repo name where would you like to store snapshots. Example: es_backup \n
        snapshot (string): Name of the snapshot that would be deleted. Example: users20220703102015 \n
        auth (tuple): Tuple that contains username and password. Example: ('user','password')
    """
    try:
        r = requests.delete(
            es_url + '/_snapshot/' + repo + '/' + snapshot,
            auth=auth,
            headers={'Content-Type': 'application/json'})
        if 200 <= r.status_code <= 299:
            logger.info("Deleting snapshot: " + snapshot)
            logger.debug(str(r.json()))
        else:
            logger.error(r.content.decode())
    except Exception as e:
        logger.error(str(e))


def remove_old_snapshots(es_url, repo, index, auth):
    """Removing all snapshots but one of provided index.

        This method is comparing creation time for all snapshots of index and keping the most recent one.

        Also, do the same for any full snapshot.

    Args:
        es_url (string): URL to Elasticsearch including port. Example: 127.0.0.1:9200 \n
        repo (string): Repo name where would you like to store snapshots. Example: es_backup \n
        index (string): Name of the index which snapshot would be deleted. Example: users \n
        auth (tuple): Tuple that contains username and password. Example: ('user','password')
    """
    try:
        req_all_snap = requests.get(
            es_url + '/_snapshot/' + repo + '/_all',
            auth=auth,
            headers={'Content-Type': 'application/json'})
        start_time = 0
        snapshot = ""
        start_time_full = 0
        snapshot_full = ""
        logger.debug("Searching for old snapshots !")
        for snap in req_all_snap.json()['snapshots']:
            if index != "" and str(index) in str(snap['snapshot']) and snap['start_time_in_millis'] > start_time:
                snapshot = snap['snapshot']
                logger.debug("Found: " + snapshot)
                start_time = snap['start_time_in_millis']
            if snap['start_time_in_millis'] > start_time_full and "full" in str(snap['snapshot']):
                snapshot_full = snap['snapshot']
                logger.debug("Found: " + snapshot_full)
                start_time_full = snap['start_time_in_millis']

        for snap in req_all_snap.json()['snapshots']:
            if index != "" and str(index) in str(snap['snapshot']) and str(snap['snapshot']) != snapshot:
                delete_snapshot(es_url=es_url, repo=repo,
                                snapshot=str(snap['snapshot']), auth=auth)
            if "full" in str(snap['snapshot']) and str(snap['snapshot']) != snapshot_full:
                delete_snapshot(es_url=es_url, repo=repo,
                                snapshot=str(snap['snapshot']), auth=auth)

    except Exception as e:
        logger.error(str(e))


def find_newest_snapshot(es_url, repo, index, auth):
    """Finding the snapshot with most recent creation time.

    Args:
        es_url (string): URL to Elasticsearch including port. Example: 127.0.0.1:9200 \n
        repo (string): Repo name where would you like to store snapshots. Example: es_backup \n
        index (string): Name of the index that snapshot would be created. Example: users \n
        auth (tuple): Tuple that contains username and password. Example: ('user','password')

    Returns:
        _type_: _description_
    """
    try:
        req_all_snap = requests.get(
            es_url + '/_snapshot/' + repo + '/_all',
            auth=auth,
            headers={'Content-Type': 'application/json'})
        start_time = 0
        snapshot = ""
        logger.debug("Searching for old snapshots !")
        if 200 <= req_all_snap.status_code <= 299:
            for snap in req_all_snap.json()['snapshots']:
                if snap['start_time_in_millis'] > start_time and str(index) in str(snap['snapshot']):
                    snapshot = snap['snapshot']
                    logger.debug("Found: " + snapshot)
                    start_time = snap['start_time_in_millis']
            return snapshot
        else:
            logger.error(req_all_snap.content.decode())
            return ""
    except Exception as e:
        logger.error(str(e))


def restore_from_snapshot(es_url, repo, index, auth):
    """ Restore index from most recent snapshot.

        If index exists, it is required to delete it firs, and then run again this method.

    Args:
        es_url (string): URL to Elasticsearch including port. Example: 127.0.0.1:9200 \n
        repo (string): Repo name where would you like to store snapshots. Example: es_backup \n
        index (string): Name of the index that snapshot would be created. Example: users \n
        auth (tuple): Tuple that contains username and password. Example: ('user','password')
    """
    try:
        snapshot_name = find_newest_snapshot(
            es_url=es_url, repo=repo, index=index, auth=auth)
        if snapshot_name != "":
            r = requests.post(
                es_url + '/_snapshot/' + repo + '/' + snapshot_name +
                '/_restore?wait_for_completion=true',
                auth=auth,
                data='{ "indices": "' + index +
                     '", "ignore_unavailable": true, "include_global_state": false }',
                headers={'Content-Type': 'application/json'})
            if 200 <= r.status_code <= 299:
                logger.info("Restoring snapshot: " +
                            snapshot_name + " was successful !")
                logger.debug(r.content.decode())
            else:
                logger.error(r.content.decode())
        else:
            logger.error("There is not any snapshot!")
    except Exception as e:
        logger.error(str(e))
