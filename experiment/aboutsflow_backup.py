#! /usr/bin/env python
# -*- coding: utf-8 -*-

# @company: heetian
# @file: aboutsflow_backup.py
# @time: 2017/11/13 0013 下午 4:44
# @author: xwh
# @desc: sflow v5  ipv4

import multiprocessing as mp
import threading as th
from kafka import KafkaProducer
import time
import json
import socket
import binascii


DEFAULT_PORT = 6343


aging_dict = dict()
aging_time = 5


def agingThead():
    while True:
        if aging_dict["time"] > time.time() + aging_time:
            send_to_kafka()
            aging_dict.clear()
            aging_dict["time"] = time.time()
        else:
            time.sleep(0.1)


def send_to_kafka():
    pass


def hex2dec(hex_char):
    return int(hex_char, 16)


def str2ip(hex_ip):
    return "%d.%d.%d.%d" % (hex2dec(hex_ip[0:2]), hex2dec(hex_ip[2:4]),
                            hex2dec(hex_ip[4:6]), hex2dec(hex_ip[6:8]))


def str2mac(hex_mac):
    return "%s:%s:%s:%s:%s:%s:%s" % (
        hex_mac[0:2], hex_mac[2:4], hex_mac[4:6], hex_mac[6:8], hex_mac[8:10], hex_mac[10:12], hex_mac[12:14])


def getGram(socket_object):
    data, addr = socket_object.recvfrom(3000)
    gram = binascii.hexlify(data)
    # 过滤非sflow v5报文   过滤非FLOW 报文  略去sflow header
    # return gram
    if gram[7] == "5":
        return gram


def IPgetLength(ip_record):
    pass


def ICMPgetLength(icmp_record):
    pass


def sflowHeader(gram):
    head_info = dict()
    head = gram[0:56]
    flow_cnt = int(gram[48:56], 16)
    head_info["sflow_version"] = gram[0:8]
    head_info["agent_address_type"] = gram[8:16]
    head_info["agent_address"] = gram[16:24]
    head_info["sub_agent_id"] = gram[24:32]
    head_info["sequence_number"] = gram[32:40]
    head_info["sysup_time"] = gram[40:48]
    head_info["num_samples"] = gram[48:56]

    return head, flow_cnt, head_info


def sflowBody(gram):
    body = gram[56:-1]
    return body


def splitBody(body, time):
    sflow_body = body
    counter_len = 328
    # flow 采样去掉raw packet header之后长度为144(实际136, flag等于60 该部分长度却是68 flag为80 该部分长度88 多出8个长度 很奇怪)
    base_length = 144
    flow_record_list = list()
    for i in xrange(time):
        if sflow_body[7] is "2":
            sflow_body = sflow_body[counter_len:-1]
            continue
        if sflow_body[7] is "1":
            length_flag = int(sflow_body[136:144], 16)
            flow_len = base_length + length_flag * 2
            flow_record_list.append(sflow_body[0:flow_len])
            sflow_body = sflow_body[flow_len:-1]
    return flow_record_list


ether_type_dict = {
    "0x0600": "XEROX",
    "0x0660": "DLOG",
    "0x0661": "DLOG",
    "0x0800": "IPv4",
    "0x0801": "X.75",
    "0x0802": "NBS",
    "0x0803": "ECMA",
    "0x0804": "Chaosnet ",
    "0x0805": "X.25",
    "0x0806": "ARP",
    "0x0808": "Frame_Relay_ARP",
    "0x6559": "Raw_Frame_Relay",
    "0x8035": "Reverse_Address_Resolution_Protocol",
    "0x8037": "Novell_Netware_IPX",
    "0x809B": "EtherTalk",
    "0x80D5": "IBM_SNA_Services",
    "0x80F3": "AppleTalk",
    "0x8100": "EAPS",
    "0x8137": "IPX",
    "0x814C": "SNMP",
    "0x86DD": "IPv6",
    "0x880B": "PPP",
    "0x880C": "GSMP",
    "0x8847": "MPLS",
    "0x8848": "MPLS",
    "0x8863": "PPPoE",
    "0x8864": "PPPoE",
    "0x88BB": "LWAPP",
    "0x88CC": "LLDP",
    "0x8E88": "EAPOL",
    "0x9000": "Loopback",
    "0x9100": "VLAN_Tag_Protocol_Identifier",
    "0x9200": "VLAN_Tag_Protocol_Identifier"
}


def getEtherType(info_dict):
    return ether_type_dict[info_dict["ethe_type"]]


