#!/usr/bin/python
import socket
import struct
import uuid
import binascii


# The sFlow Collector is a class for parsing sFlow data.

# sFlow datagrams contain a header, which may contain samples which may contain records.
#
# The datagram may not contain a sample, but if it does there will be at least on record.
#
# The records may have different formats.

# IDEA (17-06-29) Is the raw data for each block actually needed? What is the cost for preserving them?


# sFlow
#   sample
#       record

class sFlow:
    def __init__(self, dataGram):

        # sFlow Sample class.

        class Sample:
            def __init__(self, header, sampleSize, dataGram):

                # sFlow Record class.

                class Record:
                    def __init__(self, header, length, sampleType, dataGram):
                        self.header = header
                        self.enterprise = (self.header & 4294901760) / 4096
                        self.format = (self.header & 4095)
                        self.len = length
                        self.sampleType = sampleType
                        self.data = dataGram

                self.record = []
                self.data = dataGram
                SampleHeader = struct.unpack('>i', header)[0]

                self.sequence = struct.unpack('>i', dataGram[0:4])[0]
                SampleSource = struct.unpack('>i', dataGram[4:8])[0]

                self.enterprise = (SampleHeader & 4294963200) / 4096
                self.sampleType = (
                SampleHeader & 4095)  # 0 sample_data / 1 flow_data (single) / 2 counter_data (single) / 3 flow_data (expanded) / 4 counter_data (expanded)
                self.len = sampleSize

                self.sourceType = (SampleSource & 4278190080) / 16777216
                self.sourceIndex = (SampleSource & 16777215)

                dataPosition = 8

                #

                if self.sampleType == 1:  # Flow
                    self.sampleRate = struct.unpack('>i', dataGram[(dataPosition):(dataPosition + 4)])[0]
                    self.samplePool = struct.unpack('>i', dataGram[(dataPosition + 4):(dataPosition + 8)])[0]
                    self.droppedPackets = struct.unpack('>i', dataGram[(dataPosition + 8):(dataPosition + 12)])[0]
                    self.inputInterface = struct.unpack('>i', dataGram[(dataPosition + 12):(dataPosition + 16)])[0]
                    self.outputInterface = struct.unpack('>i', dataGram[(dataPosition + 16):(dataPosition + 20)])[0]
                    self.recordCount = struct.unpack('>i', dataGram[(dataPosition + 20):(dataPosition + 24)])[0]
                    dataPosition = 32

                    for i in range(self.recordCount):
                        RecordHeader = struct.unpack('>i', dataGram[(dataPosition):(dataPosition + 4)])[0]
                        RecordSize = struct.unpack('>i', dataGram[(dataPosition + 4):(dataPosition + 8)])[0]
                        RecordData = dataGram[(dataPosition + 8):(dataPosition + RecordSize + 8)]
                        self.record.append(Record(RecordHeader, RecordSize, self.sampleType, RecordData))
                        dataPosition = dataPosition + 8 + RecordSize

                elif self.sampleType == 2:  # Counters
                    self.recordCount = struct.unpack('>i', dataGram[(dataPosition):(dataPosition + 4)])[0]
                    self.sampleRate = 0
                    self.samplePool = 0
                    self.droppedPackets = 0
                    self.inputInterface = 0
                    self.outputInterface = 0
                    dataPosition = 12

                    for i in range(self.recordCount):
                        RecordHeader = struct.unpack('>i', dataGram[(dataPosition):(dataPosition + 4)])[0]
                        RecordSize = struct.unpack('>i', dataGram[(dataPosition + 4):(dataPosition + 8)])[0]
                        RecordData = dataGram[(dataPosition + 8):(dataPosition + RecordSize + 8)]
                        self.record.append(Record(RecordHeader, RecordSize, self.sampleType, RecordData))
                        dataPosition = dataPosition + 8 + RecordSize
                else:
                    self.recordCount = 0
                    self.sampleRate = 0
                    self.samplePool = 0
                    self.droppedPackets = 0
                    self.inputInterface = 0
                    self.outputInterface = 0

        # Begin sFlow

        dataPosition = 0
        self.sample = []
        self.data = dataGram
        self.dgVersion = struct.unpack('>i', dataGram[0:4])[0]
        self.addressType = struct.unpack('>i', dataGram[4:8])[0]
        self.len = len(dataGram)
        if self.addressType == 1:
            self.agentAddress = socket.inet_ntoa(dataGram[8:12])
            self.subAgent = struct.unpack('>i', dataGram[12:16])[0]
            self.sequenceNumber = struct.unpack('>i', dataGram[16:20])[0]
            self.sysUpTime = struct.unpack('>i', dataGram[20:24])[0]
            self.NumberSample = struct.unpack('>i', dataGram[24:28])[0]
            dataPosition = 28
        elif self.addressType == 2:
            self.agentAddress = binascii.hexlify(dataGram[8:24])  # Temporary fix due to lack of IPv6 support on WIN32
            self.subAgent = struct.unpack('>i', dataGram[24:28])[0]
            self.sequenceNumber = struct.unpack('>i', dataGram[28:32])[0]
            self.sysUpTime = struct.unpack('>i', dataGram[32:36])[0]
            self.NumberSample = struct.unpack('>i', dataGram[36:40])[0]
            dataPosition = 40
        else:
            self.agentAddress = 0
            self.subAgent = 0
            self.sequenceNumber = 0
            self.sysUpTime = 0
            self.NumberSample = 0
        if self.NumberSample > 0:
            for i in range(self.NumberSample):
                SampleHeader = dataGram[(dataPosition):(dataPosition + 4)]
                SampleSize = struct.unpack('>i', dataGram[(dataPosition + 4):(dataPosition + 8)])[0]
                SampleDataGram = dataGram[(dataPosition + 8):(dataPosition + SampleSize + 8)]

                self.sample.append(Sample(SampleHeader, SampleSize, SampleDataGram))
                dataPosition = dataPosition + 8 + SampleSize


