import cv2

cap = cv2.VideoCapture(0)

cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1296)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 972)
#cap.set(cv2.CAP_PROP_FPS, 42)

print("Width: '{}'".format(cv2.CAP_PROP_FRAME_WIDTH))
print("Height: '{}'".format(cv2.CAP_PROP_FRAME_HEIGHT))
print("FPS: '{}'".format(cv2.CAP_PROP_FPS))

if not cap.isOpened():
    print("Could not open the camera feed")

while cap.isOpened():
    ret, frame = cap.read()

    if ret:
        #height, width = frame.shape[:2]
        #M = cv2.getRotationMatrix2D((width/2, height/2), 180, 1)
        #frame = cv2.warpAffine(frame, M, (width, height))
        cv2.imshow("camera", frame)

        cv2.imshow("Grayscale cam", cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY))

        if cv2.waitKey(20) & 0xFF == ord('q'):
            break
    else:
        break
cap.release()
cv2.destroyAllWindows()

