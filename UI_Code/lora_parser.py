import struct
import traceback
import serial
import serial.tools.list_ports
from time import sleep

def parse_data(module_id, data):
    """根据模块ID解析数据内容（完整版）"""
    parsed = {}
    try:
        if module_id == 2:
            # 模块2：水深与水压传感器（数据长度10字节）
            # --------------------------------------------
            # | 压力(4B,u32) | 深度(4B,u32) | 温度(2B,u16) |
            # --------------------------------------------
            pressure = struct.unpack('>I', data[0:4])[0]    # mbar (原值)
            depth = struct.unpack('>I', data[4:8])[0] / 1000  # 转换为米
            temp = struct.unpack('>H', data[8:10])[0] / 10    # 温度(℃)
            parsed = {
                "pressure_mbar": pressure,
                "depth_m": round(depth, 3),
                "temperature_c": round(temp, 1)
            }

        elif module_id == 3:
            # 模块3：雨量传感器（数据长度10字节）
            # ------------------------------------------------
            # | 风速(2B,u16) | 运行时间(4B,u32) | 雨量(4B,u32) |
            # ------------------------------------------------
            wind = struct.unpack('>H', data[0:2])[0] / 100    # m/s (V*100存储)
            time_sec = struct.unpack('>I', data[2:6])[0]      # 秒
            rainfall = struct.unpack('>I', data[6:10])[0] / 100  # 毫米(Y*100)
            parsed = {
                "wind_speed_m_s": round(wind, 2),
                "uptime_sec": time_sec,
                "rainfall_mm": round(rainfall, 2)
            }

        elif module_id == 4:
            # 模块4：盐度传感器（数据长度12字节）
            # ------------------------------------------------------
            # | 电导率(4B,u32) | 电导率_25(4B,u32) | 盐度(2B,u16) | 温度(2B,u16) |
            # ------------------------------------------------------
            conductivity = struct.unpack('>I', data[0:4])[0]       # us/cm
            conductivity_25 = struct.unpack('>I', data[4:8])[0]    # us/cm
            salinity = struct.unpack('>H', data[8:10])[0] / 10     # 盐度(S*10)
            temp = struct.unpack('>H', data[10:12])[0] / 10        # 水温(℃)
            parsed = {
                "conductivity_us_cm": conductivity,
                "conductivity_25_us_cm": conductivity_25,
                "salinity": round(salinity, 1),
                "water_temp_c": round(temp, 1)
            }

        elif module_id == 5:
            # 模块5：PH传感器（数据长度4字节）
            # ---------------------------
            # | PH值(2B,u16) | 温度(2B,u16) |
            # ---------------------------
            ph_value = struct.unpack('>H', data[0:2])[0] / 10   # PH*10存储
            temp = struct.unpack('>H', data[2:4])[0] / 10       # 温度(℃)
            parsed = {
                "ph": round(ph_value, 1),
                "temperature_c": round(temp, 1)
            }

        elif module_id == 6:
            # 模块6：激光测距（数据长度4字节）
            # -------------------------
            # | 距离值(4B,u32) |
            # -------------------------
            distance = struct.unpack('>I', data[0:4])[0]  # 单位：毫米
            parsed = {"distance_mm": distance}

        elif module_id == 7:
            # 模块7：激光雷达（动态长度）
            # ----------------------------------------------------------
            # | 帧号(1B) | 转速(1B) | 起始角(2B) | 点数N(1B) | 距离值(2B*N) |
            # ----------------------------------------------------------
            frame_num = data[0]
            rpm = data[1] * 0.05  # 0.05r/s * 原始值
            start_angle = struct.unpack('>H', data[2:4])[0] * 0.01  # 0.01度/单位
            point_count = data[4]
            distances = [
                struct.unpack('>H', data[5+i*2 : 7+i*2])[0] * 0.25  # 0.25mm/单位
                for i in range(point_count)
            ]
            parsed = {
                "frame_num": frame_num,
                "rpm": round(rpm, 2),
                "start_angle_deg": round(start_angle, 2),
                "point_count": point_count,
                "distances_mm": [round(d, 2) for d in distances]
            }

        elif module_id == 8:
            # 模块8：9轴惯导（数据长度52字节）
            # --------------------------------------------------------
            # | 加速度(4B*3) | 角速度(4B*3) | 磁场(2B*3) | 四元数(4B*4) | 欧拉角(4B*3) |
            # --------------------------------------------------------
            # 加速度（单位：9.8m/s²）
            accel = [
                round(struct.unpack('>f', data[i:i+4])[0], 3)
                for i in range(0, 12, 4)
            ]
            # 角速度（单位：度/秒）
            gyro = [
                round(struct.unpack('>f', data[i:i+4])[0], 3)
                for i in range(12, 24, 4)
            ]
            # 磁场强度（单位：mGs）
            mag = [
                struct.unpack('>h', data[i:i+2])[0]
                for i in range(24, 30, 2)
            ]
            # 四元数
            quaternion = [
                round(struct.unpack('>f', data[i:i+4])[0], 4)
                for i in range(30, 46, 4)
            ]
            # 欧拉角（单位：度）
            euler = [
                round(struct.unpack('>f', data[i:i+4])[0], 2)
                for i in range(46, 58, 4)
            ]
            parsed = {
                "acceleration_g": accel,
                "angular_velocity_deg_s": gyro,
                "magnetic_field_mGs": mag,
                "quaternion": quaternion,
                "euler_angles_deg": euler
            }

        elif module_id == 9:
            # 模块9：GPS（数据长度21字节）
            # ------------------------------------------------------
            # | 经度(4B) | 经度方向(1B) | 纬度(4B) | 纬度方向(1B) | 时间(7B) |
            # ------------------------------------------------------
            lon_raw = struct.unpack('>I', data[0:4])[0] / 100000  # 经度(原始值*1e5)
            lon_dir = chr(data[4])  # E/W
            lat_raw = struct.unpack('>I', data[5:9])[0] / 100000  # 纬度(原始值*1e5)
            lat_dir = chr(data[9])  # N/S
            # 时间解析（7字节：年2B + 月1B + 日1B + 时1B + 分1B + 秒1B）
            year = struct.unpack('>H', data[10:12])[0]
            month = data[12]
            day = data[13]
            hour = data[14]
            minute = data[15]
            second = data[16]
            parsed = {
                "longitude": round(lon_raw, 5) * (1 if lon_dir == 'E' else -1),
                "latitude": round(lat_raw, 5) * (1 if lat_dir == 'N' else -1),
                "timestamp": f"{year}-{month:02d}-{day:02d} {hour:02d}:{minute:02d}:{second:02d}"
            }

        elif module_id == 11:
            # 模块11：图像（JPEG动态传输）
            # ----------------------------------------
            # | 总帧数(1B) | 帧号(1B) | 数据长度(1B) | 数据(NB) |
            # ----------------------------------------
            total_frames = data[0]
            frame_seq = data[1]
            data_length = data[2]
            image_data = data[3:3+data_length]
            parsed = {
                "total_frames": total_frames,
                "frame_seq": frame_seq,
                "jpeg_data": image_data.hex()  # 返回十六进制或保存为文件
            }

        elif module_id == 13:
            # 模块13：风力（同模块3结构）
            # ------------------------------------------------
            # | 风速(2B,u16) | 运行时间(4B,u32) | 雨量(4B,u32) |
            # ------------------------------------------------
            wind = struct.unpack('>H', data[0:2])[0] / 100    # m/s (V*100存储)
            time_sec = struct.unpack('>I', data[2:6])[0]      # 秒
            rainfall = struct.unpack('>I', data[6:10])[0] / 100  # 毫米(Y*100)
            parsed = {
                "wind_speed_m_s": round(wind, 2),
                "uptime_sec": time_sec,
                "rainfall_mm": round(rainfall, 2)
            }

        else:
            # 未定义的模块返回原始数据
            parsed = {"raw_data": data.hex(), "warning": "未定义的模块ID"}

    except Exception as e:
        parsed = {
            "error": f"解析失败: {str(e)}",
            "raw_data": data.hex(),
            "stack_trace": traceback.format_exc()
        }

    return parsed

