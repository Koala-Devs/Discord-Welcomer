import json
import os

CONFIG_FILE = "data/guild_configs.json"

def load_configs() -> dict:
    if not os.path.exists(CONFIG_FILE):
        return {}
    with open(CONFIG_FILE, "r") as f:
        return json.load(f)

def save_configs(data: dict):
    os.makedirs("data", exist_ok=True)
    with open(CONFIG_FILE, "w") as f:
        json.dump(data, f, indent=4)

def get_guild_config(guild_id: int) -> dict:
    data = load_configs()
    return data.get(str(guild_id), {})

def set_guild_value(guild_id: int, key: str, value):
    data = load_configs()
    key_str = str(guild_id)
    if key_str not in data:
        data[key_str] = {}
    data[key_str][key] = value
    save_configs(data)

def get_guild_value(guild_id: int, key: str, default=None):
    return get_guild_config(guild_id).get(key, default)
