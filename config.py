import toml
config_path = 'Python\Reddit Scraper\config.toml'


def load_config():
    config = toml.load(config_path)
    return config
