import cv2
import numpy as np

class PersonDetector:

    #Constructor
    def __init__(self):
        a=0
        self.net = cv2.dnn.readNet("C:/Users/user/Downloads/object-detection-opencv-master/object-detection-opencv-master/yolov3.weights", "C:/Users/user/Downloads/object-detection-opencv-master/object-detection-opencv-master/yolov3.cfg")

    def get_output_layers(self,net):
        
        layer_names = net.getLayerNames()
        
        output_layers = [layer_names[i-1] for i in net.getUnconnectedOutLayers()]

        return output_layers


    def detectObjects(self,imagePath):    
        image = cv2.imread(imagePath)
        # image = cv2.imread("C:/Users/user/Pictures/cars.jpg")

        Width = image.shape[1]
        Height = image.shape[0]
        scale = 0.00392

        classes = None

        with open("C:/Users/user/Downloads/object-detection-opencv-master/object-detection-opencv-master/yolov3.txt", 'r') as f:
            classes = [line.strip() for line in f.readlines()]

        #net = cv2.dnn.readNet("C:/Users/user/Downloads/object-detection-opencv-master/object-detection-opencv-master/yolov3.weights", "C:/Users/user/Downloads/object-detection-opencv-master/object-detection-opencv-master/yolov3.cfg")

        blob = cv2.dnn.blobFromImage(image, scale, (416,416), (0,0,0), True, crop=False)

        self.net.setInput(blob)

        outs = self.net.forward(self.get_output_layers(self.net))

        class_ids = []
        confidences = []
        boxes = []
        conf_threshold = 0.5
        nms_threshold = 0.4


        for out in outs:
            for detection in out:
                scores = detection[5:]
                class_id = np.argmax(scores)
                confidence = scores[class_id]
                if confidence > 0.5:
                    center_x = int(detection[0] * Width)
                    center_y = int(detection[1] * Height)
                    w = int(detection[2] * Width)
                    h = int(detection[3] * Height)
                    x = center_x - w / 2
                    y = center_y - h / 2
                    class_ids.append(class_id)
                    confidences.append(float(confidence))
                    boxes.append([x, y, w, h])


        indices = cv2.dnn.NMSBoxes(boxes, confidences, conf_threshold, nms_threshold)
        print(indices)



        for i in indices:
            box = boxes[i]
            x = box[0]
            y = box[1]
            w = box[2]
            h = box[3]

            clase = class_ids[i]
            bodyBoundingBox = [round(x), round(y), round(x+w), round(y+h)]

        return class_ids
    