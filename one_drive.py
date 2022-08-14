from datetime import timedelta
import os
from urllib.parse import urlparse
from urllib.parse import parse_qs
import requests
import pathlib
import json
import logging
from timeit import default_timer as timer

logger = logging.getLogger("backup_logger")

class OneDrive:
    
    def __init__(
        self,
        clientSecret,
        clientID,
        scopes,
        tokens=None,
        tokensFile='./tokens.json',
        folderId=None,
        tenantId=None
        ):
        self.clientSecret = clientSecret
        self.clientID = clientID
        self.scopes = scopes
        self.__GRAPH_API_URL = "https://graph.microsoft.com/v1.0"
        self.__LOGIN_BASE_URL = "https://login.microsoftonline.com"
        self.__OAUTH2_BASE_URL = self.__LOGIN_BASE_URL + "/"+tenantId+"/oauth2/v2.0"
        self.__AUTHORIZE_BASE_URL = self.__OAUTH2_BASE_URL + "/authorize"
        self.__TOKENS_BASE_URL = self.__OAUTH2_BASE_URL + "/token"
        self.__CHUNK_SIZE = 32768000  # velicina fragmenta trab da bude umnozak 320KB, trenutno je 31.25MB
        self.tokens = tokens
        self.tokensFile = tokensFile
        self.folderId = folderId
        
        self.__PerformLogin()
        
    def __GetTokensFromFile(self):
        if pathlib.Path(self.tokensFile).is_file() :
            try:
                logger.debug("Opening file: "+self.tokensFile)
                with open(self.tokensFile,'r') as f:
                    content = f.read()
                    tokens = json.loads(content)
                    logger.debug("Reading token from file: "+ str(tokens))
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
        authorization_url=authorization_url[:-1]
        authorization_url+='+offline_access+openid+profile'  
        logger.debug("Created authorization URL: "+ authorization_url.replace(' ','%20'))
        return authorization_url.replace(' ','%20')
    
    def CheckTokens(self):
        if self.tokens != None:
            if self.tokens['access_token'] != None:
                logger.debug('Access token exists')
                if self.tokens['refresh_token'] != None:
                    logger.debug('Refresh token exists')
                return True
        return False


    def GetTokens(self,redirectionUrl):
        code = parse_qs(urlparse(redirectionUrl).query)['code'][0]
        headers = {
            'Content-Type' : 'application/x-www-form-urlencoded'
        }
        try:
            scope_post = ''
            for scope in self.scopes: 
                if scope != "":
                    scope_post += scope + ' '  
            scope_post=scope_post[:-1]
            self.tokens = requests.post(url=self.__TOKENS_BASE_URL, data={
                    'client_id' : self.clientID,
                    'scope' : scope_post,
                    'code' : code,
                    'grant_type' : 'authorization_code',
                    'client_secret' : self.clientSecret
                }, headers=headers
            ).json()
            self.__SaveTokensToFile()
        except Exception as e:
            logger.error("Error while getting tokens: "+str(e))
        
    def __SaveTokensToFile(self):
        try:
            with open(self.tokensFile,'w') as f:
                logger.debug("Opening file: "+self.tokensFile)
                f.write(json.dumps(self.tokens))
                logger.debug("Tokens are succesfully writed to a file")
                f.close()
        except Exception as e:
            logger.error("Error while writing tokens to a file "+str(e))
    
    def RenewTokens(self):
        headers = {
            'Content-Type' : 'application/x-www-form-urlencoded'
        }

        new_tokens = requests.post(url=self.__TOKENS_BASE_URL, data={
                'client_id' : self.clientID,
                'scope' : self.scopes,
                'refresh_token' : self.tokens['refresh_token'],
                'grant_type' : 'refresh_token',
                'client_secret' : self.clientSecret
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
            
    def __PerformLogin(self):
        if self.__GetTokensFromFile():
            logger.info("Successfully gathered tokens from file!")
        elif self.CheckTokens():
            logger.info("Tokens already exists!")
        else:
            logger.info("Please go to this URL: "+self.CreateAuthorizationUrl())
            logger.info("Insert URL where you been redirected:")
            redirectionUrl = input()
            self.GetTokens(redirectionUrl=redirectionUrl)
            
            
    def UploadFile(self,oneDriveDir="",localDir=".",fileName="bck"):
        if self.tokens == None:
            self.__PerformLogin()
        else:
            try:
                self.__UploadToOneDrive(
                    url=self.__GetUploadUrl(dir=oneDriveDir,fileName=fileName),
                    file=(localDir+'/'+fileName)
                )
            except Exception as e:
                logger.error("Error while performing upload to OneDrive: "+str(e))
    
    def __GetUploadUrl(self,dir,fileName):
        request_body = {
            "item": {
                "description": "Uploaded file from backup system.",
                "name": fileName
            }
        }
        headers = {
            'Authorization': 'Bearer '+self.tokens['access_token'],
        }
        
        getUploadSessionUrl = self.__GRAPH_API_URL + f'/me/drive/items/root:/'+ \
        dir + '/'+ fileName+':/createUploadSession'
        response = requests.post(
            getUploadSessionUrl,
            headers=headers,
            json=request_body
        )
        logger.debug(response)
        if response.status_code >= 200 and response.status_code < 300:
            return response.json()['uploadUrl']
        elif response.status_code == 401:
            logger.warning("Access token is expired, renewing it! ")
            self.RenewTokens()
            self.__GetUploadUrl(dir,fileName)
        else:
            logger.error("Error while generating upload URL!")
            logger.error("URL for getting upload session: "+getUploadSessionUrl)
            return None
            
    def __UploadToOneDrive(self,url,file):
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
                logger.debug("Current state : bytes "+str(uploadedBytes)+'-'+str(uploadedBytes+sizeCurrRequest-1)+'/'+str(fileSize))
                headers = {
                    'Content-Length': str(sizeCurrRequest),
                    'Content-Range': 'bytes '+str(uploadedBytes)+'-'+str(uploadedBytes+sizeCurrRequest-1)+'/'+str(fileSize)
                }
                data = f.read(sizeCurrRequest)
                response = requests.put(url,data=data,headers=headers)
                if response.status_code >= 300:
                    logger.error("Error while uploading file: "+str(file)+" to OneDrive!")
                    logger.error("Response code: "+response.status_code+"\nResponse text: "+response.text)
                    return
                uploadedBytes+=sizeCurrRequest
        except Exception as e:
            logger.error(str(e))
        end = timer()
        logger.info("Successfully uploadde file")
        logger.debug("Terminating upload session from OneDrive")
        response = requests.delete(url)
        logger.debug("Session successfuly terminated")
        logger.info("Time took for uploading: " +
                str(timedelta(seconds=end - start)))
            