def getInfoFromRecord(record):
    info = dict()
    '''
    Ethertype ( 十六进制 )   协议   
    0x0000 - 0x05DC   IEEE 802.3 长度   
    0x0101 – 0x01FF   实验   
    0x0600   XEROX NS IDP   
    0x0660   DLOG
    0x0661   DLOG
    0x0800   网际协议（IP）   
    0x0801   X.75 Internet   
    0x0802   NBS Internet   
    0x0803   ECMA Internet   
    0x0804   Chaosnet   
    0x0805   X.25 Level 3   
    0x0806   地址解析协议（ARP ： Address Resolution Protocol）   
    0x0808   帧中继 ARP （Frame Relay ARP） [RFC1701]   
    0x6559   原始帧中继（Raw Frame Relay） [RFC1701]   
    0x8035   动态 DARP （DRARP：Dynamic RARP） 反向地址解析协议（RARP：Reverse Address Resolution Protocol）   
    0x8037   Novell Netware IPX   
    0x809B   EtherTalk   
    0x80D5   IBM SNA Services over Ethernet   
    0x80F3   AppleTalk 地址解析协议（AARP：AppleTalk Address Resolution Protocol）
    0x8100   以太网自动保护开关（EAPS：Ethernet Automatic Protection Switching）   
    0x8137   因特网包交换（IPX：Internet Packet Exchange）   
    0x814C   简单网络管理协议（SNMP：Simple Network Management Protocol）
    0x86DD   网际协议v6 （IPv6，Internet Protocol version 6）   
    0x880B   点对点协议（PPP：Point-to-Point Protocol）   
    0x880C   通用交换管理协议（GSMP：General Switch Management Protocol）
    0x8847   多协议标签交换（单播） MPLS：Multi-Protocol Label Switching <unicast>）   
    0x8848   多协议标签交换（组播）（MPLS, Multi-Protocol Label Switching <multicast>）   
    0x8863   以太网上的 PPP（发现阶段）（PPPoE：PPP Over Ethernet <Discovery Stage>）   
    0x8864   以太网上的 PPP（PPP 会话阶段） （PPPoE，PPP Over Ethernet<PPP Session Stage>）   
    0x88BB   轻量级访问点协议（LWAPP：Light Weight Access Point Protocol）   
    0x88CC   链接层发现协议（LLDP：Link Layer Discovery Protocol）   
    0x8E88   局域网上的 EAP（EAPOL：EAP over LAN）   
    0x9000   配置测试协议（Loopback）   
    0x9100   VLAN 标签协议标识符（VLAN Tag Protocol Identifier）   
    0x9200   VLAN 标签协议标识符（VLAN Tag Protocol Identifier）
    '''

    info["sample_length"] = record[8:16]
    info["sequence_number"] = record[16:24]
    info["source_id_class_index"] = record[24:32]
    info["sampling_rate"] = record[32:40]
    info["sampling_pool"] = record[40:48]
    info["drop_packets"] = record[48:56]
    info["input_interface"] = record[56:64]
    info["multiple_outputs"] = record[64:72]
    info["flow_record"] = record[72:80]
    info["switch_format"] = record[80:88]
    info["flow_data_length"] = record[88:96]
    info["incoming_802.1Q_VLAN"] = record[96:104]
    info["incoming_802.1P_priority"] = record[104:112]
    info["outgoing_802.1Q_VLAN"] = record[112:120]
    info["outgoing_802.1Q_priority"] = record[120:128]
    info["standard_sflow"] = record[128:136]
    info["raw_flow_data_length"] = record[136:144]
    info["header_protocol"] = record[144:152]
    info["frame_length"] = record[152:160]
    info["payload_removed"] = record[160:168]
    info["original_packet_length"] = record[168:176]
    info["ethe_dst_mac"] = record[176:188]
    info["ethe_src_mac"] = record[188:200]
    info["ethe_type"] = record[200:204]

    return info


def ARPInfo(record, info_dict):
    arp_header = record[-56:]
    info_dict["sender_mac"] = arp_header[16:28]
    info_dict["sender_ip"] = arp_header[28:36]
    info_dict["target_mac"] = arp_header[36:48]
    info_dict["target_ip"] = arp_header[48:56]
    info_dict["arp_length"] = 28
    return info_dict


def IPv4Info(record, info_dict):
    ipv4_header = record[204:244]
    info_dict[""]

def mainTask():
    pass


if __name__ == '__main__':
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(("0.0.0.0", DEFAULT_PORT))
    while True:
        gram = getGram(sock)
        try:
            head, cnt, head_info = sflowHeader(gram)
            body = sflowBody(gram)
            record_list =  splitBody(body, cnt)
            if record_list.__len__() == 0:
                continue
            for each in record_list:
                info = getInfoFromRecord(each)
                if getEtherType(info) == "IPv4":
                    pass
                if getEtherType(info) == "IPv6":
                    pass
        except KeyError:
            continue
