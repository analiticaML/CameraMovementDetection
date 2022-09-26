#Se importan librerías
from email.mime import image
from typing_extensions import Self
from faceDetector import FaceDetector
from imageService import ImageService
from cameraService import CameraService
from personDetector import PersonDetector
from rabbitmqService import RabbitmqService
import json
import cv2
import datetime

#Clase donde se desarrolla el proceso de streaming, guardado de captura y notificación
# a servidor de mensajería 
class Recorder:

    #Cosntructor
    def __init__(self,path, mqHost, movementSensibility, millisecondsBetweenCaptures):
        self.path = path
        self.mqHost = mqHost
        self.movementSensibility =  movementSensibility
        self.millisecondsBetweenCaptures = millisecondsBetweenCaptures

    #Método para comenzar el streaming
    def start(self):

        #Se crea objeto tipo ImageService
        imageservice=ImageService()
        #Método para verificar existencia del directorio donde se guardan las capturas
        imageservice.setFolder(self.path)

        #Se crea objeto tipo CameraService
        cameraservice=CameraService()
        #Se establece conexión del streaming
        cameraservice.openCamera(640, 480)

        #Se obtiene la imagen actual en escala de grises
        previousGrayFrame = cameraservice.getGrayScaleFrame(cameraservice.getFrame())

        #Se esteblece un contador para disminuir el número de imágenes a las cuales
        #se les hace el análisis. 
        cuenta=0

        facedetector = FaceDetector()
        persondetector = PersonDetector()

        #Ciclo infinito para la captura de cuadros
        while (True):
            #Nuevo cuadro
            newFrame = cameraservice.getFrame()
            cuenta = cuenta + 1

            #Se salta el análisis de 5 imágenes
            if (cuenta > 15):

                #Cambia  a escala de grises el nuevo cuadro
                newFrameGrayScale = cameraservice.getGrayScaleFrame(newFrame)

                #Se llama a método para detectar movimiento
                if (cameraservice.detectMovement(previousGrayFrame, newFrameGrayScale, 5000)):
                    print("Motion detected!!!")

                    #Se guarda la fecha de hoy y se convierte a string 
                    now = datetime.datetime.now()
                    date=str(now.year)+str(now.month)+str(now.day)+str(now.hour)+str(now.minute)+str(now.second)+str(now.microsecond)
                    #Se gurda la imagen el directorio local con nombre de la imagen como la fecha y hora de la captura
                    path = self.path + "/" + date + ".jpg"
                    data = {}
                    data["path"] = path
                    print("Data: " + str(data["path"]))
                    imageservice.saveImage(newFrame, path)

                    #Se crea objeto tipo Rabbitmq
                    rabbitmqservice=RabbitmqService()

                    # facedetector = FaceDetector()
                    # persondetector = PersonDetector()

                    objetos= persondetector.detectObjects(path)
                    caras = facedetector.facedetector(path)

                    if objetos:
                        print("Se detectó a una persona")                         
                            
                        if caras.size != 0:
                            print("Se detectó una cara")

                            imageservice.saveImage(newFrame, "C:/Users/user/Documents/sentImages"+ "/" + date + ".jpg")
                            #Se envía mensaje a la cola del servicio de mensajería
                            rabbitmqservice.publish(json.dumps(data), "captured-image-queue", self.mqHost)
                
                #Se actualiza el cuadro anterior con el cuadro nuevo
                previousGrayFrame = newFrameGrayScale

                #Tiempo que se espera entre capturas (en milisegundos)
                cv2.waitKey(100)

                #Se reinicia contador
                cuenta=0
