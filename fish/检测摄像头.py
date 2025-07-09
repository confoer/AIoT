import cv2

def list_available_cameras(max_tested=10):
    available_cameras = []
    for i in range(max_tested):
        cap = cv2.VideoCapture(i)
        if cap.isOpened():
            available_cameras.append(i)
            cap.release()
    return available_cameras

available_cams = list_available_cameras()
print(f"可用的摄像头索引: {available_cams}")