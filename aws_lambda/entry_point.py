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

import logging
import os
from pywren_ibm_cloud.version import __version__
from pywren_ibm_cloud.config import cloud_logging_config
from pywren_ibm_cloud.function import function_handler
from pywren_ibm_cloud.function import function_invoker

cloud_logging_config(logging.INFO)
logger = logging.getLogger('__main__')


def main(event, context):
    logger.info("Starting AWS Lambda Function execution")
    os.environ['__PW_ACTIVATION_ID'] = context.aws_request_id
    if 'remote_invoker' in event:
        logger.info("PyWren v{} - Starting invoker".format(__version__))
        function_invoker(event)
    else:
        logger.info("PyWren v{} - Starting execution".format(__version__))
        function_handler(event)

    return {"Execution": "Finished"}

