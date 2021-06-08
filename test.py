import socket
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
# 对于接收端，这里的地址应该通过DHCP服务器获取
s.bind(('127.0.0.1', 2022))