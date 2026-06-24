import cv2

# Threshold to detect object
#thres = 0.45 

classNames = []
# FIX 1: Using relative paths since your username is 'cubobots', not 'pi'.
# Ensure your terminal is running inside the Object_Detection_Files folder.
classFile = "coco.names"
with open(classFile,"rt") as f:
    classNames = f.read().rstrip("\n").split("\n")

configPath = "ssd_mobilenet_v3_large_coco_2020_01_14.pbtxt"
weightsPath = "frozen_inference_graph.pb"

net = cv2.dnn_DetectionModel(weightsPath,configPath)
net.setInputSize(320,320)
net.setInputScale(1.0/ 127.5)
net.setInputMean((127.5, 127.5, 127.5))
net.setInputSwapRB(True)


def getObjects(img, thres, nms, draw=True, objects=[]):
    classIds, confs, bbox = net.detect(img,confThreshold=thres,nmsThreshold=nms)
    
    if len(objects) == 0: objects = classNames
    objectInfo =[]
    if len(classIds) != 0:
        for classId, confidence,box in zip(classIds.flatten(),confs.flatten(),bbox):
            className = classNames[classId - 1]
            if className in objects:
                objectInfo.append([box,className])
                if (draw):
                    cv2.rectangle(img,box,color=(0,255,0),thickness=2)
                    cv2.putText(img,classNames[classId-1].upper(),(box[0]+10,box[1]+30),
                    cv2.FONT_HERSHEY_COMPLEX,1,(0,255,0),2)
                    cv2.putText(img,str(round(confidence*100,2)),(box[0]+200,box[1]+30),
                    cv2.FONT_HERSHEY_COMPLEX,1,(0,255,0),2)

    return img,objectInfo


if __name__ == "__main__":
    # FIX 2: Added cv2.CAP_V4L2 to bypass the GStreamer crash.
    # NOTE: Change '0' to the correct camera index if your EMEET S600 is on a different node (like 2).
    cap = cv2.VideoCapture(0, cv2.CAP_V4L2)
    
    # Downscaling to 480p to help the Raspberry Pi CPU process frames faster
    cap.set(3,640)
    cap.set(4,480)

    while True:
        success, img = cap.read()
        
        # If the camera fails to grab a frame, stop the loop instead of crashing
        if not success:
            print("Failed to read from camera. Check connection and index.")
            break
            
        result, objectInfo = getObjects(img,0.45,0.2)
        
        cv2.imshow("Output",img)
        
        # FIX 3: Added a graceful exit. Press 'q' on your keyboard to close the window.
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Clean up the camera and windows when done
    cap.release()
    cv2.destroyAllWindows()