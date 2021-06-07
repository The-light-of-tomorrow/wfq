import binascii
import requests
import json

control_plane_ip = '127.0.0.1'


def post_dhcp(role):
    url = "http://{}/dhcp".format(control_plane_ip)
    data = {'role': role}
    res = requests.post(url=url, data=data)
    return json.loads(res.text)


def post_log(flow_id, p_size, packet_num, now_time, time_type):
    url = "http://{}/log/host".format(control_plane_ip)
    # time_type 0代表发送时上报，1代表接收时上报
    data = {"flow_id": flow_id, "packet_size": p_size, "packet_number": packet_num, "now_time": now_time,
            "time_type": time_type}
    try:
        res = requests.post(url=url, data=data)
        return res.status_code
    except requests.exceptions.ConnectionError as e:
        return e


def get_setting():
    url = "http://{}/setting/get".format(control_plane_ip)
    data = dict()
    res = requests.post(url=url, data=data)
    return json.loads(res.text)


def hex_to_str(s):
    s = binascii.unhexlify(s)
    return s.decode('utf-8')


def hex2dec(s):
    return int(s, 16)


def router_post(time_t, round_number_t, active_queue_number):
    data = {'time_t': time_t, 'round_number_t': round_number_t, 'active_queue_number': active_queue_number}
    url = "http://{}/log/router".format(control_plane_ip)
    try:
        res = requests.post(url=url, data=data)
        return res.status_code
    except requests.exceptions.ConnectionError as e:
        return e


def ip_hex2dec(s):
    return str(hex2dec(s[0:2])) + '.' + str(hex2dec(s[2:4])) + '.' + str(hex2dec(s[4:6])) + '.' + str(hex2dec(s[6:8]))


class PacketDecode:
    def __init__(self, packet):
        packet = packet.decode()
        self.source_ip = ip_hex2dec(packet[:8])
        self.destination_ip = ip_hex2dec(packet[8:16])
        self.source_port = hex2dec(packet[16:24])
        self.destination_port = hex2dec(packet[24:32])
        self.weight = hex2dec(packet[32:40])
        self.flow_id = hex2dec(packet[40:48])
        self.data = hex_to_str(packet[48:])
        self.packet_number = self.data.split()[-1].split('.')[0]


def packet_encode_exchange_source_dest(packet):
    packet = packet.decode()
    temp = packet[8:16] + packet[:8] + packet[24:32] + packet[16:24] + packet[32:40] + packet[40:48] + packet[48:]
    packet = temp.encode()
    return packet
