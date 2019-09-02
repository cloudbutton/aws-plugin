import os
import logging
import boto3
import botocore
import time
import json
from pywren_ibm_cloud.version import __version__

logger = logging.getLogger(__name__)


class ComputeBackend:
    """
    A wrap-up around AWS Boto3 Lambda API
    """

    def __init__(self, aws_lambda_config):
        self.log_level = os.getenv('PYWREN_LOG_LEVEL')
        self.name = 'aws_lambda'
        self.aws_lambda_config = aws_lambda_config
        self.package = 'pywren_v'+__version__
        self.region = aws_lambda_config['region_name']
        self.role = aws_lambda_config['role']

        self.lambda_client = self.client = boto3.client(
            'lambda',
            aws_access_key_id=aws_lambda_config.get('access_key_id'),
            aws_secret_access_key=aws_lambda_config.get('secret_access_key'),
            region_name=self.region
        )

        log_msg = 'PyWren v{} init for AWS Lambda - Region: {}'.format(__version__, self.region)
        logger.info(log_msg)
        if not self.log_level:
            print(log_msg)

    def _format_action_name(self, runtime_name, runtime_memory):
        runtime_name = (self.package+'_'+runtime_name).replace('.', '-')
        return '{}_{}MB'.format(runtime_name, runtime_memory)
    
    def _unformat_action_name(self, action_name):
        split = action_name.split('_')
        runtime_name = split[1].replace('-', '.')
        runtime_memory = int(split[2].replace('MB', ''))
        return runtime_name, runtime_memory
    
    def _check_params(self, runtime_name, memory, timeout=None):
        if timeout is not None and timeout > 900:
            logger.info('Warning: Timeout for lambda functions set to 900 s. {} is not allowed'.format(timeout))
            timeout = 900
        if memory > 3008:
            logger.info('Warning: Memory size for lambda functions set to 3008 MB. {} MB is not allowed'.format(memory))
            memory = 3008
        
        function_name = self._format_action_name(runtime_name, memory)

        if timeout is not None:
            return function_name, memory, timeout
        else:
            return function_name, memory
    
    def _get_scipy_layer_arn(self, runtime_name):
        acc_id = {
            'us-east-1' : 668099181075,
            'us-east-2' : 259788987135,
            'us-west-1' : 325793726646,
            'us-west-2' : 420165488524,
            'eu-central-1' : 292169987271,
            'eu-west-1' : 399891621064,
            'eu-west-2' : 142628438157,
            'eu-west-3' : 959311844005,
            'eu-north-1' : 642425348156
        }
        
        runtime_name = runtime_name.replace('p', 'P')
        arn = 'arn:aws:lambda:'+self.region+':'+acc_id[self.region]+':layer:AWSLambda-'+runtime_name+'-SciPy1x:2'
        return arn

    def update_runtime(self, runtime_name, code, memory=3008, timeout=900, layers=[]):

        function_name, memory, timeout = self._check_params(runtime_name, memory, timeout)        

        response = self.client.update_function_code(
            FunctionName=function_name,
            ZipFile=code,
            Publish=False
        )

        if response['ResponseMetadata']['HTTPStatusCode'] == 201:
            logger.debug("OK --> Updated function code {}".format(function_name))
        else:
            msg = 'An error occurred updating function code {}: {}'.format(function_name, response)
            raise Exception(msg)

        response = self.client.update_function_configuration(
            FunctionName=function_name,
            Role=self.role,
            Timeout=timeout,
            MemorySize=memory,
            Layers=layers
        )

        if response['ResponseMetadata']['HTTPStatusCode'] == 201:
            logger.debug("OK --> Updated function code {}".format(function_name))
        else:
            msg = 'An error occurred updating function config {}: {}'.format(function_name, response)
            raise Exception(msg)

    def create_runtime(self, runtime_name, memory=3008, code=None, timeout=900, layers=[]):
        """
        Create an AWS Lambda function
        """
        function_name, memory, timeout = self._check_params(runtime_name, memory, timeout)
        logger.debug('I am about to create a new lambda function: {}'.format(function_name))

        # Upload layer from bytes zip
        layers_arn = []
        for layer in layers:
            layer_arn = self.create_layer(
                self.package.replace('.', '-')+'_layer',
                runtime_name,
                layer)
            layers_arn.append(layer_arn)
        layers_arn.append(self._get_scipy_layer_arn(runtime_name))

        try:
            response = self.client.create_function(
                FunctionName=function_name,
                Runtime=runtime_name,
                Role=self.role,
                Handler='__main__.main',
                Code={
                    'ZipFile': code
                },
                Description=self.package,
                Timeout=timeout,
                MemorySize=memory,
                Layers=layers_arn
            )

            if response['ResponseMetadata']['HTTPStatusCode'] == 201:
                logger.debug("OK --> Created action {}".format(runtime_name))
            else:
                msg = 'An error occurred creating/updating action {}: {}'.format(runtime_name, response)
                raise Exception(msg)        
        except self.client.exceptions.ResourceConflictException:
            logger.debug('{} lambda function already exists. It will be replaced.')
            layers.extend(self.list_layers(runtime_name=runtime_name))
            self.update_runtime(runtime_name, code, memory, timeout, layers)

    def delete_runtime(self, runtime_name, memory):
        logger.debug("I am about to delete lambda function: {}".format(runtime_name))

        function_name, memory = self._check_params(runtime_name, memory)
        
        response = self.client.delete_function(
            FunctionName=function_name
        )

        if response['ResponseMetadata']['HTTPStatusCode'] == 204:
            logger.debug("OK --> Deleted function {}".format(runtime_name))
        else:
            msg = 'An error occurred creating/updating action {}: {}'.format(runtime_name, response)
            raise Exception(msg)

    def delete_all_runtimes(self):

        response = self.client.list_functions(
            MasterRegion=self.region
        )

        for runtime in response['Functions']:
            if 'pywren_v' in runtime['FunctionName']:
                runtime_name, runtime_memory = self._unformat_action_name(runtime['FunctionName'])
                self.delete_runtime(runtime_name, runtime_memory)

    def list_runtimes(self, docker_image_name='all'):
        """
        List all the runtimes deployed in the IBM CF service
        return: list of tuples [docker_image_name, memory]
        """
        runtimes = []
        response = self.client.list_functions(
            MasterRegion=self.region
        )

        for runtime in response['Functions']:
            function_name = runtime['FunctionName']
            memory = runtime['MemorySize']
            runtimes.append([function_name, memory])
        return runtimes

    def create_layer(self, layer_name, runtime_name, zipfile):
        logger.debug("I am about to create lambda layer: {}".format(layer_name))
        response = self.client.publish_layer_version(
            LayerName=layer_name,
            Description=self.package,
            Content={
                'ZipFile': zipfile
            },
            CompatibleRuntimes=[runtime_name]
        )

        if response['ResponseMetadata']['HTTPStatusCode'] == 201:
            logger.debug("OK --> Layer {} created".format(layer_name))
            return response['LayerVersionArn']
        else:
            msg = 'An error occurred creating layer {}: {}'.format(layer_name, response)
            raise Exception(msg)
    
    def delete_layer(self, layer_arn, version_number=None):
        logger.debug("I am about to delete lambda layer: {}".format(layer_arn))

        if version_number is None:
            version_number = layer_arn.split(':')[-1]

        response = self.client.delete_layer_version(
            LayerName=layer_arn,
            VersionNumber=version_number
        )

        print(response)

    def list_layers(self, runtime_name=None):
        logger.debug("I am about to list lambda layers: {}".format(runtime_name))
        response = self.client.list_layers(
            CompatibleRuntime=runtime_name
        )

        layers = []
        for layer in response['Layers']:
            layers.append(layer['LayerArn'])
        return layers

    def invoke(self, runtime_name, runtime_memory, payload, self_invoked=False):
        """
        Invoke lambda function asynchronously
        """
        exec_id = payload['executor_id']
        call_id = payload['call_id']

        function_name, memory = self._check_params(runtime_name, runtime_memory)

        start = time.time()
        try:
            response = self.client.invoke(
                FunctionName=function_name,
                InvocationType='Event',
                Payload=json.dumps(payload)
            )
        except Exception as e:
            log_msg = ('ExecutorID {} - Function {} invocation failed: {}'.format(exec_id, call_id, str(e)))
            logger.debug(log_msg)
            if self_invoked:
                return None
            return self.invoke(runtime_name, runtime_memory, payload, self_invoked=True)

        roundtrip = time.time() - start
        resp_time = format(round(roundtrip, 3), '.3f')

        if response['ResponseMetadata']['HTTPStatusCode'] == 202:
            log_msg = ('ExecutorID {} - Function {} invocation done! ({}s) - Activation ID: '
                       '{}'.format(exec_id, call_id, resp_time, response['ResponseMetadata']['RequestId']))
            logger.debug(log_msg)
            return response['ResponseMetadata']['RequestId']
        else:
            logger.debug(response)
            if response['ResponseMetadata']['HTTPStatusCode'] == 401:
                raise Exception('Unauthorized - Invalid API Key')
            elif response['ResponseMetadata']['HTTPStatusCode'] == 404:
                raise Exception('PyWren Runtime: {} not deployed'.format(runtime_name))
            elif response['ResponseMetadata']['HTTPStatusCode'] == 429:
                # Too many concurrent requests in flight
                return None
            else:
                raise Exception(response)

    def invoke_with_result(self, runtime_name, runtime_memory, payload={}):
        """
        Invoke lambda function and wait for result
        """
        function_name, memory = self._check_params(runtime_name, runtime_memory)

        response = self.client.invoke(
            FunctionName=function_name,
            Payload=json.dumps(payload)
        )

        return json.loads(response['Payload'].read())

    def get_runtime_key(self, runtime_name, runtime_memory):
        """
        Method that creates and returns the runtime key.
        Runtime keys are used to uniquely identify runtimes within the storage,
        in order to know which runtimes are installed and which not.
        """
        action_name = self._format_action_name(runtime_name, runtime_memory)
        runtime_key = os.path.join(self.name, self.region, self.region, action_name)

        return runtime_key
