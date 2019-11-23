import cv2

cap = cv2.VideoCapture(0)

frame_w = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
frame_h = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
fps = cap.get(cv2.CAP_PROP_FPS)

print("Width: '{}'".format(frame_w))
print("Height: '{}'".format(frame_h))
print("FPS: '{}'".format(fps))

if not cap.isOpened():
    print("Could not open the camera feed")

while cap.isOpened():
    ret, frame = cap.read()

    if ret:
        cv2.imshow("camera", frame)

        cv2.imshow("Grayscale cam", cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY))

        if cv2.waitKey(20) & 0xFF == ord('q'):
            break
    else:
        break
cap.release()
cv2.destroyAllWindows()

