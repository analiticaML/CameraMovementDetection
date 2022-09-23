#Se importan librerías
from imageService import ImageService
from cameraService import CameraService
from rabbitmqService import RabbitmqService
import json
import cv2
import datetime

import time

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
        #cameraservice2 = CameraService()
        #Se establece conexión del streaming
        cameraservice.openCamera(944, 1080, "rtsp://192.168.1.16:554/live1s1.sdp")
        #cameraservice2.openCamera(640, 480, "rtsp://admin:admin@192.168.1.101:1935")
        #Se obtiene la imagen actual en escala de grises
        previousGrayFrame = cameraservice.getGrayScaleFrame(cameraservice.getFrame())
        #previousGrayFrame2 = cameraservice2.getGrayScaleFrame(cameraservice2.getFrame())

        #Se esteblece un contador para disminuir el número de imágenes a las cuales
        #se les hace el análisis. 
        cuenta=0

        #Ciclo infinito para la captura de cuadros
        while (True):
            try:

                #Nuevo cuadro
                newFrame = cameraservice.getFrame()
                #newFrame2 = cameraservice2.getFrame()
                cuenta = cuenta + 1

                #Se salta el análisis de 5 imágenes
                if (cuenta > 50):

                    #Cambia  a escala de grises el nuevo cuadro
                    newFrameGrayScale = cameraservice.getGrayScaleFrame(newFrame)
                    #newFrameGrayScale2 = cameraservice2.getGrayScaleFrame(newFrame2)

                    #Se llama a método para detectar movimiento
                    if (cameraservice.detectMovement(previousGrayFrame, newFrameGrayScale, 50000)):
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
                        #Se envía mensaje a la cola del servicio de mensajería
                        rabbitmqservice.publish(json.dumps(data), "captured-image-queue", self.mqHost)


                    
                    #Se llama a método para detectar movimiento
                    # if (cameraservice2.detectMovement(previousGrayFrame2, newFrameGrayScale2, 5000)):
                    #     print("Motion detected camera2!!!")

                    #     Se guarda la fecha de hoy y se convierte a string 
                    #     now = datetime.datetime.now()
                    #     date=str(now.year)+str(now.month)+str(now.day)+str(now.hour)+str(now.minute)+str(now.second)+str(now.microsecond)
                    #     Se gurda la imagen el directorio local con nombre de la imagen como la fecha y hora de la captura
                    #     path = self.path + "/" + date + "cam2"+".jpg"
                    #     data = {}
                    #     data["path"] = path
                    #     print("Data: " + str(data["path"]))
                    #     imageservice.saveImage(newFrame2, path)

                    #     Se crea objeto tipo Rabbitmq
                    #     rabbitmqservice=RabbitmqService()
                    #     Se envía mensaje a la cola del servicio de mensajería
                    #     rabbitmqservice.publish(json.dumps(data), "captured-image-queue", self.mqHost)
                        
                    #     Se actualiza el cuadro anterior con el cuadro nuevo
                    #     previousGrayFrame2 = newFrameGrayScale2

                    #Se reinicia contador
                    cuenta=0
                    #Se actualiza el cuadro anterior con el cuadro nuevo
                    previousGrayFrame = newFrameGrayScale
            except:
                cameraservice.openCamera(944, 1080, "rtsp://192.168.1.16:554/live1s1.sdp")
                #cameraservice2.openCamera(640, 480, "rtsp://admin:admin@192.168.1.101:1935")
                #Se obtiene la imagen actual en escala de grises
                cuenta=0

                    
