import os

from google.cloud import storage


def upload_blob(bucket_name, source_file_name, destination_blob_name):
    """Uploads a file to the bucket."""
    # The ID of your GCS bucket
    # bucket_name = "your-bucket-name"
    # The path to your file to upload
    # source_file_name = "local/path/to/file"
    # The ID of your GCS object
    # destination_blob_name = "storage-object-name"

    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)

    blob.upload_from_filename(source_file_name)


path = '/Users/asaflev/Desktop/imageEnhanceDebugging/floorPlanClassOneAndStudioCSV'
entries = os.listdir(path)
num_of_files_uploaded = 0
for entry in entries:
    path_of_entry = f'{path}/{entry}'
    upload_blob(bucket_name='imagerecognition-277908-vcm', source_file_name=path_of_entry,
                destination_blob_name=f'floorPlanSize/csv_created/{entry}')
    num_of_files_uploaded += 1
    if num_of_files_uploaded % 5 == 0:
        print(f'Finished uploading {num_of_files_uploaded}')



# gsutil -m cp -R ['/Users/asaflev/Desktop/imageEnhanceDebugging/floorPlanClassOneAndStudioCSV'] gs://'imagerecognition-277908-vcm/floorPlanSize/csv_created'