# Flow
#   Raw Packet Header       1-0-1
#   Ethernet Frame          1-0-2
#   Extended Switch         1-0-1001

# Counter
#   Interface Counter       2-0-1
#   Ethernet Interface      2-0-2
#   VLAN                    2-0-5
#   Processor               2-0-1001
#   Host Description        2-0-2000
#   Host Adapaters          2-0-2001
#   Host Parent             2-0-2002
#   Host CPU                2-0-2003
#   Host Memory             2-0-2004
#   Host Disk IO            2-0-2005
#   Host Network IO         2-0-2006
#   MIB2 IP Group           2-0-2007
#   MIB2 ICMP Group         2-0-2008
#   MIB2 TCP Group          2-0-2009
#   MIB2 UDP Group          2-0-2010



# IDEA (17-03-07) Sanity check for the fixed length records could be implimented with a simple value check.

# Flow Record Types

class sFlowRawPacketHeader:  # 1-1  (Variable)
    def __init__(self, length, dataGram):
        self.len = length
        self.data = dataGram
        self.headerProtocol = struct.unpack('>i', dataGram[0:4])[0]
        self.frameLength = struct.unpack('>i', dataGram[4:8])[0]
        self.payloadRemoved = struct.unpack('>i', dataGram[8:12])[0]
        headerSize = struct.unpack('>i', dataGram[12:16])[0]
        self.headerSize = headerSize
        self.header = dataGram[16:(headerSize + 16)]  # Need a class for parsing the header information.


class sFlowEthernetFrame:  # 1-2  (24 bytes)
    def __init__(self, length, dataGram):
        self.len = length
        self.data = dataGram
        self.frameLength = struct.unpack('>i', dataGram[0:4])[0]
        self.srcMAC = binascii.hexlify(dataGram[4:12])
        self.dstMAC = binascii.hexlify(dataGram[12:20])
        self.type = struct.unpack('>i', dataGram[20:24])[0]
        print "---------------------src MAC", self.srcMAC

class sFlowExtendedSwitch:  # 1-1001 (16 bytes)
    def __init__(self, length, dataGram):
        self.len = length
        self.data = dataGram
        self.srcVLAN = struct.unpack('>i', dataGram[0:4])[0]
        self.srcPriority = struct.unpack('>i', dataGram[4:8])[0]
        self.dstVLAN = struct.unpack('>i', dataGram[8:12])[0]
        self.dstPriority = struct.unpack('>i', dataGram[12:16])[0]


