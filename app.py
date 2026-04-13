from flask import Flask, render_template
from flask_socketio import SocketIO
from kafka import KafkaConsumer
import threading
import json

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode="threading")

KAFKA_SERVER = "localhost:9092"

TOPICS = [
    "zulip-summaries",
    "zulip-unread-messages"
]


def parse_message(x):
    try:
        data = x.decode('utf-8')
        data = json.loads(data)

        if isinstance(data, str):  # doble JSON
            data = json.loads(data)

        return data
    except:
        return str(x)


def consume_topic(topic):
    consumer = KafkaConsumer(
        topic,
        bootstrap_servers=KAFKA_SERVER,
        auto_offset_reset='latest',
        enable_auto_commit=True,
        value_deserializer=lambda x: x  # 👈 debug raw
    )

    for msg in consumer:
        print("----- MENSAJE RAW -----")
        print(type(msg.value))
        print(msg.value)
        print("----------------------")

        parsed = parse_message(msg.value)

        socketio.emit("new_message", {
            "topic": topic,
            "message": parsed
        })


def start_consumers():
    threads = []
    for topic in TOPICS:
        t = threading.Thread(target=consume_topic, args=(topic,))
        t.daemon = True
        t.start()
        threads.append(t)


@app.route("/")
def index():
    return render_template("index1.html")


if __name__ == "__main__":
    start_consumers()
    socketio.run(app, host="0.0.0.0", port=5000)