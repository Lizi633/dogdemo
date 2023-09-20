from flask import Flask, request, jsonify
import threading
import paho.mqtt.client as mqtt

# mqtt服务器IP地址
BROKER = "xxxx"
PORT = 1883

app = Flask(__name__)

# def load(key):
#     cap = cv2.VideoCapture(f'rtmp://your_server_ip/live/{key}')

#     while True:
#         ret, frame = cap.read()
#         if not ret:
#             break
    
#     # 在此处添加你的处理代码（例如显示帧）
#         cv2.imshow('Frame', frame)

#     # 按“q”键退出
#         if cv2.waitKey(1) & 0xFF == ord('q'):
#             break

#     cap.release()

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected to MQTT Broker!")
    else:
        print(f"Failed to connect, return code {rc}")

def connect_mqtt(topic):
    # 创建一个MQTT客户端对象
    client = mqtt.Client()
    
    # 将回调函数分配给客户端对象
    client.on_connect = on_connect
    
    # 连接到broker
    client.connect(BROKER, PORT, 60)
    
    # 启动网络循环来处理MQTT网络通信,forever是一个阻塞调用，它将阻止任何后续的代码执行,要同时执行上传视频流用loop_start()函数
    client.loop_start()
    print(topic)
    ret = client.publish(f"{topic}", "检测到狗上厕所")
    if ret[0] == 0:
        print(f"Message sent to topic {topic}")
    else:
        print(f"Failed to send message to topic {topic}")
    # 停止MQTT客户端循环和断开连接
    client.loop_stop()
    client.disconnect()

def perform_action(topic):
    # 这里模拟检测视频的过程
    while True:
        import time
        time.sleep(5)  # 延迟50秒
    # 检测到了狗上厕所pub消息
        connect_mqtt(f"{topic}")
        print(f"Action performed with: {topic}")

def async_perform_action(topic):
    thread = threading.Thread(target=perform_action, args=(topic,))
    print(topic)
    thread.start()

@app.route('/data', methods=['GET', 'POST'])
def handle_data():
    if request.method == 'GET':
        # 对GET请求返回一些数据
        return jsonify({"message": "Hello, world!"})
    elif request.method == 'POST':
        # 对POST请求返回发送的JSON数据
        data = request.get_json()
        print(data)
        key = data.get('myname')
        async_perform_action(key)
        print("成功")
        return jsonify(data)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)