# Counter Record Types

class sFlowIfCounter:  # 2-1 (88 bytes)
    def __init__(self, length, dataGram):
        self.len = length
        self.data = dataGram
        self.index = struct.unpack('>i', dataGram[0:4])[0]
        self.type = struct.unpack('>i', dataGram[4:8])[0]
        self.speed = struct.unpack('>q', dataGram[8:16])[0]  # 64-bit
        self.direction = struct.unpack('>i', dataGram[16:20])[0]
        self.status = struct.unpack('>i', dataGram[20:24])[0]  # This is really a 2-bit value
        self.inputOctets = struct.unpack('>q', dataGram[24:32])[0]  # 64-bit
        self.inputPackets = struct.unpack('>i', dataGram[32:36])[0]
        self.inputMulticast = struct.unpack('>i', dataGram[36:40])[0]
        self.inputBroadcast = struct.unpack('>i', dataGram[40:44])[0]
        self.inputDiscarded = struct.unpack('>i', dataGram[44:48])[0]
        self.inputErrors = struct.unpack('>i', dataGram[48:52])[0]
        self.inputUnknown = struct.unpack('>i', dataGram[52:56])[0]
        self.outputOctets = struct.unpack('>q', dataGram[56:64])[0]  # 64-bit
        self.outputPackets = struct.unpack('>i', dataGram[64:68])[0]
        self.outputMulticast = struct.unpack('>i', dataGram[68:72])[0]
        self.outputBroadcast = struct.unpack('>i', dataGram[72:76])[0]
        self.outputDiscarded = struct.unpack('>i', dataGram[76:80])[0]
        self.outputErrors = struct.unpack('>i', dataGram[80:84])[0]
        self.promiscuous = struct.unpack('>i', dataGram[84:88])[0]


class sFlowEthernetInterface:  # 2-2 (52 bytes)
    def __init__(self, length, dataGram):
        self.len = length
        self.data = dataGram
        self.alignmentError = struct.unpack('>i', dataGram[0:4])[0]
        self.fcsError = struct.unpack('>i', dataGram[4:8])[0]
        self.singleCollision = struct.unpack('>i', dataGram[8:12])[0]
        self.multipleCollision = struct.unpack('>i', dataGram[12:16])[0]
        self.sqeTest = struct.unpack('>i', dataGram[16:20])[0]
        self.deferred = struct.unpack('>i', dataGram[20:24])[0]
        self.lateCollision = struct.unpack('>i', dataGram[24:28])[0]
        self.excessiveCollision = struct.unpack('>i', dataGram[28:32])[0]
        self.internalTransmitError = struct.unpack('>i', dataGram[32:36])[0]
        self.carrierSenseError = struct.unpack('>i', dataGram[36:40])[0]
        self.frameTooLong = struct.unpack('>i', dataGram[40:44])[0]
        self.internalReceiveError = struct.unpack('>i', dataGram[44:48])[0]
        self.symbolError = struct.unpack('>i', dataGram[48:52])[0]


class sFlowVLAN:  # 2-5 (28 bytes)
    def __init__(self, length, dataGram):
        self.len = length
        self.data = dataGram
        self.vlanID = struct.unpack('>i', dataGram[0:4])[0]
        self.octets = struct.unpack('>q', dataGram[4:12])[0]  # 64-bit
        self.unicast = struct.unpack('>i', dataGram[12:16])[0]
        self.multicast = struct.unpack('>i', dataGram[16:20])[0]
        self.broadcast = struct.unpack('>i', dataGram[20:24])[0]
        self.discard = struct.unpack('>i', dataGram[24:28])[0]


class sFlowProcessor:  # 2-1001 (28 bytes)
    def __init__(self, length, dataGram):
        self.len = length
        self.data = dataGram
        self.cpu5s = struct.unpack('>i', dataGram[0:4])[0]
        self.cpu1m = struct.unpack('>i', dataGram[4:8])[0]
        self.cpu5m = struct.unpack('>i', dataGram[8:12])[0]
        self.totalMemory = struct.unpack('>q', dataGram[12:20])[0]  # 64-bit
        self.freeMemory = struct.unpack('>q', dataGram[20:28])[0]  # 64-bit


