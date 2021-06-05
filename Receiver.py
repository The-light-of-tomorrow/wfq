import logging
import socket
import time

from util.packet import PacketDecode, post_log, post_dhcp, packet_encode_exchange_source_dest

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class Receiver:
    def __init__(self):
        self.ip = post_dhcp('Receiver')
        self.address = self.ip['address']
        self.gateway = self.ip['gateway']
        self.prefix = self.ip['prefix']


if __name__ == '__main__':
    receiver = Receiver()
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    # 对于接收端，这里的地址应该通过DHCP服务器获取
    s.bind((receiver.address, 2021))

    while True:
        data, _ = s.recvfrom(1400 + 24 + 8)
        packet = PacketDecode(data)
        now_time = time.time()
        log = "[{}] [R] [Flow ID: {}] [Weight: {}] [{}:{} -> {}:{}] {}".format(
            time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(now_time)),
            packet.flow_id, packet.weight, packet.source_ip, packet.source_port, packet.destination_ip,
            packet.destination_port, packet.data)
        logger.info(log)
        # 通知控制平面 Flow ID, 接收时间，包大小，packet_number
        post_log(packet.flow_id, len(data) - 24, packet.packet_number, now_time, 2)
        # 对于接收端，这里应该替换成网关地址 172.16.2.254
        s.sendto(packet_encode_exchange_source_dest(data), (receiver.gateway, 2021))
