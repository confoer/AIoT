import eventlet
import serial
from flask import Flask, render_template
from flask_socketio import SocketIO, emit
from lora_parser import serial_receiver, decode_lora_packet, find_ch340_port
import random
import time
import json
import os
from flask import Flask, render_template, request, redirect, url_for, send_from_directory, jsonify
import threading
import glob
import re
from datetime import datetime
import shutil
from werkzeug.utils import secure_filename

# 解决异步问题
eventlet.monkey_patch()

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
# app.config['STATIC_FOLDER'] = os.path.join(app.root_path, '图片')
socketio = SocketIO(app, cors_allowed_origins='*', async_mode='eventlet')

# 全局数据缓存
sensor_data_cache = {
    'pressure': [],
    'depth': [],
    'temperature': [],
    'wind_speed': [],
    # 'rainfall': [],
    'salinity': [],
    'ph': [],
    'distance': []
}

# 修改后的串口接收函数，用于SocketIO推送
def socket_serial_receiver():
    port = find_ch340_port()
    if not port:
        print("模拟模式：生成随机传感器数据")
        current_wind_speed = 15.0  # 初始风速
        def simulate_data():
            # 立即生成并发送第一组数据
            nonlocal current_wind_speed
            # 更新风速：从当前值随机递减0.5-3.0，最小为0
            current_wind_speed -= random.uniform(0.5, 3.0)
            if current_wind_speed < 0:
                current_wind_speed = 15.0  # 重置为初始值
            simulated = {
                'pressure': [round(random.uniform(900, 1100), 2)],
                'depth': [round(random.uniform(0.5, 5.0), 2)],
                'temperature': [round(random.uniform(10, 35), 1)],
                'wind_speed': [round(current_wind_speed, 2)],
                # 'rainfall': [round(random.uniform(0, 50), 2)],
                'salinity': [round(random.uniform(20, 40), 1)],
                'ph': [round(random.uniform(6.5, 8.5), 1)],
                'distance': [random.randint(500, 2000)]
            }
            for key in sensor_data_cache:
                sensor_data_cache[key].extend(simulated[key])
                if len(sensor_data_cache[key]) > 100:
                    sensor_data_cache[key] = sensor_data_cache[key][-100:]
            socketio.emit('sensor_update', {'type': 'simulation', 'history': sensor_data_cache})
            print(f"模拟数据已发送: {sensor_data_cache}")
            
            # 后续数据每1秒生成一次
            while True:
                current_wind_speed -= random.uniform(0.5, 3.0)
                if current_wind_speed < 0:
                    current_wind_speed = 15.0  # 重置为初始值
                simulated = {
                    'pressure': [round(random.uniform(998, 1010), 2)],
                    'depth': [round(random.uniform(0, 1.0), 2)],
                    'temperature': [round(random.uniform(30, 32), 1)],
                    # 'wind_speed': [round(random.uniform(0, 20), 2)],
                    'wind_speed': [round(current_wind_speed, 2)],
                    # 'rainfall': [round(random.uniform(0, 50), 2)],
                    'salinity': [round(random.uniform(30, 35), 1)],
                    'ph': [round(random.uniform(6.8, 8.4), 1)],
                    'distance': [random.randint(80, 90)]
                }
                for key in sensor_data_cache:
                    sensor_data_cache[key].extend(simulated[key])
                    if len(sensor_data_cache[key]) > 100:
                        sensor_data_cache[key] = sensor_data_cache[key][-100:]
                socketio.emit('sensor_update', {'type': 'simulation', 'history': sensor_data_cache})
                eventlet.sleep(5)
        sim_thread = eventlet.spawn(simulate_data)
        return

    try:
        ser = serial.Serial(
            port=port,
            baudrate=115200,
            bytesize=serial.EIGHTBITS,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            timeout=0.1
        )
    except Exception as e:
        print(f"串口连接失败: {e}")
        return

    buffer = bytearray()
    print(f"已连接串口 {port}，开始接收数据...")

    try:
        while True:
            data = ser.read(ser.in_waiting)
            if data:
                buffer.extend(data)
                results, processed_pos = decode_lora_packet(buffer)
                for result in results:
                    # 处理不同模块的数据
                    module_id = result['module_id']
                    sensor_data = result['data']
                    
                    # 根据模块ID分类处理数据
                    if module_id == 2:  # 水深与水压
                        sensor_data_cache['pressure'].append(sensor_data.get('pressure_mbar', 0))
                        sensor_data_cache['depth'].append(sensor_data.get('depth_m', 0))
                        sensor_data_cache['temperature'].append(sensor_data.get('temperature_c', 0))
                        
                        # 只保留最近100个数据点
                        for key in ['pressure', 'depth', 'temperature']:
                            if len(sensor_data_cache[key]) > 100:
                                sensor_data_cache[key].pop(0)
                        
                        # 推送数据到前端
                        socketio.emit('sensor_update', {
                            'type': 'water_sensor',
                            'pressure': sensor_data_cache['pressure'][-1],
                            'depth': sensor_data_cache['depth'][-1],
                            'temperature': sensor_data_cache['temperature'][-1],
                            'history': sensor_data_cache
                        })
                    
                    elif module_id == 3 or module_id == 13:  # 雨量/风力
                        sensor_data_cache['wind_speed'].append(sensor_data.get('wind_speed_m_s', 0))
                        # sensor_data_cache['rainfall'].append(sensor_data.get('rainfall_mm', 0))
                        
                        if len(sensor_data_cache['wind_speed']) > 100:
                            sensor_data_cache['wind_speed'].pop(0)
                        # if len(sensor_data_cache['rainfall']) > 100:
                            # sensor_data_cache['rainfall'].pop(0)
                        
                        socketio.emit('sensor_update', {
                            'type': 'weather_sensor',
                            'wind_speed': sensor_data_cache['wind_speed'][-1],
                            # 'rainfall': sensor_data_cache['rainfall'][-1],
                            'history': sensor_data_cache
                        })
                    
                    elif module_id == 4:  # 盐度
                        sensor_data_cache['salinity'].append(sensor_data.get('salinity', 0))
                        if len(sensor_data_cache['salinity']) > 100:
                            sensor_data_cache['salinity'].pop(0)
                        
                        socketio.emit('sensor_update', {
                            'type': 'salinity_sensor',
                            'salinity': sensor_data_cache['salinity'][-1],
                            'history': sensor_data_cache
                        })
                    
                    elif module_id == 5:  # PH
                        sensor_data_cache['ph'].append(sensor_data.get('ph', 0))
                        if len(sensor_data_cache['ph']) > 100:
                            sensor_data_cache['ph'].pop(0)
                        
                        socketio.emit('sensor_update', {
                            'type': 'ph_sensor',
                            'ph': sensor_data_cache['ph'][-1],
                            'history': sensor_data_cache
                        })
                    
                    elif module_id == 6:  # 激光测距
                        sensor_data_cache['distance'].append(sensor_data.get('distance_mm', 0))
                        if len(sensor_data_cache['distance']) > 100:
                            sensor_data_cache['distance'].pop(0)
                        
                        socketio.emit('sensor_update', {
                            'type': 'distance_sensor',
                            'distance': sensor_data_cache['distance'][-1],
                            'history': sensor_data_cache
                        })

                buffer = buffer[processed_pos:]
            time.sleep(0.01)

    except Exception as e:
        print(f"串口接收错误: {e}")
    finally:
        ser.close()
        print("串口已关闭")

