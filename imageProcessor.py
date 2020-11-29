import cv2


class ImageAnalyzer:
    def __init__(self, image):
        self.video = cv2.VideoCapture(image)
        self.padding = 20

        self.faceProto = "models/opencv_face_detector.pbtxt"
        self.faceModel = "models/opencv_face_detector_uint8.pb"
        self.ageProto = "models/age_deploy.prototxt"
        self.ageModel = "models/age_net.caffemodel"
        self.genderProto = "models/gender_deploy.prototxt"
        self.genderModel = "models/gender_net.caffemodel"

        self.MODEL_MEAN_VALUES = (78.4263377603, 87.7689143744, 114.895847746)
        self.ageList = ['(0-2)', '(4-6)', '(8-12)', '(15-20)', '(25-32)', '(38-43)', '(48-53)', '(60-100)']
        self.genderList = ['Male', 'Female']

        self.faceNet = cv2.dnn.readNet(self.faceModel, self.faceProto)
        self.ageNet = cv2.dnn.readNet(self.ageModel, self.ageProto)
        self.genderNet = cv2.dnn.readNet(self.genderModel, self.genderProto)

    def highlightFace(self, net, frame, conf_threshold=0.7):
        frameOpencvDnn = frame.copy()
        frameHeight = frameOpencvDnn.shape[0]
        frameWidth = frameOpencvDnn.shape[1]
        blob = cv2.dnn.blobFromImage(frameOpencvDnn, 1.0, (300, 300), [104, 117, 123], True, False)

        net.setInput(blob)
        detections = net.forward()
        faceBoxes = []
        for i in range(detections.shape[2]):
            confidence = detections[0, 0, i, 2]
            if confidence > conf_threshold:
                x1 = int(detections[0, 0, i, 3] * frameWidth)
                y1 = int(detections[0, 0, i, 4] * frameHeight)
                x2 = int(detections[0, 0, i, 5] * frameWidth)
                y2 = int(detections[0, 0, i, 6] * frameHeight)
                faceBoxes.append([x1, y1, x2, y2])
                cv2.rectangle(frameOpencvDnn, (x1, y1), (x2, y2), (0, 255, 0), int(round(frameHeight / 150)), 8)
        return frameOpencvDnn, faceBoxes

    def face_detector(self):
        try:
            while cv2.waitKey(1) < 0:
                hasFrame, frame = self.video.read()
                if not hasFrame:
                    cv2.waitKey()
                    break
                self.resultImg, faceBoxes = self.highlightFace(self.faceNet, frame)
                if not faceBoxes:
                    return "unknown"
                for self.faceBox in faceBoxes:
                    face = frame[max(0, self.faceBox[1] - self.padding):
                                 min(self.faceBox[3] + self.padding, frame.shape[0] - 1),
                           max(0, self.faceBox[0] - self.padding)
                           :min(self.faceBox[2] + self.padding,
                                frame.shape[1] - 1)]

                    blob = cv2.dnn.blobFromImage(face, 1.0, (227, 227), self.MODEL_MEAN_VALUES, swapRB=False)

                    yield blob
        except Exception as err:
            print(err)

    def gender_identifier(self):
        blobs = self.face_detector()
        for blob in blobs:
            self.genderNet.setInput(blob)
            genderPreds = self.genderNet.forward()
            gender = self.genderList[genderPreds[0].argmax()]
            yield gender

    def age_identifier(self):
        blobs = self.face_detector()
        for blob in blobs:
            self.ageNet.setInput(blob)
            agePreds = self.ageNet.forward()
            age = self.ageList[agePreds[0].argmax()]
            yield age


if __name__ == '__main__':
    ia = ImageAnalyzer('cccccc.jpg')
    for data in ia.age_identifier():
        print(data)
        cv2.putText(ia.resultImg, f'{data}', (ia.faceBox[0], ia.faceBox[1] + 10), cv2.FONT_HERSHEY_SIMPLEX, 0.8,
                    (0, 255, 255), 2, cv2.LINE_AA)
        cv2.imshow("Detecting age and gender", ia.resultImg)
    cv2.waitKey(0)
