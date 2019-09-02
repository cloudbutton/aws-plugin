import sys
from pywren_ibm_cloud.utils import version_str

RUNTIME_TIMEOUT_DEFAULT = 900  # Default timeout: 900 s == 15 min
RUNTIME_MEMORY_DEFAULT = 1024  # Default memory: 1024 MB

def load_config(config_data=None):
    if 'runtime_memory' not in config_data['pywren']:
        config_data['pywren']['runtime_memory'] = RUNTIME_MEMORY_DEFAULT
    if 'runtime_timeout' not in config_data['pywren']:
        config_data['pywren']['runtime_timeout'] = RUNTIME_TIMEOUT_DEFAULT
    if 'runtime' not in config_data['pywren']:
        config_data['pywren']['runtime'] = 'python'+version_str(sys.version_info)

    if 'aws' not in config_data and 'aws_lambda' not in config_data:
        raise Exception("'aws' and 'aws_lambda' sections are mandatory in the configuration")

    required_parameters_0 = ('access_key_id', 'secret_access_key')
    if not set(required_parameters_0) <= set(config_data['aws']):
        raise Exception("'access_key_id' and 'secret_access_key' are mandatory under 'aws' section")

    required_parameters_1 = ('region_name', 'execution_role')
    if not set(required_parameters_1) <= set(config_data['aws']):
        raise Exception("'region_name' and 'execution_role' are mandatory under 'aws_lambda' section")
    