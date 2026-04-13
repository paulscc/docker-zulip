from flask import Flask, render_template, jsonify
from kafka import KafkaConsumer
import json
import time
import threading
from collections import deque

app = Flask(__name__)

# Global message storage
summaries_messages = deque(maxlen=100)
unread_messages = deque(maxlen=100)

def kafka_consumer_thread():
    """Background thread to consume Kafka messages"""
    print("Starting Kafka consumer thread...")
    
    # Create consumer for both topics
    consumer = KafkaConsumer(
        'zulip-summaries',
        'zulip-unread-messages',
        bootstrap_servers=['localhost:9092'],
        value_deserializer=lambda x: json.loads(x.decode('utf-8')),
        auto_offset_reset='earliest',
        enable_auto_commit=True,
        group_id='flask_web_working'
    )
    
    print("Kafka consumer connected, starting to consume messages...")
    
    try:
        for message in consumer:
            message_data = {
                'timestamp': time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(message.timestamp / 1000)),
                'content': message.value,
                'topic': message.topic,
                'partition': message.partition,
                'offset': message.offset
            }
            
            if message.topic == 'zulip-summaries':
                summaries_messages.append(message_data)
                print(f"Added summary message. Total summaries: {len(summaries_messages)}")
            elif message.topic == 'zulip-unread-messages':
                unread_messages.append(message_data)
                print(f"Added unread message. Total unread: {len(unread_messages)}")
                
    except Exception as e:
        print(f"Error in Kafka consumer thread: {e}")
    finally:
        consumer.close()

# Start consumer thread
consumer_thread = threading.Thread(target=kafka_consumer_thread, daemon=True)
consumer_thread.start()

@app.route('/')
def index():
    """Main page to display messages"""
    return render_template('index.html')

@app.route('/api/summaries')
def get_summaries():
    """API endpoint to get summary messages"""
    messages = list(summaries_messages)
    print(f"API /api/summaries called. Returning {len(messages)} messages")
    return jsonify(messages)

@app.route('/api/unread')
def get_unread():
    """API endpoint to get unread messages"""
    messages = list(unread_messages)
    print(f"API /api/unread called. Returning {len(messages)} messages")
    return jsonify(messages)

@app.route('/api/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'kafka_connected': True,
        'total_summaries': len(summaries_messages),
        'total_unread': len(unread_messages)
    })

if __name__ == '__main__':
    print("Starting Flask app with background Kafka consumer...")
    print("Waiting a moment for consumer to connect...")
    time.sleep(3)  # Give consumer time to start
    app.run(host='0.0.0.0', port=5000, use_reloader=False)
