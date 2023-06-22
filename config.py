import configparser

class ConfigError(Exception):
    pass

def read_config(file_path):
    try:
        config = configparser.ConfigParser()
        config.read(file_path)

        log_path = config.get('Server', 'log_path')
        log_file_mask = config.get('Server', 'log_file_mask')

        return log_path, log_file_mask
    except configparser.Error as e:
        raise ConfigError(f"Ошибка при чтении файла конфигурации: {e}")
    except KeyError as e:
        raise ConfigError(f"Отсутствует обязательный параметр: {e}")
    except Exception as e:
        raise ConfigError(f"В приложении произошла неизвестная ошибка: {e}")
