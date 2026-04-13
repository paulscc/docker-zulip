from flask import Flask, render_template, jsonify
from kafka import KafkaConsumer
import json
import time
from collections import deque

app = Flask(__name__)

# Kafka configuration
KAFKA_BOOTSTRAP_SERVERS = ['localhost:9092']
SUMMARIES_TOPIC = 'zulip-summaries'
UNREAD_TOPIC = 'zulip-unread-messages'

def get_messages_from_topic(topic_name, max_messages=100):
    """Get messages from a specific Kafka topic"""
    try:
        consumer = KafkaConsumer(
            topic_name,
            bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
            value_deserializer=lambda x: json.loads(x.decode('utf-8')),
            auto_offset_reset='earliest',
            consumer_timeout_ms=5000
        )
        
        messages = []
        for message in consumer:
            message_data = {
                'timestamp': time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(message.timestamp / 1000)),
                'content': message.value,
                'topic': message.topic,
                'partition': message.partition,
                'offset': message.offset
            }
            messages.append(message_data)
            
            # Limit to max_messages
            if len(messages) >= max_messages:
                break
        
        consumer.close()
        print(f"Retrieved {len(messages)} messages from {topic_name}")
        return messages
        
    except Exception as e:
        print(f"Error getting messages from {topic_name}: {e}")
        return []

@app.route('/')
def index():
    """Main page to display messages"""
    return render_template('index.html')

@app.route('/api/summaries')
def get_summaries():
    """API endpoint to get summary messages"""
    messages = get_messages_from_topic(SUMMARIES_TOPIC)
    print(f"API /api/summaries called. Returning {len(messages)} messages")
    return jsonify(messages)

@app.route('/api/unread')
def get_unread():
    """API endpoint to get unread messages"""
    messages = get_messages_from_topic(UNREAD_TOPIC)
    print(f"API /api/unread called. Returning {len(messages)} messages")
    return jsonify(messages)

@app.route('/api/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'kafka_connected': True
    })

if __name__ == '__main__':
    print("Starting Flask app with direct Kafka consumption...")
    app.run(debug=False, host='0.0.0.0', port=5000)
