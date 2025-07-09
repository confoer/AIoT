from deep_sort.utils.parser import get_config
from deep_sort.deep_sort import DeepSort
import torch
import cv2

palette = (2 ** 11 - 1, 2 ** 15 - 1, 2 ** 20 - 1)
cfg = get_config()
cfg.merge_from_file("deep_sort/configs/deep_sort.yaml")
deepsort = DeepSort(cfg.DEEPSORT.REID_CKPT,
                    max_dist=cfg.DEEPSORT.MAX_DIST, min_confidence=cfg.DEEPSORT.MIN_CONFIDENCE,
                    nms_max_overlap=cfg.DEEPSORT.NMS_MAX_OVERLAP, max_iou_distance=cfg.DEEPSORT.MAX_IOU_DISTANCE,
                    max_age=cfg.DEEPSORT.MAX_AGE, n_init=cfg.DEEPSORT.N_INIT, nn_budget=cfg.DEEPSORT.NN_BUDGET,
                    use_cuda=True)


def plot_bboxes(image, bboxes, line_thickness=None):
    # Plots one bounding box on image img
    tl = line_thickness or round(0.002 * (image.shape[0] + image.shape[1]) / 2) + 1  # line/font thickness
    for (x1, y1, x2, y2, cls_id, pos_id) in bboxes:
        color = (0, 0, 255)  # 所有类别都用绿色（BGR格式）
        c1, c2 = (x1, y1), (x2, y2)
        cv2.rectangle(image, c1, c2, color, thickness=tl, lineType=cv2.LINE_AA)
        tf = max(tl - 1, 1)  # font thickness
        t_size = cv2.getTextSize(str(cls_id), 0, fontScale=tl / 3, thickness=tf)[0]  # 确保 cls_id 是字符串
        c2 = c1[0] + t_size[0], c1[1] - t_size[1] - 3
        cv2.rectangle(image, c1, c2, color, -1, cv2.LINE_AA)  # filled
        cv2.putText(image, f'{cls_id} ID-{pos_id}', (c1[0], c1[1] - 2), 0, tl / 3,
                    [225, 255, 255], thickness=tf, lineType=cv2.LINE_AA)
    return image


def update_tracker(bboxes, image):
    bbox_xywh = []
    confs = []
    clss = []

    for box in bboxes:
        x1, y1, x2, y2, conf, cls_name = box  # 解包
        obj = [int((x1 + x2) / 2), int((y1 + y2) / 2), x2 - x1, y2 - y1]
        bbox_xywh.append(obj)
        confs.append(conf)
        clss.append(cls_name)  # 直接使用类别名称（字符串）

    xywhs = torch.Tensor(bbox_xywh)
    confss = torch.Tensor(confs)

    outputs = deepsort.update(xywhs, confss, clss, image)

    bboxes2draw = []
    for value in list(outputs):
        x1, y1, x2, y2, cls_, track_id = value
        bboxes2draw.append((x1, y1, x2, y2, cls_, track_id))

    image = plot_bboxes(image, bboxes2draw)
    return image