#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018/7/23 13:58
# @Author  : xwh
# @File    : parse_xml_string.py

from xml.dom.minidom import parse
import xml.dom.minidom

xml_string = """
<domain type='kvm'>
  <name>instance-0000a97f</name>
  <uuid>6d18a67b-6659-4a4b-b1e2-7d8ff19e50e7</uuid>
  <metadata>
    <nova:instance xmlns:nova="http://openstack.org/xmlns/libvirt/nova/1.0">
      <nova:package version="13.1.4-1.el7"/>
      <nova:name>2222222222</nova:name>
      <nova:creationTime>2018-07-26 07:16:35</nova:creationTime>
      <nova:flavor name="m1.tiny">
        <nova:memory>512</nova:memory>
        <nova:disk>1</nova:disk>
        <nova:swap>0</nova:swap>
        <nova:ephemeral>0</nova:ephemeral>
        <nova:vcpus>1</nova:vcpus>
      </nova:flavor>
      <nova:owner>
        <nova:user uuid="6431c3c8e24549f3a15201c4119688c9">admin</nova:user>
        <nova:project uuid="eedfb5a39c8b4118a145ba971cbe7305">admin</nova:project>
      </nova:owner>
      <nova:root type="image" uuid="9b0d1a14-f83e-446e-af2b-c7164c22e7ab"/>
    </nova:instance>
  </metadata>
  <memory unit='KiB'>524288</memory>
  <currentMemory unit='KiB'>524288</currentMemory>
  <vcpu placement='static'>1</vcpu>
  <cputune>
    <shares>1024</shares>
  </cputune>
  <sysinfo type='smbios'>
    <system>
      <entry name='manufacturer'>Fedora Project</entry>
      <entry name='product'>OpenStack Nova</entry>
      <entry name='version'>13.1.4-1.el7</entry>
      <entry name='serial'>328fd4f0-474d-4fb9-a950-cfb619a70bd0</entry>
      <entry name='uuid'>6d18a67b-6659-4a4b-b1e2-7d8ff19e50e7</entry>
      <entry name='family'>Virtual Machine</entry>
    </system>
  </sysinfo>
  <os>
    <type arch='x86_64' machine='pc-i440fx-rhel7.0.0'>hvm</type>
    <boot dev='hd'/>
    <smbios mode='sysinfo'/>
  </os>
  <features>
    <acpi/>
    <apic/>
  </features>
  <cpu mode='host-passthrough'>
    <topology sockets='1' cores='1' threads='1'/>
  </cpu>
  <clock offset='utc'>
    <timer name='pit' tickpolicy='delay'/>
    <timer name='rtc' tickpolicy='catchup'/>
    <timer name='hpet' present='no'/>
  </clock>
  <on_poweroff>destroy</on_poweroff>
  <on_reboot>restart</on_reboot>
  <on_crash>destroy</on_crash>
  <devices>
    <emulator>/usr/libexec/qemu-kvm</emulator>
    <disk type='file' device='disk'>
      <driver name='qemu' type='qcow2' cache='none'/>
      <source file='/var/lib/nova/instances/6d18a67b-6659-4a4b-b1e2-7d8ff19e50e7/disk'/>
      <target dev='vda' bus='virtio'/>
      <address type='pci' domain='0x0000' bus='0x00' slot='0x05' function='0x0'/>
    </disk>
    <controller type='usb' index='0'>
      <address type='pci' domain='0x0000' bus='0x00' slot='0x01' function='0x2'/>
    </controller>
    <controller type='pci' index='0' model='pci-root'/>
    <interface type='bridge'>
      <mac address='fa:16:3e:d8:30:1a'/>
      <source bridge='qbrf8ae473c-69'/>
      <target dev='tapf8ae473c-69'/>
      <model type='virtio'/>
      <address type='pci' domain='0x0000' bus='0x00' slot='0x03' function='0x0'/>
    </interface>
    <interface type='bridge'>
      <mac address='fa:16:3e:5a:b5:15'/>
      <source bridge='qbr76c36a87-96'/>
      <target dev='tap76c36a87-96'/>
      <model type='virtio'/>
      <address type='pci' domain='0x0000' bus='0x00' slot='0x04' function='0x0'/>
    </interface>
    <serial type='file'>
      <source path='/var/lib/nova/instances/6d18a67b-6659-4a4b-b1e2-7d8ff19e50e7/console.log'/>
      <target port='0'/>
    </serial>
    <serial type='pty'>
      <target port='1'/>
    </serial>
    <console type='file'>
      <source path='/var/lib/nova/instances/6d18a67b-6659-4a4b-b1e2-7d8ff19e50e7/console.log'/>
      <target type='serial' port='0'/>
    </console>
    <input type='tablet' bus='usb'>
      <address type='usb' bus='0' port='1'/>
    </input>
    <input type='mouse' bus='ps2'/>
    <input type='keyboard' bus='ps2'/>
    <graphics type='vnc' port='-1' autoport='yes' listen='192.168.100.11' keymap='en-us'>
      <listen type='address' address='192.168.100.11'/>
    </graphics>
    <video>
      <model type='cirrus' vram='16384' heads='1' primary='yes'/>
      <address type='pci' domain='0x0000' bus='0x00' slot='0x02' function='0x0'/>
    </video>
    <memballoon model='virtio'>
      <stats period='10'/>
      <address type='pci' domain='0x0000' bus='0x00' slot='0x06' function='0x0'/>
    </memballoon>
  </devices>
</domain>
"""


DOMTree = xml.dom.minidom.parseString(xml_string)

collection = DOMTree.documentElement

# print collection.getElementsByTagName("name")[0].firstChild.data
# print collection.getElementsByTagName("interface")[0].getElementsByTagName("target")[0].getAttribute("dev")
# print collection.getElementsByTagName("nova:name")[0].firstChild.data
# print [i.getElementsByTagName("target")[0].getAttribute("dev") for i in collection.getElementsByTagName("interface")]
# print collection.getElementsByTagName("uuid")[0].firstChild.data
# print collection.getElementsByTagName("disk")[0].getElementsByTagName("source")[0].getAttribute("file")
pass