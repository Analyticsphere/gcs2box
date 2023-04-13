"""
This function will run as a GCP Function to push any file 
dropped in a GCP Cloud Storage Bucket to a folder on Box.com using
a token associated with Custom Box.com app. The token is will be 
managed by GCP Secret Manager.

Pipleline Details:

GCP Project:          nih-nci-dceg-connect-dev
GCP CS Bucket:        analyticsReport2box
GCP Cloud Function:   test_analytics_team_bucket
GCP Secret:           Jake still needs Secret Manager Permissions
Box Folder:           CONNECT_DCEG ONLY > GCP2BOX_test
Box Folder ID:        198972272346
Box Folder Link:      https://nih.app.box.com/folder/198972272346                 
Box App:              NCI_BOX_GCP_CONNECT4CANCER_DEV
Box App Link:         https://nih.app.box.com/developers/console/app/1960499
"""

def gcs2box_on_file_creation_event(event, context):
    """Triggered by a change to a Cloud Storage bucket.
    Args:
         event (dict): Event payload.
         context (google.cloud.functions.Context): Metadata for the event.
    """
    file = event
    print(f"Processing file: {file['name']}.")

    
    ### Get Secrets
    # Documentation: https://github.com/box/box-python-sdk/blob/main/docs/usage/files.md#upload-a-file
    # Import the Secret Manager client library.
    from google.cloud import secretmanager

    # GCP project in which to store secrets in Secret Manager.
    project_id = "nih-nci-dceg-connect-dev"

    # ID of the secret to create.
    secret_id = "YOUR_SECRET_ID"

    # Create the Secret Manager client.
    client = secretmanager.SecretManagerServiceClient()

    # Build the parent name from the project.
    parent = f"projects/{project_id}"

    # Create the parent secret.
    secret = client.create_secret(
        request={
            "parent": parent,
            "secret_id": secret_id,
            "secret": {"replication": {"automatic": {}}},
          }
    )

    # Add the secret version.
    version = client.add_secret_version(
        request={"parent": secret.name, "payload": {"data": b"hello world!"}}
    )

    # Access the secret version.
    response = client.access_secret_version(request={"name": version.name})

    # Print the secret payload.
    #
    # WARNING: Do not print the secret in a production environment - this
    # snippet is showing how to access the secret material.
    payload = response.payload.data.decode("UTF-8")
    # print("Plaintext: {}".format(payload))



    ### Authenticate to Box.com using JWT
    # Documentation: https://github.com/box/box-python-sdk/blob/main/docs/usage/authentication.md
    from boxsdk import JWTAuth, Client

    auth = JWTAuth(
        client_id='YOUR_CLIENT_ID',
        client_secret='YOUR_CLIENT_SECRET',
        enterprise_id='YOUR_ENTERPRISE_ID',
        jwt_key_id='YOUR_JWT_KEY_ID',
        rsa_private_key_file_sys_path='CERT.PEM',
        rsa_private_key_passphrase='PASSPHRASE',
        store_tokens=your_store_tokens_callback_method, # 
    )

    access_token = auth.authenticate_instance()

    client = Client(auth)
    

    ### Move file to Box
    # Documentation: https://github.com/box/box-python-sdk/blob/main/docs/usage/files.md#upload-a-file
    folder_id = '22222' # Replace with your folder_id
    # new_file = client.folder(folder_id).upload('/home/me/document.pdf')
    new_file = client.folder(folder_id).upload(file)
    print(f'File "{new_file.name}" uploaded to Box with file ID {new_file.id}')