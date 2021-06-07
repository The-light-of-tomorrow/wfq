import socket
import threading
import queue
import time
import logging
from util.packet import PacketDecode, get_setting, router_post

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

lock = threading.Lock()
lock1 = threading.Lock()
lock2 = threading.Lock()
lock3 = threading.Lock()

q = queue.Queue(3000)
q1 = queue.Queue(1000)
q2 = queue.Queue(1000)
q3 = queue.Queue(1000)

setting = get_setting()
q1_w = int(setting['Sender']['172.16.1.1'][0])
q2_w = int(setting['Sender']['172.16.1.2'][0])
q3_w = int(setting['Sender']['172.16.1.3'][0])

# 带宽20Mbps，令牌桶最大20480
token = 20480
token_lock = threading.Lock()
# Round Number 在 t 时刻的数值
R_t = 0
R_t_lock = threading.Lock()
# 在 t 时刻检查的队列活跃情况
N_ac_t = 3
N_ac_t_lock = threading.Lock()
# 时刻 t
time_t = 0
time_t_lock = threading.Lock()
# Finish Number
F_t = 0
F_t_lock = threading.Lock()
# 三个队列的最大 Finish Number
q1_f = 0
q2_f = 0
q3_f = 0


def token_bucket():
    logger.info("Token Bucket is Running!")
    global token
    global token_lock
    while True:
        token_lock.acquire()
        token += 2048
        if token > 20480:
            token = 20480
        token_lock.release()
        # sleep 100ms
        time.sleep(0.1)


def router_in(s):
    logger.info("Router In is Running!")
    global q, lock
    while True:
        data, _ = s.recvfrom(1400 + 24 + 8)
        # 先要获取锁:
        lock.acquire()
        try:
            # 写数据
            q.put(data)
        finally:
            # 写完队列一定要释放锁（有点多余，Python 多线程队列已经原生处理了互斥的问题，这里使用这个方式为了体现互斥的原理）
            # from multiprocessing import Queue 每次访问multiprocessing.Queue都会加锁
            lock.release()


def router_out(net1, net2):
    logger.info("Router Out is Running!")
    global token, token_lock, q, R_t
    while True:
        if not q.empty():
            data = q.get()
            packet = PacketDecode(data)
            while token < len(packet.data):
                # 如果令牌桶不够了，等待50ms
                time.sleep(0.05)
            token_lock.acquire()
            token -= len(data)
            token_lock.release()
            # 根据 destination ip 实现路由下一条匹配算法，最长前缀匹配原则
            if packet.destination_ip[:8] == '172.16.2':
                net_hop = net2
            elif packet.destination_ip[:8] == '172.16.1':
                net_hop = net1
            else:
                net_hop = -1
            net_hop.sendto(data, (packet.destination_ip, 2021))

            # 转发一个数据包更新一个 Round Number
            R_t_lock.acquire()
            R_t += len(packet.data)
            R_t_lock.release()

            now_time = time.time()
            log = "[{}] [Router] [Flow ID: {}] [Weight: {}] [{}:{} -> {}:{}] {}".format(
                time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(now_time)),
                packet.flow_id, packet.weight, packet.source_ip, packet.source_port, packet.destination_ip,
                packet.destination_port, packet.data)
            logger.info(log)


def wfq_number_computation_and_post():
    logger.info("wfq_number_computation_and_post is Running!")
    global R_t, token, N_ac_t, time_t, q1_f, q2_f, q3_f, R_t_lock, time_t_lock
    while True:
        R_t_temp = R_t
        L = token
        N = N_ac_t
        # 简化算法，每次检查N都从3检查到1
        for i in range(3):
            F = min(q1_f, q2_f, q3_f)
            # 时间间隔简化处理，设置为1秒
            D = 1
            if N == 0:
                continue
            else:
                if F <= R_t_temp + D * L / N:
                    R_t_temp = F
                    N = N - 1
                else:
                    R_t_temp = R_t_temp + D * L / N
        post_r_t = R_t_temp
        post_n_ac_t = N
        post_time_t = time_t
        router_post(post_time_t, post_r_t, post_n_ac_t)
        # 计算新的数值，加锁写入全局变量
        time_t_lock.acquire()
        time_t += 1
        time_t_lock.release()
        R_t_lock.acquire()
        R_t = R_t_temp
        R_t_lock.release()
        # # 读取队列数量
        # print(q1.qsize(), q2.qsize(), q3.qsize())
        time.sleep(1)