class sFlowMib2IP:  # 2-2007 (76 bytes)
    def __init__(self, length, dataGram):
        self.len = length
        self.data = dataGram
        self.forwarding = struct.unpack('>i', dataGram[0:4])[0]
        self.defaultTTL = struct.unpack('>i', dataGram[4:8])[0]
        self.inReceives = struct.unpack('>i', dataGram[8:12])[0]
        self.inHeaderErrors = struct.unpack('>i', dataGram[12:16])[0]
        self.inAddressErrors = struct.unpack('>i', dataGram[16:20])[0]
        self.inForwardDatagrams = struct.unpack('>i', dataGram[20:24])[0]
        self.inUnknownProtocols = struct.unpack('>i', dataGram[24:28])[0]
        self.inDiscards = struct.unpack('>i', dataGram[28:32])[0]
        self.inDelivers = struct.unpack('>i', dataGram[32:36])[0]
        self.outRequests = struct.unpack('>i', dataGram[36:40])[0]
        self.outDiscards = struct.unpack('>i', dataGram[40:44])[0]
        self.outNoRoutes = struct.unpack('>i', dataGram[44:48])[0]
        self.reassemblyTimeout = struct.unpack('>i', dataGram[48:52])[0]
        self.reassemblyRequired = struct.unpack('>i', dataGram[52:56])[0]
        self.reassemblyOkay = struct.unpack('>i', dataGram[56:60])[0]
        self.reassemblyFail = struct.unpack('>i', dataGram[60:64])[0]
        self.fragmentOkay = struct.unpack('>i', dataGram[64:68])[0]
        self.fragmentFail = struct.unpack('>i', dataGram[68:72])[0]
        self.fragmentCreate = struct.unpack('>i', dataGram[72:76])[0]


class sFlowMib2ICMP:  # 2-2008 (100 bytes)
    def __init__(self, length, dataGram):
        self.len = length
        self.data = dataGram
        self.inMessage = struct.unpack('>i', dataGram[0:4])[0]
        self.inError = struct.unpack('>i', dataGram[4:8])[0]
        self.inDestinationUnreachable = struct.unpack('>i', dataGram[8:12])[0]
        self.inTimeExceeded = struct.unpack('>i', dataGram[12:16])[0]
        self.inParameterProblem = struct.unpack('>i', dataGram[16:20])[0]
        self.inSourceQuence = struct.unpack('>i', dataGram[20:24])[0]
        self.inRedirect = struct.unpack('>i', dataGram[24:28])[0]
        self.inEcho = struct.unpack('>i', dataGram[28:32])[0]
        self.inEchoReply = struct.unpack('>i', dataGram[32:36])[0]
        self.inTimestamp = struct.unpack('>i', dataGram[36:40])[0]
        self.inAddressMask = struct.unpack('>i', dataGram[40:44])[0]
        self.inAddressMaskReply = struct.unpack('>i', dataGram[44:48])[0]
        self.outMessage = struct.unpack('>i', dataGram[48:52])[0]
        self.outError = struct.unpack('>i', dataGram[52:56])[0]
        self.outDestinationUnreachable = struct.unpack('>i', dataGram[56:60])[0]
        self.outTimeExceeded = struct.unpack('>i', dataGram[60:64])[0]
        self.outParameterProblem = struct.unpack('>i', dataGram[64:68])[0]
        self.outSourceQuence = struct.unpack('>i', dataGram[68:72])[0]
        self.outRedirect = struct.unpack('>i', dataGram[72:76])[0]
        self.outEcho = struct.unpack('>i', dataGram[76:80])[0]
        self.outEchoReply = struct.unpack('>i', dataGram[80:84])[0]
        self.outTimestamp = struct.unpack('>i', dataGram[84:88])[0]
        self.outTimestampReply = struct.unpack('>i', dataGram[88:92])[0]
        self.outAddressMask = struct.unpack('>i', dataGram[92:96])[0]
        self.outAddressMaskReplay = struct.unpack('>i', dataGram[96:100])[0]


