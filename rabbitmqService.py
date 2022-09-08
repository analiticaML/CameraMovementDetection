import pika

class RabbitmqService:

    #Constructor (Es vacío, pero como Python exige tener algo en el cuerpose pone a=1)
    def __init__(self):
        a=1

    #método para públicar
    def publish(self,message, queue, mqHost):

        #Se establece conexión con el servidor
        connection = pika.BlockingConnection(pika.ConnectionParameters(mqHost))

        #Se comienza el canal de comunicación
        channel = connection.channel()

        #Se establece la cola
        channel.queue_declare(queue, passive=False, durable=False, exclusive=False, auto_delete=False, arguments=None)

        #Se envía mensaje
        channel.basic_publish("", queue, bytes(message, 'utf-8'), properties=None, mandatory=False)
        print(" [x] Sent %r" % message)

        #Se cierra la conexión
        connection.close()


