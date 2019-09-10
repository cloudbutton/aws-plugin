import sys
from pywren_ibm_cloud.utils import version_str

RUNTIME_TIMEOUT_DEFAULT = 900  # Default timeout: 900 s == 15 min
RUNTIME_MEMORY_DEFAULT = 256  # Default memory: 256 MB
RUNTIME_MEMORY_MAX = 3008  # Max. memory: 3008 MB

def load_config(config_data=None):
    if 'runtime_memory' not in config_data['pywren']:
        config_data['pywren']['runtime_memory'] = RUNTIME_MEMORY_DEFAULT
    if config_data['pywren']['runtime_memory'] > RUNTIME_MEMORY_MAX:
        config_data['pywren']['runtime_memory'] = RUNTIME_MEMORY_MAX
    if config_data['pywren']['runtime_memory'] % 64 != 0:   # Adjust 64 MB memory increments restriction
        mem = config_data['pywren']['runtime_memory']
        config_data['pywren']['runtime_memory'] = (mem + (64 - (mem % 64)))
    if 'runtime_timeout' not in config_data['pywren'] or \
        config_data['pywren']['runtime_timeout'] > RUNTIME_TIMEOUT_DEFAULT:
        config_data['pywren']['runtime_timeout'] = RUNTIME_TIMEOUT_DEFAULT
    if 'runtime' not in config_data['pywren']:
        config_data['pywren']['runtime'] = 'python'+version_str(sys.version_info)

    if 'aws' not in config_data and 'aws_lambda' not in config_data:
        raise Exception("'aws' and 'aws_lambda' sections are mandatory in the configuration")
    
    # Put credential keys to 'aws_lambda' dict entry
    config_data['aws_lambda'] = {**config_data['aws_lambda'], **config_data['aws']}

    required_parameters_0 = ('access_key_id', 'secret_access_key')
    if not set(required_parameters_0) <= set(config_data['aws']):
        raise Exception("'access_key_id' and 'secret_access_key' are mandatory under 'aws' section")

    if 'execution_role' not in config_data['aws_lambda']:
        raise Exception("execution_role' are mandatory under 'aws_lambda' section")
    
    if 'region' not in config_data['aws_lambda']:
        config_data['aws_lambda']['region'] = config_data['pywren']['compute_backend_region']    