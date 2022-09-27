from utils import utils
import requests
import logging
from timeit import default_timer as timer
from datetime import timedelta

logger = logging.getLogger("backup_logger")


# add shared file system repo
# sudo echo 'path.repo: ["/mnt/es_backup"]' >> /etc/elasticsearch/elasticsearch.yml
# sudo chown -R elasticsearch: /mnt/es_backup/
# sudo systemctl restart elasticsearch


def create_repo(es_url, repo_name, location, auth):
    """
    Create repo in Elasticsearch.

    :param es_url: The URL of the Elasticsearch cluster
    :param repo_name: The name of the repository
    :param location: The location of the repository
    :param auth: This is the authentication information for the Elasticsearch cluster
    """
    logger.info("---------------------------------------")
    logger.info("start snapshotting elasticsearch")
    logger.info("---------------------------------------")
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
    """
    It creates a snapshot of the entire cluster

    :param es_url: The URL of the Elasticsearch cluster
    :param repo: The name of the repository to create the snapshot in
    :param auth: This is the authentication information for the Elasticsearch cluster
    """

    try:
        start = timer()
        r = requests.put(
            es_url + '/_snapshot/' + repo + '/full' +
            utils.get_curr_date_time() + '?wait_for_completion=true',
            auth=auth,
            headers={'Content-Type': 'application/json'})
        if 200 <= r.status_code <= 299:
            logger.info("Created Snapshot: " +
                        str(r.json()['snapshot']['snapshot']))
            logger.debug(str(r.json()))
            end = timer()
            logger.info("Time took for creating snapshot: " +
                        str(timedelta(seconds=end - start)))
        else:
            logger.error(r.content.decode())
    except Exception as e:
        logger.error(str(e))


def create_snapshot_of_index(es_url, repo, index, auth):
    """
    It creates a snapshot of the index passed as a parameter

    :param es_url: The URL of the Elasticsearch cluster
    :param repo: The name of the repository to use
    :param index: The name of the index to snapshot
    :param auth: This is the authentication for the Elasticsearch cluster
    """

    try:
        start = timer()
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
            end = timer()
            logger.info("Time took for creating snapshot: " +
                        str(timedelta(seconds=end - start)))
        else:
            logger.error(r.content.decode())
    except Exception as e:
        logger.error(str(e))


def delete_snapshot(es_url, repo, snapshot, auth):
    """
    It takes the Elasticsearch URL, the repository name, the snapshot name, and the authentication credentials as arguments,
    and then deletes the snapshot

    :param es_url: The URL of the Elasticsearch cluster
    :param repo: The name of the repository to use
    :param snapshot: The name of the snapshot to delete
    :param auth: The authentication credentials for the Elasticsearch cluster
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
    """
    It will delete all snapshots except the latest one for each index and the latest full snapshot

    :param es_url: The URL of the Elasticsearch cluster
    :param repo: The name of the repository to use
    :param index: The name of the index to be backed up
    :param auth: This is the authentication information for the Elasticsearch cluster
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
    """
    It takes the Elasticsearch URL, the repository name, the index name and the authentication credentials as input and
    returns the name of the latest snapshot of the index

    :param es_url: The URL of the Elasticsearch cluster
    :param repo: The name of the repository you want to use
    :param index: The name of the index you want to backup
    :param auth: This is the authentication information for the Elasticsearch cluster
    :return: The name of the snapshot.
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
    """
    It restores the latest snapshot of the index.

    :param es_url: The URL of the Elasticsearch instance
    :param repo: The name of the repository to use
    :param index: The name of the index to be backed up
    :param auth: This is a tuple of the username and password for the Elasticsearch instance
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
