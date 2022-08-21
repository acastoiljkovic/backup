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
        clientSecret,
        clientID,
        scopes,
        tokens=None,
        tokensFile='./tokens.json',
        tenantId="common"
    ):
        """This is the class to work with OneDrive. It consists of several parts:
            generating and refreshing access token, uploading files to OneDrive,
            removing old files from OneDrive

        Args:
            clientSecret (string): Client secret gained form Microsoft applicaiton
            clientID (string): Client ID gained from Microsoft application
            scopes (array): Array of Microsoft scopes ie. ['User.Read']
            tokens (json, optional): JSON object that contains access and refres tokens. Defaults to None.
            tokensFile (str, optional): File where JSON tokes will be stored. Defaults to './tokens.json'.
            tenantId (string, optional): Micriostf Tenant ID where your application is beeing deployd.
                                         If you are using personal account backup system will use default "common".
        """
        self.clientSecret = clientSecret
        self.clientID = clientID
        self.scopes = scopes
        self.__GRAPH_API_URL = "https://graph.microsoft.com/v1.0"
        self.__LOGIN_BASE_URL = "https://login.microsoftonline.com"
        self.__OAUTH2_BASE_URL = self.__LOGIN_BASE_URL + "/"+tenantId+"/oauth2/v2.0"
        self.__AUTHORIZE_BASE_URL = self.__OAUTH2_BASE_URL + "/authorize"
        self.__TOKENS_BASE_URL = self.__OAUTH2_BASE_URL + "/token"
        # velicina fragmenta trab da bude umnozak 320KB, trenutno je 31.25MB
        self.__CHUNK_SIZE = 32768000
        self.tokens = tokens
        self.tokensFile = tokensFile

        self.__PerformLogin()

    def __GetTokensFromFile(self):
        if pathlib.Path(self.tokensFile).is_file():
            try:
                logger.debug("Opening file: "+self.tokensFile)
                with open(self.tokensFile, 'r') as f:
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
            logger.debug("File: "+self.tokensFile+" doesn't exists !")
            self.tokens = None
            return False

    def CreateAuthorizationUrl(self):
        authorization_url = (
            self.__AUTHORIZE_BASE_URL +
            '?client_id=' +
            self.clientID +
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

    def CheckTokens(self):
        if self.tokens != None:
            if self.tokens['access_token'] != None:
                logger.debug('Access token exists')
                if self.tokens['refresh_token'] != None:
                    logger.debug('Refresh token exists')
                return True
        return False

    def GetTokens(self, redirectionUrl):
        code = parse_qs(urlparse(redirectionUrl).query)['code'][0]
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
                'client_id': self.clientID,
                'scope': scope_post,
                'code': code,
                'grant_type': 'authorization_code',
                'client_secret': self.clientSecret
            }, headers=headers
            ).json()
            self.__SaveTokensToFile()
        except Exception as e:
            logger.error("Error while getting tokens: "+str(e))

    def __SaveTokensToFile(self):
        try:
            with open(self.tokensFile, 'w') as f:
                logger.debug("Opening file: "+self.tokensFile)
                f.write(json.dumps(self.tokens))
                logger.debug("Tokens are succesfully writed to a file")
                f.close()
        except Exception as e:
            logger.error("Error while writing tokens to a file "+str(e))

    def RenewTokens(self):
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded'
        }

        new_tokens = requests.post(url=self.__TOKENS_BASE_URL, data={
            'client_id': self.clientID,
            'scope': self.scopes,
            'refresh_token': self.tokens['refresh_token'],
            'grant_type': 'refresh_token',
            'client_secret': self.clientSecret
        }, headers=headers
        ).json()

        if self.tokens['access_token'] != new_tokens['access_token']:
            self.tokens['access_token'] = new_tokens['access_token']
            logger.info("Access token is successfully renewed!")
            try:
                self.tokens['refresh_token'] = new_tokens['refresh_token']
            except Exception as e:
                logger.warning("Keeping old refresh token!")
            self.__SaveTokensToFile()
        else:
            logger.warning("New access token is same as old !")

    def __PerformLogin(self):
        if self.__GetTokensFromFile():
            logger.info("Successfully gathered tokens from file!")
        elif self.CheckTokens():
            logger.info("Tokens already exists!")
        else:
            logger.info("Please go to this URL: " +
                        self.CreateAuthorizationUrl())
            logger.info("Insert URL where you been redirected:")
            redirectionUrl = input()
            self.GetTokens(redirectionUrl=redirectionUrl)

    def UploadFile(self, oneDriveDir="", localDir=".", fileName="bck"):
        if oneDriveDir[0] == '/':
            oneDriveDir = oneDriveDir[1:]
        if self.tokens == None:
            self.__PerformLogin()
        else:
            try:
                uploadUrl = self.__GetUploadUrl(
                    dir=oneDriveDir, fileName=fileName)
                logger.debug("Upload URL: "+str(uploadUrl))
                self.__UploadToOneDrive(
                    url=uploadUrl,
                    file=(localDir+'/'+fileName)
                )
            except Exception as e:
                logger.error(
                    "Error while performing upload to OneDrive: "+str(e))

    def __GetUploadUrl(self, dir, fileName):

        response = self.__GetUploadUrlRequest(dir=dir, fileName=fileName)

        if response.status_code >= 200 and response.status_code < 300:
            logger.debug(response.json())
            return response.json()['uploadUrl']
        elif response.status_code == 401:
            logger.warning("Access token is expired, renewing it! ")
            self.RenewTokens()
            return self.__GetUploadUrlRequest(dir, fileName).json()['uploadUrl']
        else:
            logger.error("Error while generating upload URL!")
            return None

    def __GetUploadUrlRequest(self, dir, fileName):
        request_body = {
            "item": {
                "description": "Uploaded file from backup system.",
                "name": fileName
            }
        }
        headers = {
            'Authorization': 'Bearer '+self.tokens['access_token'],
        }

        getUploadSessionUrl = self.__GRAPH_API_URL + f'/me/drive/items/root:/' + \
            dir + '/' + fileName+':/createUploadSession'
        logger.debug("URL for getting upload session: "+getUploadSessionUrl)
        try:
            response = requests.post(
                getUploadSessionUrl,
                headers=headers,
                json=request_body
            )
            if response.status_code >= 200 and response.status_code < 300:
                logger.debug(response.json())
                return response
            elif response.status_code == 401:
                logger.warning("Access token is expired, renewing it! ")
                self.RenewTokens()
                return self.__GetUploadUrlRequest(dir, fileName).json()['uploadUrl']
            else:
                logger.error("Error while generating upload URL!")
                return None
        except Exception as e:
            logger.error(str(e))
            logger.debug("Response code: "+response.status_code)

    def __UploadToOneDrive(self, url, file):
        f = open(file)
        fileSize = os.path.getsize(file)
        uploadedBytes = 0
        start = timer()
        logger.info("Uploading file: "+file)
        logger.debug("File size: "+str(fileSize))
        try:
            while uploadedBytes < fileSize:
                if fileSize < self.__CHUNK_SIZE:
                    logger.debug("File is less than 31.25MB")
                    sizeCurrRequest = fileSize
                elif (fileSize-f.tell()) < self.__CHUNK_SIZE:
                    logger.debug("Uploading last fragment ")
                    sizeCurrRequest = fileSize - f.tell()
                else:
                    sizeCurrRequest = self.__CHUNK_SIZE
                logger.debug("Size of current fragment: "+str(sizeCurrRequest))
                logger.debug("Current state : bytes "+str(uploadedBytes) +
                             '-'+str(uploadedBytes+sizeCurrRequest-1)+'/'+str(fileSize))
                headers = {
                    'Content-Length': str(sizeCurrRequest),
                    'Content-Range': 'bytes '+str(uploadedBytes)+'-'
                    + str(uploadedBytes+sizeCurrRequest-1)+'/'+str(fileSize)
                }
                if ".gz" in file:
                    import gzip
                    f = gzip.open(file)
                    data = f.read(sizeCurrRequest)
                else:
                    data = f.read(sizeCurrRequest)

                response = requests.put(url, data=data, headers=headers)
                if response.status_code >= 300:
                    logger.error("Error while uploading file: " +
                                 str(file)+" to OneDrive!")
                    logger.error("Response code: "+response.status_code +
                                 "\nResponse text: "+response.text)
                    return
                uploadedBytes += sizeCurrRequest
        except Exception as e:
            logger.error(str(e))
        end = timer()
        logger.info("Successfully uploadde file")
        logger.debug("Terminating upload session from OneDrive")
        response = requests.delete(url)
        logger.debug("Session successfuly terminated")
        logger.info("Time took for uploading: " +
                    str(timedelta(seconds=end - start)))

    def RemoveOldFiles(self, fileName, oneDriveDir, encrypt, noCopies=3):
        if oneDriveDir[0] == '/':
            oneDriveDir = oneDriveDir[1:]
        fileName = fileName.strip()
        noCopies = int(noCopies)
        try:
            logger.debug("File Name for removal: "+fileName)
            logger.debug("Fetching list of files")
            list_of_files = self.__ListFilesForRemoval(
                fileName=fileName,
                oneDriveDir=oneDriveDir,
                encrypt=encrypt
            )
            keep_list = []
            rem_list = []
            for i in list_of_files:
                if len(keep_list) == noCopies:
                    if parser.parse(keep_list[len(keep_list)-1]["lastModifiedDateTime"]) < \
                            parser.parse(i["lastModifiedDateTime"]):
                        rem_list.append(keep_list[len(keep_list)-1])
                        cnt = 0
                        for j in keep_list:
                            if parser.parse(i["lastModifiedDateTime"]) > \
                                    parser.parse(j["lastModifiedDateTime"]):
                                for k in range(noCopies-1, cnt, -1):
                                    keep_list[k] = keep_list[k-1]
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

            logger.info("Removing files:")
            for i in rem_list:
                self.__RemoveFile(i)
            logger.debug("Keeping files:")
            for i in keep_list:
                logger.debug("File name: "+i['name'])
        except Exception as e:
            logger.error(str(e))

    def __ListFilesForRemoval(self, fileName, oneDriveDir, encrypt):
        list_of_files = []
        try:
            headers = {
                'Authorization': 'Bearer '+self.tokens['access_token'],
            }

            getListUrl = self.__GRAPH_API_URL + f'/me/drive/items/root:/' + \
                oneDriveDir + ':/children'
            logger.debug("URL for listing directory: "+str(getListUrl))
            response = requests.get(
                getListUrl,
                headers=headers
            )
            logger.debug(response.json())
            if response.status_code >= 200 and response.status_code < 300:
                for i in response.json()["value"]:
                    if fileName in str(i["name"]):
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
                self.RenewTokens()
                list_of_files = self.__ListFilesForRemoval(
                    fileName, oneDriveDir, encrypt)
            else:
                logger.error("Listing directories failed with status code: " +
                             str(response.status_code)
                             + " and response message: " + response.json())

        except Exception as e:
            logger.error(str(e))

        return list_of_files

    def __RemoveFile(self, oneDriveElement):
        try:
            headers = {
                'Authorization': 'Bearer '+self.tokens['access_token'],
            }
            deleteUrl = self.__GRAPH_API_URL + \
                f'/me/drive/items/' + oneDriveElement['id']
            logger.debug("URL for deleting file: "+deleteUrl)
            response = requests.delete(
                deleteUrl,
                headers=headers
            )
            if response.status_code >= 200 and response.status_code < 300:
                logger.info(
                    "File: "+oneDriveElement['name']+" is successfully removed!")
            elif response.status_code == 401:
                logger.warning("Access token is expired, renewing it! ")
                self.RenewTokens()
                self.__RemoveFile(oneDriveElement)
            else:
                logger.error("Error wile deleting file: " +
                             oneDriveElement['name']+" , with statsu code: " +
                             str(response.status_code))
        except Exception as e:
            logger.error(str(e))

    def KeppOnlyNewestAndOldest(self, fileName, oneDriveDir, encrypt):
        if oneDriveDir[0] == '/':
            oneDriveDir = oneDriveDir[1:]
        fileName = fileName.strip()
        try:
            logger.debug("File Name for removal: "+fileName)
            logger.debug("Fetching list of files")
            list_of_files = self.__ListFilesForRemoval(
                fileName=fileName,
                oneDriveDir=oneDriveDir,
                encrypt=encrypt
            )
            newest = None
            oldest = None
            rem_list = []
            for i in list_of_files:
                if i["name"].endswith(".snap"):
                    pass
                else:
                    if newest != None and oldest != None:
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

            logger.debug("Newest file: "+newest["name"]+" Last Modified Date Time: " +
                         newest["lastModifiedDateTime"])
            logger.debug("Oldest file: "+oldest["name"]+" Last Modified Date Time: " +
                         oldest["lastModifiedDateTime"])
            logger.debug("Removing list: ")
            for j in rem_list:
                logger.debug("File name: "+j["name"]+" Last Modified Date Time: " +
                         j["lastModifiedDateTime"])

        except Exception as e:
            logger.error(str(e))
