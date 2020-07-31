#
# Copyright Cloudlab URV 2020
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

import pywren_ibm_cloud
import os
import shutil


pywren_path = os.path.dirname(os.path.abspath(pywren_ibm_cloud.__file__))

storage_backends_dir = os.path.dirname(os.path.abspath(pywren_ibm_cloud.storage.__file__))
compute_backends_dir = os.path.dirname(os.path.abspath(pywren_ibm_cloud.compute.__file__))
dst_storage_backend_path = os.path.join(storage_backends_dir, 'backends', 'aws_s3')
dst_compute_backend_path = os.path.join(compute_backends_dir, 'backends', 'aws_lambda')

if os.path.isdir(dst_storage_backend_path):
    shutil.rmtree(dst_storage_backend_path)
elif os.path.isfile(dst_storage_backend_path):
    os.remove(dst_storage_backend_path)

if os.path.isdir(dst_compute_backend_path):
    shutil.rmtree(dst_compute_backend_path)
elif os.path.isfile(dst_compute_backend_path):
    os.remove(dst_compute_backend_path)

current_location = os.path.dirname(os.path.abspath(__file__))
src_storage_backend_path = os.path.join(current_location, 'aws_s3')
src_compute_backend_path = os.path.join(current_location, 'aws_lambda')

shutil.copytree(src_storage_backend_path, dst_storage_backend_path)
shutil.copytree(src_compute_backend_path, dst_compute_backend_path)

print('AWS plugin successfully installed in : {}'.format(pywren_path))
