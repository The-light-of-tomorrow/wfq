import json
import logging
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
# sender_gateway = '127.0.0.1'
receiver_address_pool = ["172.16.2.1"]
receiver_gateway = '172.16.2.254'
sender_prefix = 24
receiver_prefix = 24


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


@app.route('/log', methods=['POST'])
def log():
    flow_id = request.form.get('flow_id')
    packet_size = request.form.get('packet_size')
    packet_number = request.form.get('packet_number')
    now_time = request.form.get('now_time')
    time_type = request.form.get('time_type')
    # 把数据存下来计算数据包大小和delay之间的关系, 0代表发送方发送 1代表发送方接收 2代表接收方接收
    data = {'flow_id': flow_id, 'packet_size': packet_size, 'packet_number': packet_number, 'now_time': now_time,
            'time_type': time_type}
    #
    # 这里记得做，最后画曲线用
    #
    #
    #
    logger.info(data)
    result = {'code': 200}
    return json.dumps(result, ensure_ascii=False)


if __name__ == '__main__':
    app.secret_key = '123456'
    app.run(port=80, host='127.0.0.1', debug=True)