def validate_checksum(frame_header, device_id, module_id, data, checksum_received):
    """校验和验证函数（异或校验）"""
    checksum = 0
    # 帧头参与校验（2字节分别异或）
    checksum ^= frame_header[0]  # 帧头高字节（0x5A）
    checksum ^= frame_header[1]  # 帧头低字节（0xA5）
    # 设备ID和模块ID参与校验
    checksum ^= device_id
    checksum ^= module_id
    # 数据部分逐字节异或
    for byte in data:
        checksum ^= byte
    # 返回校验结果（计算值是否等于接收值）
    return checksum == checksum_received

# def decode_lora_packet(packet):
#     """解析完整的LoRa数据包"""
#     index = 0
#     results = []
#     while index <= len(packet) - 6:  # 最小帧长度检查（帧头2B+设备1B+模块1B+长度1B+校验1B）
#         # 查找帧头0x5AA5（协议规定帧头固定值）
#         if packet[index] == 0x5A and packet[index+1] == 0xA5:
#             # 提取帧头（元组形式保存）
#             frame_header = (packet[index], packet[index+1])
#             # 设备号（1字节）
#             device_id = packet[index+2]
#             # 模块号（1字节）
#             module_id = packet[index+3]
#             # 数据长度（1字节）
#             data_length = packet[index+4]
#             # 数据起始位置（当前索引+5字节）
#             data_start = index + 5
#             data_end = data_start + data_length
            
