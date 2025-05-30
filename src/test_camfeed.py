import camera_feed
import cv2

camera_feed.setup_cam(recording_path="data\\recordings\\HD720_SN33773243_10-13-17.svo2")

#MODE = 'IMAGE'
MODE = 'DEPTH'

while True:
    try:
        camera_feed.go_next_frame()
        if MODE == 'IMAGE':
            im = camera_feed.get_image()
        elif MODE == 'DEPTH':
            im = camera_feed.get_depth_display()
        
        cv2.imshow("Test video",im)
        
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q') or key == 27:
            print("Quitting")
            break
    except Exception as e:
        print(e)
        break

camera_feed.shutdown_cam()