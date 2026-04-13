#!/usr/bin/env python3
import json

with open('bot_config.json', 'r') as f:
    config = json.load(f)

print('CORREOS DE BOTS ACTIVOS (servidores accesibles):')
print('=' * 50)
for bot in config['bots']:
    if '127.0.0.1.nip.io' in bot['server_url'] or 'localhost:443' in bot['server_url']:
        print(f'Bot: {bot["bot_name"]}')
        print(f'Email: {bot["email"]}')
        print(f'Server: {bot["server_url"]}')
        print('-' * 30)