#             # 检查数据完整性（防止越界）
#             if data_end + 1 > len(packet):
#                 break  # 数据不完整，退出循环
                
#             # 提取数据部分（根据长度字段）
#             data = packet[data_start:data_end]
#             # 校验和（1字节）
#             checksum = packet[data_end]
            
#             # 校验验证通过才进行解析
#             if validate_checksum(frame_header, device_id, module_id, data, checksum):
#                 result = {
#                     "device_id": device_id,
#                     "module_id": module_id,
#                     "data": parse_data(module_id, data)
#                 }
#                 results.append(result)
#                 index = data_end + 1  # 成功解析后跳到下一帧起始位置
#             else:
#                 index += 1  # 校验失败，逐字节查找下一个帧头
#         else:
#             index += 1  # 未找到帧头，继续向后搜索
#     return results

def decode_lora_packet(packet):
    """解析完整的LoRa数据包，返回结果列表和已处理的字节位置"""
    index = 0
    results = []
    max_processed = 0
    # print(packet)
    # print(len(packet))
    while index <= len(packet) - 6:
        if packet[index] == 0x5A and packet[index+1] == 0xA5:  # 帧头检测
            # 提取字段
            frame_header = (packet[index], packet[index+1])
            device_id = packet[index+2]
            module_id = packet[index+3]
            data_length = packet[index+4]
            data_start = index + 5
            data_end = data_start + data_length -1
            # 检查数据完整性
            if data_end + 1 > len(packet):
                break  # 数据不完整，停止解析
            data = packet[data_start:data_end]
            checksum = packet[data_end]
            # 校验和验证
            if validate_checksum(frame_header, device_id, module_id, data, checksum):
                try:
                    parsed = parse_data(module_id, data)
                    results.append({
                        "device_id": device_id,
                        "module_id": module_id,
                        "data": parsed
                    })
                    index = data_end + 1  # 跳到下一帧
                    max_processed = index
                except:
                    index += 1  # 解析失败，继续搜索
            else:
                index += 1  # 校验失败，继续搜索
        else:
            index += 1  # 未找到帧头，继续搜索
    return results, max_processed

def find_ch340_port():
    """自动检测CH340串口设备"""
    ports = serial.tools.list_ports.comports()
    for port in ports:
        if "CH9102" in port.description:  # 根据操作系统描述关键词匹配
            return port.device
    return None

def serial_receiver():
    # 1. 自动检测CH340串口
    port = find_ch340_port()
    if not port:
        raise Exception("未检测到CH340设备，请检查连接")

    # 2. 配置串口参数（根据实际设备调整波特率）
    ser = serial.Serial(
        port=port,
        baudrate=115200,        # 常见值：9600/115200
        bytesize=serial.EIGHTBITS,
        parity=serial.PARITY_NONE,
        stopbits=serial.STOPBITS_ONE,
        timeout=0.1           # 非阻塞读取，超时时间0.1秒
    )
    
    # 3. 数据缓冲区初始化
    buffer = bytearray()
    print(f"已连接串口 {port}，开始接收数据...")

    try:
        while True:
            # 4. 读取串口数据并追加到缓冲区
            # data = ser.read(ser.in_waiting or 1)
            # while(ser.in_waiting<10):
            #     pass
            sleep(0.1)
            # data = ser.read()
            data = ser.read(ser.in_waiting)
            # print(data)
            # print(type(data))
            if data:
                buffer.extend(data)
                #print(buffer)
                # 5. 解析数据包
                results, processed_pos = decode_lora_packet(buffer)
                #print(results)
                #print(processed_pos)
                # 6. 输出解析结果
                for result in results:
                    print(f"[设备{result['device_id']}] 模块{result['module_id']} 数据:")
                    print(result["data"])
                
                # 7. 截断已处理的数据
                buffer = buffer[processed_pos:]
                
            # sleep(0.01)  # 降低CPU占用

    except KeyboardInterrupt:
        print("用户终止程序")
    finally:
        ser.close()
        print("串口已关闭")

if __name__ == "__main__":
    serial_receiver()

    