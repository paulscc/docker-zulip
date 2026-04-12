#!/usr/bin/env python3
from zulip import Client
import json

# Test connection with first bot
try:
    client = Client(
        email='Kn3vSm1mJiUKEIoDZQ1IGtaCJDspkbXX-bot@localhost',
        api_key='Kn3vSm1mJiUKEIoDZQ1IGtaCJDspkbXX',
        site='http://localhost:9991'
    )
    
    # Get server settings
    result = client.get_server_settings()
    print('Connection successful!')
    
    # List streams
    streams = client.get_streams()
    print(f'Found {len(streams)} streams:')
    for stream in streams:
        print(f'- {stream["name"]} (ID: {stream["stream_id"]})')
        
except Exception as e:
    print(f'Error: {e}')
