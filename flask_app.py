from flask import Flask, render_template, jsonify
from kafka import KafkaConsumer
import json
import threading
import time
from collections import deque

app = Flask(__name__)

# Global storage for messages (in production, use a proper database)
summaries_messages = deque(maxlen=100)  # Keep last 100 summary messages
unread_messages = deque(maxlen=100)    # Keep last 100 unread messages
consumer_thread = None
stop_consumer = threading.Event()

class KafkaMessageConsumer:
    def __init__(self):
        self.consumer = None
        self.running = False
    
    def start_consuming(self):
        """Start consuming messages from Kafka"""
        try:
            # Configure Kafka consumer
            self.consumer = KafkaConsumer(
                'zulip-unread-messages',  # Topic for unread messages
                'zulip-summaries',        # Topic for summaries
                bootstrap_servers=['localhost:9092'],  # Kafka broker
                value_deserializer=lambda x: json.loads(x.decode('utf-8')),
                auto_offset_reset='earliest',  # Start from the beginning of topics
                enable_auto_commit=True,
                group_id='flask_web_group_full_history'
            )
            
            self.running = True
            print("Kafka consumer started successfully")
            
            # Consume messages
            for message in self.consumer:
                if stop_consumer.is_set():
                    break
                
                # Add message to appropriate deque based on topic
                message_data = {
                    'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
                    'content': message.value,
                    'topic': message.topic,
                    'partition': message.partition,
                    'offset': message.offset
                }
                
                if message.topic == 'zulip-summaries':
                    summaries_messages.append(message_data)
                    print(f"Added to summaries_messages. Total: {len(summaries_messages)}")
                elif message.topic == 'zulip-unread-messages':
                    unread_messages.append(message_data)
                    print(f"Added to unread_messages. Total: {len(unread_messages)}")
                
                print(f"Received message from {message.topic}: {message_data}")
                
        except Exception as e:
            print(f"Error in Kafka consumer: {e}")
            self.running = False
    
    def stop(self):
        """Stop the consumer"""
        self.running = False
        if self.consumer:
            self.consumer.close()
            print("Kafka consumer stopped")

# Global consumer instance
kafka_consumer = KafkaMessageConsumer()

def start_kafka_consumer():
    """Start Kafka consumer in a background thread"""
    global consumer_thread
    consumer_thread = threading.Thread(target=kafka_consumer.start_consuming)
    consumer_thread.daemon = True
    consumer_thread.start()

@app.route('/')
def index():
    """Main page to display messages"""
    return render_template('index.html')

@app.route('/api/summaries')
def get_summaries():
    """API endpoint to get summary messages"""
    print(f"API /api/summaries called. summaries_messages length: {len(summaries_messages)}")
    return jsonify(list(summaries_messages))

@app.route('/api/unread')
def get_unread():
    """API endpoint to get unread messages"""
    print(f"API /api/unread called. unread_messages length: {len(unread_messages)}")
    return jsonify(list(unread_messages))

@app.route('/api/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'kafka_consumer_running': kafka_consumer.running,
        'total_summaries': len(summaries_messages),
        'total_unread': len(unread_messages)
    })

@app.teardown_appcontext
def shutdown_kafka_consumer(exception=None):
    """Clean up Kafka consumer on app shutdown"""
    stop_consumer.set()
    kafka_consumer.stop()

if __name__ == '__main__':
    # Start Kafka consumer before running the app
    start_kafka_consumer()
    
    # Give consumer a moment to start
    time.sleep(2)
    
    # Run Flask app
    app.run(debug=True, host='0.0.0.0', port=5000)
