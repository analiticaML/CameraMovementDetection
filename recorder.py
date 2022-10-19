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
        #cameraservice2 = CameraService()
        #cameraservice3 = CameraService()

        #Se establece conexión del streaming
        cameraservice.openCamera(800, 1080, "rtsp://192.168.1.16:554/live1s1.sdp")
        #cameraservice2.openCamera(640, 480, "rtsp://admin:admin@192.168.1.101:1935")
        #cameraservice3.openCamera(640, 480, "rtsp://admin:admin@192.168.1.8:1935")

        #Se obtiene la imagen actual en escala de grises
        previousGrayFrame = cameraservice.getGrayScaleFrame(cameraservice.getFrame())
        #previousGrayFrame2 = cameraservice2.getGrayScaleFrame(cameraservice2.getFrame())
        #previousGrayFrame3 = cameraservice3.getGrayScaleFrame(cameraservice3.getFrame())

        #Se esteblece un contador para disminuir el número de imágenes a las cuales
        #se les hace el análisis. 
        cuenta=0

        facedetector = FaceDetector()
        #persondetector = PersonDetector()


        #Se crea objeto tipo Rabbitmq
        rabbitmqservice=RabbitmqService()

        #Ciclo infinito para la captura de cuadros
        while (True):
            try:
                #Nuevo cuadro
                newFrame = cameraservice.getFrame()
                #newFrame2 = cameraservice2.getFrame()
                #newFrame3 = cameraservice3.getFrame()
                cuenta = cuenta + 1

                #Se salta el análisis de 5 imágenes
                if (cuenta > 30):

                    #Cambia  a escala de grises el nuevo cuadro
                    newFrameGrayScale = cameraservice.getGrayScaleFrame(newFrame)
                    #newFrameGrayScale2 = cameraservice2.getGrayScaleFrame(newFrame2)
                    #newFrameGrayScale3 = cameraservice3.getGrayScaleFrame(newFrame3)

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



                        #objetos= persondetector.detectObjects(path)
                        caras = facedetector.facedetector(path)

                        # if 0 in objetos:
                        #     print("Se detectó a una persona en la camara 1")                         
                                
                        if caras.size != 0:
                            print("Se detectó una cara")

                            imageservice.saveImage(newFrame, "/home/analitica2/Documentos/RecuadrosPersonas"+ "/" + date + ".jpg")
                            #Se envía mensaje a la cola del servicio de mensajería
                            rabbitmqservice.publish(json.dumps(data), "captured-image-queue", self.mqHost)
                
                        #Se llama a método para detectar movimiento
                    # if (cameraservice2.detectMovement(previousGrayFrame2, newFrameGrayScale2, 50000)):
                    #     print("Motion detected camera2!!!")

                    #     #Se guarda la fecha de hoy y se convierte a string 
                    #     now = datetime.datetime.now()
                    #     date=str(now.year)+str(now.month)+str(now.day)+str(now.hour)+str(now.minute)+str(now.second)+str(now.microsecond)
                    #     #Se gurda la imagen el directorio local con nombre de la imagen como la fecha y hora de la captura
                    #     path = self.path + "/" + date + "cam2"+".jpg"
                    #     data = {}
                    #     data["path"] = path
                    #     print("Data: " + str(data["path"]))
                    #     imageservice.saveImage(newFrame2, path)


                        # objetos= persondetector.detectObjects(path)
                        # caras = facedetector.facedetector(path)
                        
                        # if 0 in objetos:
                        #     print("Se detectó a una persona en la camara 2")                         
                                
                        #     if caras.size != 0:
                        #         print("Se detectó una cara")

                        #imageservice.saveImage(newFrame2, "/home/analitica2/Documentos/RecuadrosPersonas"+ "/" + date + ".jpg")
                        #         #Se envía mensaje a la cola del servicio de mensajería
                        #rabbitmqservice.publish(json.dumps(data), "captured-image-queue", self.mqHost)
                        
                    #Se llama a método para detectar movimiento
                    # if (cameraservice.detectMovement(previousGrayFrame3, newFrameGrayScale3, 50000)):
                    #     print("Motion detected!!!")

                    #     #Se guarda la fecha de hoy y se convierte a string 
                    #     now = datetime.datetime.now()
                    #     date=str(now.year)+str(now.month)+str(now.day)+str(now.hour)+str(now.minute)+str(now.second)+str(now.microsecond)
                    #     #Se gurda la imagen el directorio local con nombre de la imagen como la fecha y hora de la captura
                    #     path = self.path + "/" + date +'cam3'+ ".jpg"
                    #     data = {}
                    #     data["path"] = path
                    #     print("Data: " + str(data["path"]))
                    #     imageservice.saveImage(newFrame3, path)


                        #objetos= persondetector.detectObjects(path)
                        #caras = facedetector.facedetector(path)

                        # if 0 in objetos:
                        #     print("Se detectó a una persona en la camara 3")                         
                                
                        #     if caras.size != 0:
                        #         print("Se detectó una cara")

                        #         imageservice.saveImage(newFrame3, "/home/analitica2/Documentos/RecuadrosPersonas"+ "/" + date + ".jpg")
                        #         #Se envía mensaje a la cola del servicio de mensajería
                        #rabbitmqservice.publish(json.dumps(data), "captured-image-queue", self.mqHost)
                    
                    #Se actualiza el cuadro anterior con el cuadro nuevo
                    #previousGrayFrame2 = newFrameGrayScale2
                    #Se actualiza el cuadro anterior con el cuadro nuevo
                    previousGrayFrame = newFrameGrayScale
                    #Se actualiza el cuadro anterior con el cuadro nuevo
                    #previousGrayFrame3 = newFrameGrayScale3

                    #Se reinicia contador
                    cuenta=0
            except:
                cameraservice.openCamera(800, 1080, "rtsp://192.168.1.16:554/live1s1.sdp")
                
                #cameraservice.openCamera(640, 480, "rtsp://admin:admin@192.168.1.101:1935")
                #cuenta=0