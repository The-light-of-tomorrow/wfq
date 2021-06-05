import socket
import time
import threading
import logging
from binascii import hexlify

from util.packet import PacketDecode, post_log, post_dhcp

packet_number = 0

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def get_packet(project_header, pa_size):
    global packet_number
    packet_number += 1
    project_data = "Hello, This is Liu Ming(20020090082), The Packet Number is {}.".format(packet_number)
    # string 转 bytes（字符串转字节）
    project_data = project_data.encode()
    project_data = project_data.hex().zfill(pa_size - 24)
    packet = project_header + project_data
    return packet, packet_number


def send_packet(r, sender_info, s):
    for _ in range(r):
        packet, packet_num = get_packet(sender_info.get_project_header(), sender_info.packet_size)
        addr = (sender_info.gateway, 2021)
        s.sendto(packet.encode(), addr)
        packet = PacketDecode(packet.encode())
        now_time = time.time()
        log = "[{}] [S] [Flow ID: {}] [Weight: {}] [{}:{} -> {}:{}] {}".format(
            str(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(now_time))),
            packet.flow_id, packet.weight, packet.source_ip, packet.source_port, packet.destination_ip,
            packet.destination_port, packet.data)
        logger.info(log)
        # 通知控制平面 Flow ID, 发送时间，包大小，packet_number
        post_log(sender_info.flow_id, sender_info.packet_size, packet_num, time.time(), 0)


class Sender:
    def __init__(self, w, _packet_size):
        self.address = post_dhcp('Sender')
        self.source_ip = self.address['address']
        self.gateway = self.address['gateway']
        self.prefix = self.address['prefix']
        self.weight = w
        self.flow_id = self.address['address'][-1]
        self.packet_size = _packet_size

    def get_project_header(self):
        tr_weight = hex(self.weight)[2:].zfill(8)

        if self.source_ip == '0.0.0.0':
            print("Address Pool Error!")
        # 字符串IP地址转16进制
        source_ip = hexlify(socket.inet_aton(self.source_ip))
        # 补全8位
        source_ip = str(source_ip, encoding="utf-8").zfill(8)

        # 转16进制，补全8位
        source_port = 2021
        source_port = hex(source_port)[2:].zfill(8)

        destination_ip = '172.16.2.1'
        # 字符串IP地址转16进制
        destination_ip = hexlify(socket.inet_aton(destination_ip))
        # 补全8位
        destination_ip = str(destination_ip, encoding="utf-8").zfill(8)

        destination_port = 2021
        destination_port = hex(destination_port)[2:].zfill(8)

        flow_id = hex(int(self.flow_id))[2:].zfill(8)

        # 48个16进制数字，共24个字节
        project_header = source_ip + destination_ip + source_port + destination_port + tr_weight + flow_id
        return project_header


def sender_f(sc, udp_s):
    while True:
        send_packet(rate, sc, udp_s)
        time.sleep(1)


def receiver_f(sc, udp_s):
    while True:
        data, _ = udp_s.recvfrom(1400 + 24 + 8)
        packet = PacketDecode(data)
        now_time = time.time()
        log = "[{}] [R] [Flow ID: {}] [Weight: {}] [{}:{} -> {}:{}] {}".format(
            str(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(now_time))),
            packet.flow_id, packet.weight, packet.source_ip, packet.source_port, packet.destination_ip,
            packet.destination_port, packet.data)
        logger.info(log)
        # 通知控制平面 Flow ID, 接收时间，包大小，packet_number
        post_log(packet.flow_id, sc.packet_size, packet.packet_number, now_time, 1)


if __name__ == '__main__':
    # 权重为1
    weight = 1
    # 每秒10个包
    rate = 10
    # 包大小
    packet_size = 512
    sender = Sender(weight, packet_size)

    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_socket.bind((sender.source_ip, 2021))
    # 双线程启动与同步
    thread_sender = threading.Thread(target=sender_f, args=(sender, udp_socket,))
    thread_receiver = threading.Thread(target=receiver_f, args=(sender, udp_socket,))
    thread_sender.start()
    thread_receiver.start()
    thread_sender.join()
    thread_receiver.join()
