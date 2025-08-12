import cv2
import functions.myfunctions as funct

funct.clear()

funct.getcwd('media/img/')

# person = 0
# danger = 0

# width = 1280
# height = 720

# user = "root"
# pwd = "Sisa.2025"
# ip = "192.168.1.144"
# rstp_url = f"rtsp://{user}:{pwd}@{ip}/axis-media/media.amp"

# cameras = [
#     f"rtsp://{user}:{pwd}@{ip}/axis-media/media.amp",
#     f"rtsp://{user}:{pwd}@{ip}/axis-media/media.amp",
#     f"rtsp://{user}:{pwd}@{ip}/axis-media/media.amp",
#     f"rtsp://{user}:{pwd}@{ip}/axis-media/media.amp"
# ]

# cap = cv2.VideoCapture(rstp_url)

# # persons_cascade = cv2.CascadeClassifier("./haarcascade_fullbody.xml")

# while True:
#     ret, frame = cap.read()
    
#     if not ret: break
    
#     # gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
#     # persons = persons_cascade.detectMultiScale(gray, 1.5, 1)
#     color = (0 , 255, 0)
    
#     #detected area
    
    
    
#     # for (x, y, w, h) in persons:
#     #     cv2.rectangle(frame, (x, y), (x + w, y + h), color, 2)
    
    
#     frame = cv2.resize(frame, (width, height))

    
#     cv2.imshow("Test", frame)

    
#     if cv2.waitKey(1) & 0xFF == 27 or cv2.waitKey(1) & 0xFF == ord('q'): break
# cap.release()
# cv2.destroyAllWindows()