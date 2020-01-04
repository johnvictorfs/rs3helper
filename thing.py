from mypy_extensions import TypedDict
import json

Settings = TypedDict('Settings', {'token': str})

with open('settings.json') as f:
    settings: Settings = json.load(f)
    print(settings['token'])
