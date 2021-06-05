import socket
import threading
import queue
import time
import logging

from util.packet import PacketDecode

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
lock = threading.Lock()

q = queue.Queue(1000)


def router_in(s):
    while True:
        data, _ = s.recvfrom(1400 + 24 + 8)
        # 先要获取锁:
        lock.acquire()
        try:
            # 写数据
            q.put(data)
        finally:
            # 写完队列一定要释放锁（有点多余，Python队列已经原生处理了互斥的问题，这里使用这个方式为了体现互斥的原理）
            lock.release()


def router_out(net1, net2):
    while True:
        while not q.empty():
            data = q.get()
            packet = PacketDecode(data)
            # 根据 destination ip 实现路由下一条匹配算法，最长前缀匹配原则
            if packet.destination_ip[:8] == '172.16.2':
                net_hop = net1
            elif packet.destination_ip[:8] == '172.16.1':
                net_hop = net2
            else:
                net_hop = -1
            net_hop.sendto(data, (packet.destination_ip, 2021))
            now_time = time.time()
            log = "[{}] [Router] [Flow ID: {}] [Weight: {}] [{}:{} -> {}:{}] {}".format(
                time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(now_time)),
                packet.flow_id, packet.weight, packet.source_ip, packet.source_port, packet.destination_ip,
                packet.destination_port, packet.data)
            logger.info(log)


if __name__ == '__main__':
    forwarding_algorithm = 'FIFO'

    s1 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s2 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s1.bind(("172.16.2.254", 2021))
    s2.bind(("172.16.1.254", 2021))

    t1 = threading.Thread(target=router_in, args=(s1,))
    t2 = threading.Thread(target=router_in, args=(s2,))
    t3 = threading.Thread(target=router_out, args=(s1, s2,))
    t1.start()
    t2.start()
    t3.start()
    t1.join()
    t2.join()
    t3.join()