# 创建存储返回图片的文件夹
UPLOAD_FOLDER = os.path.join(app.root_path, 'return_images')
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# 指定返回的图片路径
SPECIFIED_IMAGE = os.path.join(app.root_path, 'return_images', 'default.jpg')  # 假设鱼病文件夹中有默认图片

@app.route('/')
def index():
    return render_template('dashboard.html')

@app.route('/upload')
def upload_page():
    return render_template('upload.html')

@app.route('/upload_image', methods=['POST'])
def upload_image():
    if 'file' not in request.files:
        return redirect(request.url)
    file = request.files['file']
    if file.filename == '':
        return redirect(request.url)
    if file:
        # 保存上传的文件（可选）
        filename = secure_filename(file.filename)
        upload_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(upload_path)
        
        # 返回指定的图片
        return send_from_directory(os.path.dirname(SPECIFIED_IMAGE), os.path.basename(SPECIFIED_IMAGE))

@app.route('/return_images/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# 添加新的图片路由
@app.route('/lstm/<filename>')
def serve_lstm_images(filename):
    lstm_folder = os.path.join(app.root_path, 'lstm')
    return send_from_directory(lstm_folder, filename)

@app.route('/鱼病/<filename>')
def serve_fish_disease_images(filename):
    fish_disease_folder = os.path.join(app.root_path, '鱼病')
    return send_from_directory(fish_disease_folder, filename)

@socketio.on('connect')
def handle_connect():
    print('客户端已连接')
    emit('initial_data', {'history': sensor_data_cache})

if __name__ == '__main__':
    # 启动串口接收线程
    serial_thread = threading.Thread(target=socket_serial_receiver, daemon=True)
    serial_thread.start()
    
    # 启动Web服务器
    socketio.run(app, host='0.0.0.0', port=5003, debug=True)