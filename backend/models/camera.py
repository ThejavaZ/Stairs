import cv2

class Camera:
    def __init__(self, rtsp_url:str, camera_id:int):
        self.camera = camera_id
        self.rtsp_url = rtsp_url
        self.cap = cv2.VideoCapture(rtsp_url)
        if not self.cap.isOpened(): print(f"Error: Camera not found: {camera_id}")
        
    
    def get_frame(self):
        ret, frame = self.cap.read()
        
        if ret: return frame
        else: return None