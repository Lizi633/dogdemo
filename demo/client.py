import requests
import cv2
import subprocess
import paho.mqtt.client as mqtt

# 服务器IP地址
BROKER = "xxxx" 
PORT = 1883
SUB = ""

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected to MQTT Broker!")
    else:
        print("Failed to connect, return code %d\n", rc)
    client.subscribe(SUB)
    

# 定义当接收到消息时要执行的操作
def on_message(client, userdata, msg):
    print(f"Received message: {msg.topic} -> {msg.payload.decode('utf-8')}")

# 上传本机的key的视频流
def upvideo(key):
# 用OpenCV捕获视频
    cap = cv2.VideoCapture(0)

# 使用ffmpeg推送视频流到RTMP服务器
    command = [
        'ffmpeg',
        '-y',
        '-f', 'rawvideo',
        '-vcodec', 'rawvideo',
        '-pix_fmt', 'bgr24',
        '-s', '{}x{}'.format(640, 480),
        '-r', '30',
        '-i', '-',
        '-c:v', 'libx264',
        '-pix_fmt', 'yuv420p',
        '-preset', 'ultrafast',
        '-f', 'flv',
        f'rtmp://39.108.117.45:1935/live/{key}'
    ]

    proc = subprocess.Popen(command, stdin=subprocess.PIPE)

    while True:
        ret, frame = cap.read()
        if not ret:
            break
    
        # 将帧写入ffmpeg进程的stdin
        proc.stdin.write(frame.tostring())

    cap.release()
    proc.stdin.close()
    proc.wait()

def connect_mqtt(key):
    # 创建一个MQTT客户端对象
    client = mqtt.Client()
    
    # 将回调函数分配给客户端对象
    client.on_connect = on_connect
     # 订阅topic
    print(key)
    # client.subscribe("device1")
    client.on_message = on_message
    
    # 连接到broker
    client.connect(BROKER, PORT, 60)
    
    # 启动网络循环来处理MQTT网络通信,forever是一个阻塞调用，它将阻止任何后续的代码执行,要同时执行上传视频流用loop_start()函数
    client.loop_start()

    # upvideo(key)
    try:
        while True:
            import time
            time.sleep(5)
            print("处理视频流")
    except KeyboardInterrupt:
        print("Exiting...")

    client.loop_stop()

def send_data_and_get_response(url, data_to_send):
    response = requests.post(url, json=data_to_send)
    
    if response.status_code == 200:
        print('POST Success:', response.json())
        response_data = response.json()
        key = response_data.get('myname')
        # 连接mqtt
        global SUB
        SUB=key
        print("sub"+SUB)
        connect_mqtt(key)
        # 在这里调用另一个函数 upvideo(key)

        # print("upvideo")
        # upvideo(key)
    else:
        print('POST Failed:', response.status_code)

def main():
    data_to_send = {"myname": "device1"}
    # xxxx服务器IP地址
    send_data_and_get_response('http://xxxx:5000/data', data_to_send)

if __name__ == "__main__":
    main()