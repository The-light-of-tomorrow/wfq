import json
import logging
import time

from flask import Flask, request, render_template
import os

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
cur_dir = os.path.dirname(os.path.abspath(__file__))
if cur_dir.find('\\') != -1:
    cur_dir = cur_dir.replace('\\', '/')
dir_static = cur_dir + '/static'
dir_templates = cur_dir + '/templates'

app = Flask(__name__,
            template_folder=dir_templates,
            static_folder=dir_static,
            static_url_path='')

sender_address_pool = ['172.16.1.1', '172.16.1.2', '172.16.1.3']
sender_gateway = '172.16.1.254'
receiver_address_pool = ["172.16.2.1"]
receiver_gateway = '172.16.2.254'
sender_prefix = 24
receiver_prefix = 24

sender_data = {'1': [], '2': [], '3': []}
# 这三个数据做成图
receiver_data = {'1': [[1, 2], [2, 3]], '2': [[1, 2], [2, 3]], '3': [[1, 2], [2, 3]]}
# receiver_data = {'1': [], '2': [], '3': []}
sender_data_result = []
router_data = []


class Setting:
    def __init__(self):
        self.forwarding_algorithm = 'WFQ'  # FIFO WFQ
        self.RouteRate = '20Mbps'
        self.Receiver = '172.16.2.1'
        self.Sender = {'172.16.1.1': [1, 512], '172.16.1.2': [1, 1024], '172.16.1.3': [1, 1024]}


user_setting = Setting()


@app.route('/data/receiver_data')
def data_receiver_data():
    # receiver_data = {'1': [时间，包大小], '2': [], '3': []}
    # 需要把数据处理成 {'1': [时间四舍五入为0.1秒颗粒度，包大小累计], '2': [], '3': []}
    receiver_data_temp = receiver_data
    temp = {'1': [], '2': [], '3': []}
    sum1 = 0
    # 最多取后五十个数据，采集简化
    for i in receiver_data_temp['1'][-50:]:
        sum1 = int(i[1]) + sum1
        temp['1'].append([str(round(float(i[0]), 1)), str(sum1)])
    sum2 = 0
    for i in receiver_data_temp['2'][-50:]:
        sum2 = int(i[1]) + sum2
        temp['2'].append([str(round(float(i[0]), 1)), str(sum2)])
    sum3 = 0
    for i in receiver_data_temp['3'][-50:]:
        sum3 = int(i[1]) + sum3
        temp['3'].append([str(round(float(i[0]), 1)), str(sum3)])
    time_line = []
    flow_id_1 = []
    flow_id_2 = []
    flow_id_3 = []
    for i in temp['1']:
        time_line.append(i[0])
        flow_id_1.append(i[1])
    for i in temp['2']:
        flow_id_2.append(i[1])
    for i in temp['3']:
        flow_id_3.append(i[1])
    # 考虑把时间转换成人类可读
    result = {'time_line': [], 'flow_id_1': flow_id_1, 'flow_id_2': flow_id_2, 'flow_id_3': flow_id_3}
    return result


@app.route('/data/sender_demo')
def sender_demo():
    return {
        "time_line": ['0s', '2s', '4s', '6s', '8s', '10s', '12s'],
        "flow_id_1": [0, 1, 4, 0, 230, 210],
        "flow_id_2": [0, 2, 5, 0, 0, 330, 310],
        "flow_id_3": [0, 3, 6, 154, 190, 330, 410]
    }


@app.route('/data/receiver_demo')
def receiver_demo():
    return {
        "time_line": ['0s', '2s', '4s', '6s', '8s', '10s', '12s'],
        "flow_id_1": [0, 101, 134, 0, 230, 210],
        "flow_id_2": [0, 0, 191, 0, 0, 330, 310],
        "flow_id_3": [0, 232, 201, 154, 190, 330, 410]
    }


@app.route('/data/sender_data_result')
def data_sender_data_result():
    # 返回最近50个延迟
    a = dict()
    a['Result'] = sender_data_result
    return a


