import cloudbutton
import os
import shutil

base_path = os.path.dirname(cloudbutton.__file__)
source_path = os.path.dirname(__file__)

aws_functions_backend_path = os.path.join(os.path.join(base_path, 'engine', 'backends', 'compute'), 'aws_lambda')
aws_storage_backend_path = os.path.join(os.path.join(base_path, 'engine', 'backends', 'storage'), 'aws_s3')

try:
    if os.path.exists(aws_functions_backend_path) and os.path.isfile(aws_functions_backend_path):
        os.remove(aws_functions_backend_path)
    if os.path.exists(aws_storage_backend_path) and os.path.isfile(aws_storage_backend_path):
        os.remove(aws_storage_backend_path)

    if os.path.exists(aws_functions_backend_path) and os.path.isdir(aws_functions_backend_path):
        shutil.rmtree(aws_functions_backend_path)
    if os.path.exists(aws_storage_backend_path) and os.path.isdir(aws_storage_backend_path):
        shutil.rmtree(aws_storage_backend_path)

    if not os.path.exists(aws_functions_backend_path):
        shutil.copytree(os.path.join(source_path, 'compute_backend'), aws_functions_backend_path)
    if not os.path.exists(aws_storage_backend_path):
        shutil.copytree(os.path.join(source_path, 'storage_backend'), aws_storage_backend_path)

    print('Done')
except Exception as e:
    print('Installation failed: {}'.format(e))
