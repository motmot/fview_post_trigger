# This example will trigger the plugin to record a movie.
import socket

host = ''
port = 30041
sender = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sender.sendto('x',(host,port))