@app.route('/data/router_data')
def data_router_data():
    a = dict()
    a['Result'] = router_data
    return a


@app.route('/')
def index():
    return render_template("index.html")


@app.route('/dhcp', methods=['POST'])
def dhcp():
    role = request.form.get('role')
    prefix = 24
    address = '0.0.0.0'
    gateway = '0.0.0.0'
    if role == 'Sender':
        if len(sender_address_pool) != 0:
            address = sender_address_pool.pop()
        prefix = sender_prefix
        gateway = sender_gateway
    elif role == 'Receiver':
        if len(receiver_address_pool) != 0:
            address = receiver_address_pool.pop()
        prefix = receiver_prefix
        gateway = receiver_gateway
    result = {'address': address, 'prefix': prefix, 'gateway': gateway}
    return json.dumps(result, ensure_ascii=False)


@app.route('/setting/set', methods=['POST'])
def setting_set():
    # 写入设置
    #
    #
    #
    #
    #
    #
    result = {'code': 200}
    return json.dumps(result, ensure_ascii=False)


@app.route('/setting/get', methods=['POST'])
def setting_get():
    # 读取设置
    result = {'forwarding_algorithm': user_setting.forwarding_algorithm, 'Sender': user_setting.Sender}
    return json.dumps(result, ensure_ascii=False)


@app.route('/log/host', methods=['POST'])
def log():
    flow_id = request.form.get('flow_id')
    packet_size = request.form.get('packet_size')
    packet_number = request.form.get('packet_number')
    now_time = request.form.get('now_time')
    time_type = request.form.get('time_type')
    # 把数据存下来计算数据包大小和delay之间的关系, 0代表发送方发送 1代表发送方接收 2代表接收方接收
    data = {'flow_id': flow_id, 'packet_size': packet_size, 'packet_number': packet_number, 'now_time': now_time,
            'time_type': time_type}
    # 0代表 Sender 发送时上报，1代表 Sender 接收时上报，2代表 Receiver 接收时发送
    # 分类写数据进入一个数据结构，让页面读取
    if data['time_type'] == '0':
        _now_time = data['now_time']
        _flow_id = data['flow_id']
        _packet_size = data['packet_size']
        _packet_number = data['packet_number']
        _temp = [_packet_number, _now_time, _packet_size]
        sender_data[_flow_id].append(_temp)
    elif data['time_type'] == '1':
        _now_time = data['now_time']
        _flow_id = data['flow_id']
        _packet_size = data['packet_size']
        _packet_number = data['packet_number']
        sender_data_temp = sender_data
        for i in sender_data_temp[_flow_id]:
            if i[0] == _packet_number:
                send_time = i[1]
                break
        temp = [float(_now_time) - float(send_time), _flow_id, _packet_size]
        sender_data_result.append(temp)
    elif data['time_type'] == '2':
        _now_time = data['now_time']
        _flow_id = data['flow_id']
        _packet_size = data['packet_size']
        _temp = [_now_time, _packet_size]
        receiver_data[_flow_id].append(_temp)
    logger.info(data)
    result = {'code': 200}
    return json.dumps(result, ensure_ascii=False)


@app.route('/log/router', methods=['POST'])
def router():
    # 统计Router的t,R(t),Acitve Queue Number
    time_t = request.form.get('time_t')
    round_number_t = request.form.get('round_number_t')
    active_queue_number = request.form.get('active_queue_number')
    # 将这些数据存入数组，等待网页读取
    router_data.append([time_t, round_number_t, active_queue_number])
    msg = "Time: {}, Round Number: {}, Active Queue Number: {}.".format(time_t, round_number_t, active_queue_number)
    logger.info(msg)
    # print(time_t, round_number_t, active_queue_number)
    result = {'code': 200}
    return json.dumps(result, ensure_ascii=False)


if __name__ == '__main__':
    app.secret_key = '20020090082 Liu Ming'
    app.run(port=80, host='0.0.0.0', debug=True)
