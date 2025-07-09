import os
from ultralytics import YOLO
import cv2
import numpy as np
from tracker import update_tracker
from tracker import plot_bboxes
from deep_sort.utils.parser import get_config
from deep_sort.deep_sort import DeepSort

# 加载训练好的模型
cfg = get_config()
cfg.merge_from_file("deep_sort/configs/deep_sort.yaml")
deepsort = DeepSort(cfg.DEEPSORT.REID_CKPT,
                    max_dist=cfg.DEEPSORT.MAX_DIST, min_confidence=cfg.DEEPSORT.MIN_CONFIDENCE,
                    nms_max_overlap=cfg.DEEPSORT.NMS_MAX_OVERLAP, max_iou_distance=cfg.DEEPSORT.MAX_IOU_DISTANCE,
                    max_age=cfg.DEEPSORT.MAX_AGE, n_init=cfg.DEEPSORT.N_INIT, nn_budget=cfg.DEEPSORT.NN_BUDGET,
                    use_cuda=True)

model_path = '测试/测试模型/best.pt'
model = YOLO(model_path)

# 打开摄像头
cap = cv2.VideoCapture(0)

while True:
    # 读取一帧视频
    ret, frame = cap.read()
    if not ret:
        break

    # 进行目标检测
    results = model(frame)

    # 处理检测结果
    all_boxes = []  # 存储所有检测框
    for result in results:
        boxes = result.boxes  # 检测到的边界框信息
        for box in boxes:
            # 获取边界框坐标
            x1, y1, x2, y2 = box.xyxy[0].cpu().numpy().astype(int)
            # 获取类别索引
            cls_idx = int(box.cls[0].cpu().numpy())
            cls_name = model.names[cls_idx]  # 获取类别名称（字符串）
            # 获取置信度
            conf = float(box.conf[0].cpu().numpy())

            # 在图片上绘制边界框
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
            # 构建标签文本
            label = f'{cls_name} {conf:.2f}'
            # 在图片上绘制标签
            cv2.putText(frame, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)

            # 组合成 [x1, y1, x2, y2, conf, cls_name] 并存入 all_boxes
            all_boxes.append([x1, y1, x2, y2, conf, cls_name])

    # 更新跟踪器（传入所有检测框）
    if all_boxes:
        frame = update_tracker(all_boxes, frame)

    # 显示检测结果
    cv2.imshow('YOLOv8 Object Detection', frame)

    # 按 'q' 键退出循环
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# 释放摄像头并关闭所有窗口
cap.release()
cv2.destroyAllWindows()