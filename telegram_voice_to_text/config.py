from pathlib import Path


_config = {}

def get(key):
    global _config
    if not _config:
        config_file = Path(__file__).resolve().parents[1] / '.env'
        if not config_file.exists():
            raise RuntimeError('File {} not found'.format(config_file))
        for line in config_file.read_text().splitlines():
            key, value = line.split('=', 1)
            _config[key] = value
    value = _config.get(key)
    if value is None:
        raise RuntimeError('Missing configuration key {}'.format(key))
    return value