def wfq_scheduler():
    logger.info("wfq_scheduler is Running!")
    global q1, q2, q3
    forward_data = {'q1': None, 'q2': None, 'q3': None}
    forward_fn = {'q1': -1, 'q2': -1, 'q3': -1}
    while True:
        # 同时读取三个队列，比较三个队列的 非空 Finish Number，最小的转发，设置为None，再读再比对，没出去的放到缓存，下次不读。
        if forward_data['q1'] is None:
            if not q1.empty():
                temp = q1.get()
                temp = str(temp).split(',')
                forward_data['q1'] = temp[0]
                forward_fn['q1'] = int(float(temp[1]))
        if forward_data['q2'] is None:
            if not q2.empty():
                temp = q2.get()
                temp = str(temp).split(',')
                forward_data['q2'] = temp[0]
                forward_fn['q2'] = int(float(temp[1]))
        if forward_data['q3'] is None:
            if not q3.empty():
                temp = q3.get()
                temp = str(temp).split(',')
                forward_data['q3'] = temp[0]
                forward_fn['q3'] = int(float(temp[1]))
        forward_fn_temp = sorted(forward_fn.items(), key=lambda asd: asd[1], reverse=False)
        for i in range(len(forward_fn_temp)):
            if forward_fn_temp[i][1] > 0:
                # 转发这个数据包
                data = forward_data[forward_fn_temp[i][0]]
                data = data.encode()
                lock.acquire()
                q.put(data)
                lock.release()
                # 设置对应键值为 None 和 -1
                forward_data[forward_fn_temp[i][0]] = None
                forward_fn[forward_fn_temp[i][0]] = -1


def router_in_with_wfq(s):
    logger.info("router_in_with_wfq is Running!")
    global q1, q2, q3, lock1, lock2, lock3, q1_f, q2_f, q3_f
    while True:
        data, _ = s.recvfrom(1400 + 24 + 8)
        packet = PacketDecode(data)
        if packet.flow_id == 1:
            finish_number = max(q1_f, R_t) + len(packet.data) / q1_w
            if finish_number > q1_f:
                q1_f = finish_number
            data = data.decode() + ',' + str(finish_number)
            lock1.acquire()
            try:
                q1.put(data)
            finally:
                lock1.release()
        elif packet.flow_id == 2:
            finish_number = max(q2_f, R_t) + len(packet.data) / q2_w
            if finish_number > q2_f:
                q2_f = finish_number
            lock2.acquire()
            data = data.decode() + ',' + str(finish_number)
            try:
                q2.put(data)
            finally:
                lock2.release()
        elif packet.flow_id == 3:
            finish_number = max(q3_f, R_t) + len(packet.data) / q3_w
            if finish_number > q3_f:
                q3_f = finish_number
            data = data.decode() + ',' + str(finish_number)
            lock3.acquire()
            try:
                q3.put(data)
            finally:
                lock3.release()


if __name__ == '__main__':
    s1 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s2 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s1.bind(("172.16.1.254", 2021))
    s2.bind(("172.16.2.254", 2021))
    logger.info("forwarding_algorithm: {}".format(setting['forwarding_algorithm']))
    if setting['forwarding_algorithm'] == 'FIFO':
        t = [threading.Thread(target=router_in, args=(s1,)),
             threading.Thread(target=router_in, args=(s2,)),
             threading.Thread(target=token_bucket),
             threading.Thread(target=router_out, args=(s1, s2,))]
        for i in t:
            i.start()
        for i in t:
            i.join()
    elif setting['forwarding_algorithm'] == 'WFQ':
        t = [threading.Thread(target=router_in_with_wfq, args=(s1,)),
             threading.Thread(target=router_in_with_wfq, args=(s2,)),
             threading.Thread(target=wfq_number_computation_and_post),
             threading.Thread(target=token_bucket),
             threading.Thread(target=wfq_scheduler),
             threading.Thread(target=router_out, args=(s1, s2,))]
        for i in t:
            i.start()
        for i in t:
            i.join()
