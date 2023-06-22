import configparser
def read_config(file_path):
    config = configparser.ConfigParser()
    config.read(file_path)

    log_path = config.get('Server', 'log_path')
    log_file_mask = config.get('Server', 'log_file_mask')

    return log_path, log_file_mask