class sFlowMib2TCP:  # 2-2009 (60 bytes)
    def __init__(self, length, dataGram):
        self.len = length
        self.data = dataGram
        self.algorithm = struct.unpack('>i', dataGram[0:4])[0]
        self.rtoMin = struct.unpack('>i', dataGram[4:8])[0]
        self.rtoMax = struct.unpack('>i', dataGram[8:12])[0]
        self.maxConnection = struct.unpack('>i', dataGram[12:16])[0]
        self.activeOpen = struct.unpack('>i', dataGram[16:20])[0]
        self.passiveOpen = struct.unpack('>i', dataGram[20:24])[0]
        self.attemptFail = struct.unpack('>i', dataGram[24:28])[0]
        self.establishedReset = struct.unpack('>i', dataGram[28:32])[0]
        self.currentEstablished = struct.unpack('>i', dataGram[32:36])[0]
        self.inSegment = struct.unpack('>i', dataGram[36:40])[0]
        self.outSegment = struct.unpack('>i', dataGram[40:44])[0]
        self.retransmitSegment = struct.unpack('>i', dataGram[44:48])[0]
        self.inError = struct.unpack('>i', dataGram[48:52])[0]
        self.outReset = struct.unpack('>i', dataGram[52:56])[0]
        self.inCsumError = struct.unpack('>i', dataGram[56:60])[0]


class sFlowMib2UDP:  # 2-2010 (28 bytes)
    def __init__(self, length, dataGram):
        self.len = length
        self.data = dataGram
        self.inDatagrams = struct.unpack('>i', dataGram[0:4])[0]
        self.noPorts = struct.unpack('>i', dataGram[4:8])[0]
        self.inErrors = struct.unpack('>i', dataGram[8:12])[0]
        self.outDatagrams = struct.unpack('>i', dataGram[12:16])[0]
        self.receiveBufferError = struct.unpack('>i', dataGram[16:20])[0]
        self.sendBufferError = struct.unpack('>i', dataGram[20:24])[0]
        self.inCheckSumError = struct.unpack('>i', dataGram[24:28])[0]


# Basic Listener

UDP_IP = "0.0.0.0"
UDP_PORT = 6343

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((UDP_IP, UDP_PORT))

