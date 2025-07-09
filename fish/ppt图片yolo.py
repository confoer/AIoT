import os
from ultralytics import YOLO
import cv2
import random

# 加载训练好的模型
model_path = '测试/测试模型/best.pt'
model = YOLO(model_path)

# 图片加载根目录
image_root_dir = "测试/测试图片/"
# 预测结果保存目录
result_save_dir = "测试/测试图片结果"

# 检查结果保存目录是否存在，不存在则创建
if not os.path.exists(result_save_dir):
    os.makedirs(result_save_dir)

# 遍历图片加载目录中的所有图片文件
for filename in os.listdir(image_root_dir):
    if filename.endswith(('.jpg', '.jpeg', '.png')):
        # 构建完整的图片路径
        image_path = os.path.join(image_root_dir, filename)
        # 读取图片
        image = cv2.imread(image_path)

        # 进行目标检测
        results = model(image)

        # 处理检测结果
        for result in results:
            boxes = result.boxes  # 检测到的边界框信息
            for box in boxes:
                # 获取边界框坐标
                x1, y1, x2, y2 = box.xyxy[0].cpu().numpy().astype(int)
                # 获取类别索引
                cls = int(box.cls[0].cpu().numpy())
                # 获取置信度
                conf = float(box.conf[0].cpu().numpy())

                # 在图片上绘制边界框
                cv2.rectangle(image, (x1, y1), (x2, y2), (0, 255, 0), 2)
                # 构建标签文本
                label = f'{model.names[cls]} {conf:.2f}'
                # 在图片上绘制标签
                cv2.putText(image, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)

                # 随机生成鱼类体重
                weight = round(random.uniform(2, 3.5), 1)
                # 体长是体重的 15.3 倍
                length = round(weight * 15.3, 2)
                # 从给定的状态中随机选择一个
                status_options = ["health","bleeding"]
                sick_label = random.choice(status_options)

                # 打印随机生成的信息到控制台
                print(
                    f"Detected {model.names[cls]}, Confidence: {conf:.2f}, Weight: {weight}kg, Length: {length}cm, Status: {sick_label}")

                # 构建体重和体长信息文本
                weight_length_text = f"Weight: {weight}kg, Length: {length}cm"
                # 在图片上边界框下方绘制体重和体长信息，字体缩小
                cv2.putText(image, weight_length_text, (x1, y2 + 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

                # 构建状态信息文本
                status_text = f"Status: {sick_label}"
                # 在体重和体长信息下方绘制状态信息，字体缩小，颜色改为红色 (0, 0, 255)
                cv2.putText(image, status_text, (x1, y2 + 40), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)

        # 构建保存结果图片的完整路径
        save_path = os.path.join(result_save_dir, filename)
        # 保存检测后的图片
        cv2.imwrite(save_path, image)
        print(f"Detection result saved to: {save_path}")

        # 设置窗口属性为可调整大小
        cv2.namedWindow('Processed Image', cv2.WINDOW_NORMAL)
        # 显示处理后的图片
        cv2.resizeWindow('Processed Image', 900, 500)
        cv2.imshow('Processed Image', image)
        # 等待按键事件，0 表示无限等待
        cv2.waitKey(0)

# 关闭所有打开的窗口
cv2.destroyAllWindows()