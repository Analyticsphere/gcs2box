# gcs2box
This code will be used in a Google Cloud Function to usher files from Google Cloud Storage Bucket to a folder in Box.com

This code will run as a GCP Function to push any file 
dropped in a GCP Cloud Storage Bucket to a folder on Box.com using
a token associated with Custom Box.com app. The token is will be 
managed by GCP Secret Manager.

Pipleline Details:

- GCP Project:          nih-nci-dceg-connect-dev

- GCP CS Bucket:        analyticsReport2box

- GCP Cloud Function:   test_analytics_team_bucket

- GCP Secret:           Jake still needs Secret Manager Permissions

- Box Folder:           CONNECT_DCEG ONLY > GCP2BOX_test

- Box Folder ID:        198972272346

- Box Folder Link:      https://nih.app.box.com/folder/198972272346          

- Box App:              NCI_BOX_GCP_CONNECT4CANCER_DEV

- Box App Link:         https://nih.app.box.com/developers/console/app/1960499
