import yaml
import os
from src.utils.encryption import decrypt_file
from dotenv import load_dotenv
load_dotenv()

class ConfigLoader:
    def __init__(self):
        self.config = None
        self.secrets = None
        self.config_mtime = 0
        self.secrets_mtime = 0

    def load_config(self):
        current_mtime = os.path.getmtime("config/config.yaml")
        if current_mtime > self.config_mtime:
            with open("config/config.yaml", "r") as file:
                self.config = yaml.safe_load(file)
            self.config_mtime = current_mtime
        return self.config

    def load_secrets(self):
        secrets_path = os.path.join("config", "secrets.yaml.enc")
        key = os.environ.get("SECRETS_KEY")
        if not key:
            raise ValueError("SECRETS_KEY environment variable is not set")
        key = key.encode()  # Ensure the key is in bytes
        decrypted_content = decrypt_file(secrets_path, key)
        self.secrets = yaml.safe_load(decrypted_content)
        return self.secrets