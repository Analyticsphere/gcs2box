'''
Written by:    Daniel Russ, Jake Peters
Written:       Apr 2022
Last Modified: May 2022
Description:   This cloud function uses a Custom box app service account
               to move a file to a specified Box folder when the file has 
               been put into a specified Cloud Storage bucket.
               The Box folder admin must invite the Box app service account
               as a user for the folder. 
'''

from google.cloud import secretmanager, storage
from boxsdk import JWTAuth, Client
import json
import io

# Change this one parameter to use a different box folder.
BOX_FOLDER_ID = "205507496270"

def gcs2box_on_file_creation_event(event, context):
    """Triggered by a change to a Cloud Storage bucket.
    Args:
         event (dict): Event payload.
         context (google.cloud.functions.Context): Metadata for the event.
    """
    fileObject = event
    # print(f"File object: {fileObject}")
    # print(f"Processing file: {fileObject['name']}.")

    ## get the contents of the newly created file on GCP...
    storageClient = storage.Client()
    bucket  = storageClient.bucket(fileObject['bucket'])
    blob = bucket.blob(fileObject['name'])
    contents = blob.download_as_bytes()

    ## get the service account from Box and create a client...
    boxToken = json.loads( get_box_token() )
    boxClient = get_box_client(boxToken)

    ## Move file to Box
    # Documentation: https://github.com/box/box-python-sdk/blob/main/docs/usage/files.md#upload-a-file
    # NOTE: box requires either a Stream or a file.  Since we do not have
    #       files on GCS, convert the byte-array (contents) into a stream
    #       and upload it to box.    
    stream = io.BytesIO(contents)
    # Check for "_export2box_" tag in filename before exporting
    if fileToBeExported(fileObject['name']):
        new_file = boxClient.folder(BOX_FOLDER_ID).upload_stream(stream, fileObject['name'])

def fileToBeExported(file_name):
    '''Check for "_export2box_" to prevent accidental exports of files dropped in this bucket.'''
    if "_export2box_" in file_name:
        return True
    else:
        return False

def stoken_callback(token, arg2):
  '''This function is used as a callback by the in Box's JWTAuth object. 
  It takes a token as an argument and returns it, so it basically does 
  nothing, but it is required.'''
  return token

def get_box_token(version_id="latest"):
    '''Get Secrets
    Documentation: https://github.com/box/box-python-sdk/blob/main/docs/usage/files.md#upload-a-file
    '''

    secret_id = "boxtoken" # This is the name of the Cloud Secret set up for this purpose by Daniel Russ
    PROJECT_ID = 1061430463455 # This is the project_id for the `nih-nci-dceg-connect-dev` environment
    
    # Create the Secret Manager client.
    client = secretmanager.SecretManagerServiceClient()

    # Build the resource name of the secret version.
    name = f"projects/{PROJECT_ID}/secrets/{secret_id}/versions/{version_id}"

    # Access the secret version.
    response = client.access_secret_version(name=name)

    # Return the decoded payload.
    return response.payload.data.decode('UTF-8')

def get_box_client(boxToken):
    '''Authenticate to Box.com
    Documentation: https://github.com/box/box-python-sdk/blob/main/docs/usage/authentication.md
    '''
    service_account_auth = JWTAuth(
        client_id = boxToken['boxAppSettings']['clientID'],
        client_secret = boxToken['boxAppSettings']['clientSecret'],
        enterprise_id = boxToken['enterpriseID'],
        jwt_key_id = boxToken['boxAppSettings']['appAuth']['publicKeyID'],
        rsa_private_key_data = boxToken['boxAppSettings']['appAuth']['privateKey'],
        rsa_private_key_passphrase = boxToken['boxAppSettings']['appAuth']['passphrase'],
        store_tokens=stoken_callback)
    # print(' ==================== THE SERVICE ACCOUNT AUTH IS ', service_account_auth)
    access_token = service_account_auth.authenticate_instance()
    service_account_client = Client(service_account_auth)
    return service_account_client