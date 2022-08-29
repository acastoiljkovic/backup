from datetime import timedelta
import os
from urllib.parse import urlparse
from urllib.parse import parse_qs
import requests
import pathlib
import json
import logging
from timeit import default_timer as timer
from dateutil import parser

logger = logging.getLogger("backup_logger")


class OneDrive:
    def __init__(
            self,
            client_secret,
            client_id,
            scopes,
            tokens=None,
            tokens_file='./tokens.json',
            tenant_id="common"
    ):
        """This is the class to work with OneDrive. It consists of several parts:
            generating and refreshing access token, uploading files to OneDrive,
            removing old files from OneDrive

        Args:
            client_secret (string): Client secret gained form Microsoft application
            client_id (string): Client ID gained from Microsoft application
            scopes (array): Array of Microsoft scopes ie. ['User.Read']
            tokens (json, optional): JSON object that contains access and refresh tokens. Defaults to None.
            tokens_file (str, optional): File where JSON tokes will be stored. Defaults to './tokens.json'.
            tenant_id (string, optional): Microsoft Tenant ID where your application is being deployd.
                                         If you are using personal account backup system will use default "common".
        """
        self.client_secret = client_secret
        self.client_id = client_id
        self.scopes = scopes
        self.__GRAPH_API_URL = "https://graph.microsoft.com/v1.0"
        self.__LOGIN_BASE_URL = "https://login.microsoftonline.com"
        self.__OAUTH2_BASE_URL = self.__LOGIN_BASE_URL + "/" + tenant_id + "/oauth2/v2.0"
        self.__AUTHORIZE_BASE_URL = self.__OAUTH2_BASE_URL + "/authorize"
        self.__TOKENS_BASE_URL = self.__OAUTH2_BASE_URL + "/token"
        # size of fragment should be divisible with 320KB, currently it's 31.25MB
        self.__CHUNK_SIZE = 32768000
        self.tokens = tokens
        self.tokens_file = tokens_file

        self.__perform_login()

    def __get_tokens_from_file(self):
        if pathlib.Path(self.tokens_file).is_file():
            try:
                logger.debug("Opening file: " + self.tokens_file)
                with open(self.tokens_file, 'r') as f:
                    content = f.read()
                    tokens = json.loads(content)
                    logger.debug("Reading token from file: " + str(tokens))
                    f.close()
                    self.tokens = tokens
                    return True
            except Exception as e:
                logger.error("Error while reading tokens from file: " + str(e))
                return False
        else:
            logger.debug("File: " + self.tokens_file + " doesn't exists !")
            self.tokens = None
            return False

    def create_authorization_url(self):
        authorization_url = (
                self.__AUTHORIZE_BASE_URL +
                '?client_id=' +
                self.client_id +
                '&response_type=code' +
                '&scope='
        )
        for scope in self.scopes:
            if scope != "":
                authorization_url += scope + ' '
        authorization_url = authorization_url[:-1]
        authorization_url += '+offline_access+openid+profile'
        logger.debug("Created authorization URL: " +
                     authorization_url.replace(' ', '%20'))
        return authorization_url.replace(' ', '%20')

    def check_tokens(self):
        if self.tokens is not None:
            if self.tokens['access_token'] is not None:
                logger.debug('Access token exists')
                if self.tokens['refresh_token'] is not None:
                    logger.debug('Refresh token exists')
                    get_list_url = self.__GRAPH_API_URL + f'/me/drive/items/root/children'
                    headers = {
                        'Authorization': 'Bearer ' + self.tokens['access_token'],
                    }
                    response = requests.get(
                        get_list_url,
                        headers=headers
                    )
                    logger.debug(response.json())
                    if 200 <= response.status_code < 300:
                        logger.info("Tokens are valid!")
                    elif response.status_code == 401:
                        logger.warning("Tokens expired !")
                        self.renew_tokens()
                    else:
                        logger.error("Unexpected error: " + str(response.content))
                return True
        else:
            self.__perform_login()

        return False

    def get_tokens(self, redirection_url):
        code = parse_qs(urlparse(redirection_url).query)['code'][0]
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        try:
            scope_post = ''
            for scope in self.scopes:
                if scope != "":
                    scope_post += scope + ' '
            scope_post = scope_post[:-1]
            self.tokens = requests.post(url=self.__TOKENS_BASE_URL, data={
                'client_id': self.client_id,
                'scope': scope_post,
                'code': code,
                'grant_type': 'authorization_code',
                'client_secret': self.client_secret
            }, headers=headers
                                        ).json()
            self.__save_tokens_to_file()
        except Exception as e:
            logger.error("Error while getting tokens: " + str(e))

    def __save_tokens_to_file(self):
        try:
            with open(self.tokens_file, 'w') as f:
                logger.debug("Opening file: " + self.tokens_file)
                f.write(json.dumps(self.tokens))
                logger.debug("Tokens are successfully written to a file")
                f.close()
        except Exception as e:
            logger.error("Error while writing tokens to a file " + str(e))

    def renew_tokens(self):
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded'
        }

        new_tokens = requests.post(url=self.__TOKENS_BASE_URL, data={
            'client_id': self.client_id,
            'scope': self.scopes,
            'refresh_token': self.tokens['refresh_token'],
            'grant_type': 'refresh_token',
            'client_secret': self.client_secret
        }, headers=headers
                                   ).json()

        if self.tokens['access_token'] != new_tokens['access_token']:
            self.tokens['access_token'] = new_tokens['access_token']
            logger.info("Access token is successfully renewed!")
            try:
                self.tokens['refresh_token'] = new_tokens['refresh_token']
            except:
                logger.warning("Keeping old refresh token!")
            self.__save_tokens_to_file()
        else:
            logger.warning("New access token is same as old !")

    def __perform_login(self):
        if self.__get_tokens_from_file():
            logger.info("Successfully gathered tokens from file!")
        elif self.check_tokens():
            logger.info("Tokens already exists!")
        else:
            logger.info("Please go to this URL: " +
                        self.create_authorization_url())
            logger.info("Insert URL where you been redirected:")
            redirection_url = input()
            self.get_tokens(redirection_url=redirection_url)

    def upload_file(self, one_drive_dir="", local_dir=".", file_name="bck"):
        if one_drive_dir[0] == '/':
            one_drive_dir = one_drive_dir[1:]
        if self.tokens is None:
            self.__perform_login()
        else:
            self.check_tokens()
            try:
                upload_url = self.__get_upload_url(
                    dir=one_drive_dir, file_name=file_name)
                logger.debug("Upload URL: " + str(upload_url))
                self.__upload_to_one_drive(
                    url=upload_url,
                    file=(local_dir + '/' + file_name)
                )
            except Exception as e:
                logger.error(
                    "Error while performing upload to OneDrive: " + str(e))

    def __get_upload_url(self, dir, file_name):

        response = self.__get_upload_url_request(dir=dir, file_name=file_name)

        if 200 <= response.status_code < 300:
            logger.debug(response.json())
            return response.json()['uploadUrl']
        elif response.status_code == 401:
            logger.warning("Access token is expired, renewing it! ")
            self.renew_tokens()
            return self.__get_upload_url_request(dir, file_name).json()['uploadUrl']
        else:
            logger.error("Error while generating upload URL!")
            return None

    def __get_upload_url_request(self, dir, file_name):
        request_body = {
            "item": {
                "description": "Uploaded file from backup system.",
                "name": file_name
            }
        }
        headers = {
            'Authorization': 'Bearer ' + self.tokens['access_token'],
        }

        get_upload_session_url = self.__GRAPH_API_URL + f'/me/drive/items/root:/' + \
                                 dir + '/' + file_name + ':/createUploadSession'
        logger.debug("URL for getting upload session: " + get_upload_session_url)
        response = None
        try:
            response = requests.post(
                get_upload_session_url,
                headers=headers,
                json=request_body
            )
            if 200 <= response.status_code < 300:
                logger.debug(response.json())
                return response
            elif response.status_code == 401:
                logger.warning("Access token is expired, renewing it! ")
                self.renew_tokens()
                return self.__get_upload_url_request(dir, file_name).json()['uploadUrl']
            else:
                logger.error("Error while generating upload URL!")
                return None
        except Exception as e:
            logger.error(str(e))
            logger.debug("Response code: " + str(response.status_code))

    def __upload_to_one_drive(self, url, file):
        f = open(file, 'rb')
        file_size = os.path.getsize(file)
        uploaded_bytes = 0
        start = timer()
        logger.info("Uploading file: " + file)
        logger.debug("File size: " + str(file_size))
        try:
            while uploaded_bytes < file_size:
                if file_size < self.__CHUNK_SIZE:
                    logger.debug("File is less than 31.25MB")
                    size_curr_request = file_size
                elif (file_size - f.tell()) < self.__CHUNK_SIZE:
                    logger.debug("Uploading last fragment ")
                    size_curr_request = file_size - f.tell()
                else:
                    size_curr_request = self.__CHUNK_SIZE
                logger.debug("Size of current fragment: " + str(size_curr_request))
                logger.debug("Current state : bytes " + str(uploaded_bytes) +
                             '-' + str(uploaded_bytes + size_curr_request - 1) + '/' + str(file_size))
                headers = {
                    'Content-Length': str(size_curr_request),
                    'Content-Range': 'bytes ' + str(uploaded_bytes) + '-'
                                     + str(uploaded_bytes + size_curr_request - 1) + '/' + str(file_size)
                }
                if ".gz" in file:
                    import gzip
                    f = gzip.open(file)
                    data = f.read(size_curr_request)
                else:
                    data = f.read(size_curr_request)

                response = requests.put(url, data=data, headers=headers)
                if response.status_code >= 300:
                    logger.error("Error while uploading file: " +
                                 str(file) + " to OneDrive!")
                    logger.error("Response code: " + str(response.status_code) +
                                 "\nResponse text: " + response.text)
                    return
                uploaded_bytes += size_curr_request
        except Exception as e:
            logger.error(str(e))
        end = timer()
        logger.info("Successfully uploaded file")
        logger.debug("Terminating upload session from OneDrive")
        response = requests.delete(url)
        if 200 <= response.status_code < 300:
            logger.debug("Session successfully terminated")
            logger.info("Time took for uploading: " +
                        str(timedelta(seconds=end - start)))
        else:
            logger.warning("Session is terminated with status code: " +
                           str(response.status_code) + "\nand content: " + response.content)

    def remove_old_files(self, file_name, one_drive_dir, encrypt, no_copies=3):
        if one_drive_dir[0] == '/':
            one_drive_dir = one_drive_dir[1:]
        file_name = file_name.strip()
        no_copies = int(no_copies)
        try:
            logger.debug("File Name for removal: " + file_name)
            logger.debug("Fetching list of files")
            list_of_files = self.__list_files_for_removal(
                file_name=file_name,
                one_drive_dir=one_drive_dir,
                encrypt=encrypt
            )
            keep_list = []
            rem_list = []
            for i in list_of_files:
                if len(keep_list) == no_copies:
                    if parser.parse(keep_list[len(keep_list) - 1]["lastModifiedDateTime"]) < \
                            parser.parse(i["lastModifiedDateTime"]):
                        rem_list.append(keep_list[len(keep_list) - 1])
                        cnt = 0
                        for j in keep_list:
                            if parser.parse(i["lastModifiedDateTime"]) > \
                                    parser.parse(j["lastModifiedDateTime"]):
                                for k in range(no_copies - 1, cnt, -1):
                                    keep_list[k] = keep_list[k - 1]
                                keep_list[cnt] = i

                                break
                            cnt += 1
                    else:
                        rem_list.append(i)
                elif len(keep_list) > 0:
                    keep_list.append(i)
                    keep_list.sort(key=lambda x: parser.parse(
                        x["lastModifiedDateTime"]), reverse=True)
                else:
                    keep_list.append(i)

            logger.info("Removing files")
            for i in rem_list:
                self.__remove_file(i)
            logger.debug("Keeping files:")
            for i in keep_list:
                logger.debug("File name: " + i['name'])
        except Exception as e:
            logger.error(str(e))

    def __list_files_for_removal(self, file_name, one_drive_dir, encrypt):
        list_of_files = []
        try:
            headers = {
                'Authorization': 'Bearer ' + self.tokens['access_token'],
            }

            get_list_url = self.__GRAPH_API_URL + f'/me/drive/items/root:/' + one_drive_dir + ':/children'
            logger.debug("URL for listing directory: " + str(get_list_url))
            response = requests.get(
                get_list_url,
                headers=headers
            )
            logger.debug(response.json())
            if 200 <= response.status_code < 300:
                for i in response.json()["value"]:
                    if file_name in str(i["name"]):
                        if str(encrypt).upper() == "TRUE":
                            if str(i["name"]).endswith(".enc"):
                                logger.debug("Find file: " + i["name"])
                                list_of_files.append(i)
                        else:
                            if not str(i["name"]).endswith(".enc"):
                                logger.debug("Find file: " + i["name"])
                                list_of_files.append(i)

            elif response.status_code == 401:
                logger.warning("Access token is expired, renewing it! ")
                self.renew_tokens()
                list_of_files = self.__list_files_for_removal(
                    file_name, one_drive_dir, encrypt)
            else:
                logger.error("Listing directories failed with status code: " +
                             str(response.status_code)
                             + " and response message: " + response.json())

        except Exception as e:
            logger.error(str(e))

        return list_of_files

    def __remove_file(self, one_drive_element):
        try:
            headers = {
                'Authorization': 'Bearer ' + self.tokens['access_token'],
            }
            delete_url = self.__GRAPH_API_URL + f'/me/drive/items/' + one_drive_element['id']
            response = requests.delete(
                delete_url,
                headers=headers
            )
            if 200 <= response.status_code < 300:
                logger.info(
                    "File: " + one_drive_element['name'] + " is successfully removed!")
            elif response.status_code == 401:
                logger.warning("Access token is expired, renewing it! ")
                self.renew_tokens()
                self.__remove_file(one_drive_element)
            else:
                logger.error("Error wile deleting file: " +
                             one_drive_element['name'] + " , with status code: " +
                             str(response.status_code))
        except Exception as e:
            logger.error(str(e))

    def keep_only_oldest_and_newest(self, file_name, one_drive_dir, encrypt):
        if one_drive_dir[0] == '/':
            one_drive_dir = one_drive_dir[1:]
        file_name = file_name.strip()
        try:
            logger.debug("File Name for removal: " + file_name)
            logger.debug("Fetching list of files")
            list_of_files = self.__list_files_for_removal(
                file_name=file_name,
                one_drive_dir=one_drive_dir,
                encrypt=encrypt
            )
            newest = None
            oldest = None
            rem_list = []
            for i in list_of_files:
                if i["name"].endswith(".snap") or i["name"].endswith(".snap.bak"):
                    pass
                else:
                    if newest is not None and oldest is not None:
                        if newest["lastModifiedDateTime"] > i["lastModifiedDateTime"]:
                            if oldest["lastModifiedDateTime"] < i["lastModifiedDateTime"]:
                                rem_list.append(i)
                            else:
                                if oldest != newest:
                                    rem_list.append(oldest)
                                oldest = i
                        else:
                            if oldest == newest:
                                oldest = i
                            else:
                                rem_list.append(newest)
                                newest = i
                    else:
                        newest = i
                        oldest = i

            logger.debug("Newest file: " + newest["name"] + " Last Modified Date Time: " +
                         newest["lastModifiedDateTime"])
            logger.debug("Oldest file: " + oldest["name"] + " Last Modified Date Time: " +
                         oldest["lastModifiedDateTime"])
            logger.debug("Removing list: ")
            for j in rem_list:
                self.__remove_file(j)

        except Exception as e:
            logger.error(str(e))