while True:

    data, addr = sock.recvfrom(
        3000)  # 1386 bytes is the largest possible sFlow packet, by spec 3000 seems to be the number by practice
    sFlowData = sFlow(data)

    # Below this point is test code.

    print ""
    # print "Source:", addr[0]
    print "length:", sFlowData.len
    print "DG Version:", sFlowData.dgVersion
    print "Agent Address:", sFlowData.agentAddress
    print "Sub Agent:", sFlowData.subAgent
    print "Sequence Number:", sFlowData.sequenceNumber
    # print "System UpTime:", sFlowData.sysUpTime
    # print "Number of Samples:", sFlowData.NumberSample
    # print ""
    for i in range(sFlowData.NumberSample):
        # print "Sample Number:", i + 1
        # print "Sample Sequence:", sFlowData.sample[i].sequence
        # print "Sample Enterprise:", sFlowData.sample[i].enterprise
        # print "Sample Type:", sFlowData.sample[i].sampleType
        # print "Sample Length:", sFlowData.sample[i].len
        # print "Sample Source Type:", sFlowData.sample[i].sourceType
        # print "Sample Source Index:", sFlowData.sample[i].sourceIndex
        # print "Sample Rate:", sFlowData.sample[i].sampleRate
        # print "Sample Pool:", sFlowData.sample[i].samplePool

        # print "Sample Record Count:", sFlowData.sample[i].recordCount
        # print ""
        for j in range(sFlowData.sample[i].recordCount):
            # print "Record Header:", sFlowData.sample[i].record[j].header
            # print "Record Enterprise:", sFlowData.sample[i].record[j].enterprise
            # print "Record Sample Type:", sFlowData.sample[i].record[j].sampleType
            # print "Record Format:", sFlowData.sample[i].record[j].format
            # print "Record Length:", sFlowData.sample[i].record[j].len
            if sFlowData.sample[i].record[j].sampleType == 1:
                if sFlowData.sample[i].record[j].format == 1 and sFlowData.sample[i].record[j].enterprise == 0:
                    record = sFlowRawPacketHeader(sFlowData.sample[i].record[j].len, sFlowData.sample[i].record[j].data)
                    # print "Raw Packet Header Protocol:", record.headerProtocol
                    print "Frame Length:", record.frameLength
                    # print "Payload Removed:", record.payloadRemoved
                    # print "Header Size:", record.headerSize

                elif sFlowData.sample[i].record[j].format == 2 and sFlowData.sample[i].record[j].enterprise == 0:
                    record = sFlowEthernetFrame(sFlowData.sample[i].record[j].len, sFlowData.sample[i].record[j].data)
                    print "Ethernet Frame Length:", record.frameLength
                    print "Ethernet Frame src MAC:", record.srcMAC
                    print "Ethernet Frame dst MAC:", record.dstMAC
                    print "Ethernet Frame Record Type:", record.type
                elif sFlowData.sample[i].record[j].format == 1001:
                    record = sFlowExtendedSwitch(sFlowData.sample[i].record[j].len, sFlowData.sample[i].record[j].data)
                    # print "Extended Switch:", record.srcVLAN
                    # print "Extended Switch:", record.srcPriority
                    # print "Extended Switch:", record.dstVLAN
                    # print "Extended Switch:", record.dstPriority
                    # print "Flow 1001"
                    # else:
                    # print "Flow Record Enterprise:", sFlowData.sample[i].record[j].enterprise
                    # print "Flow Record Type:", sFlowData.sample[i].record[j].format
            elif sFlowData.sample[i].record[j].sampleType == 2:
                if sFlowData.sample[i].record[j].format == 1:
                    record = sFlowIfCounter(sFlowData.sample[i].record[j].len, sFlowData.sample[i].record[j].data)

                elif sFlowData.sample[i].record[j].format == 2:
                    record = sFlowEthernetInterface(sFlowData.sample[i].record[j].len,
                                                    sFlowData.sample[i].record[j].data)
                    # print "Ethernet Alignmet Error:", record.alignmentError
                    # print "Ethernet FCS Error:", record.fcsError
                    # print "Ethernet Single Collision Frames:", record.singleCollision
                    # print "Ethernet Multiple Collision Frames:", record.multipleCollision
                    # print "Ethernet SQE Test Error:", record.sqeTest
                    # print "Ethernet Deferred Transmissions:", record.deferred
                    # print "Ethernet Late Collisions:", record.lateCollision
                    # print "Ethernet Excessiove Collisions:", record.excessiveCollision
                    # print "Ethernet Internal Transmit Error:", record.internalTransmitError
                    # print "Ethernet Carrier Sense Error:", record.carrierSenseError
                    # print "Ethernet Frame Too Long:", record.frameTooLong
                    # print "Ethernet Internal Receive Error:", record.internalReceiveError
                    # print "Ethernet Symbol Error:", record.symbolError
                    # print "Counter 2"
                elif sFlowData.sample[i].record[j].format == 5:
                    record = sFlowVLAN(sFlowData.sample[i].record[j].len, sFlowData.sample[i].record[j].data)
                    # print "VLAN :", record.vlanID
                    # print "VLAN :", record.octets
                    # print "VLAN :", record.unicast
                    # print "VLAN :", record.multicast
                    # print "VLAN :", record.broadcast
                    # print "VLAN :", record.discard
                    # print "Counter 5"
                elif sFlowData.sample[i].record[j].format == 1001:
                    record = sFlowProcessor(sFlowData.sample[i].record[j].len, sFlowData.sample[i].record[j].data)

                elif sFlowData.sample[i].record[j].format == 2010:
                    record = sFlowMib2UDP(sFlowData.sample[i].record[j].len, sFlowData.sample[i].record[j].data)
                    # print "Counter 2010"
                    # print "UDP In Datagrams:", record.inDatagrams
                    # print "UDP No Ports:", record.noPorts
                    # print "UDP In Errors:", record.inErrors
                    # print "UDP Out Datagrams:", record.outDatagrams
                    # print "UDP Receive Buffer Error:", record.receiveBufferError
                    # print "UDP Send Buffer Error:", record.sendBufferError
                    # print "UDP In Check Sum Error:", record.inCheckSumError
                    # else:
                    # print "Counter Record Enterprise:", sFlowData.sample[i].record[j].enterprise
                    # print "Counter Record Type:", sFlowData.sample[i].record[j].format