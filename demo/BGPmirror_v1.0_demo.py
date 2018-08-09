#! /usr/bin/env python
# -*- coding: utf-8 -*-

# @company: heetian
# @file: BGPmirror_v1.0_demo.py
# @time: 2017/11/16 0016 下午 2:15
# @author: xwh
# @desc:

from kafka import KafkaProducer
import socket


producer = KafkaProducer(bootstrap_servers="192.168.100.15:9092")
CONFIG_TOPIC = "192.168.100.13_BGP_MIRROR_CONFIG"


a = '{"type":"mirror","keys":"qvob8c07499-7e,qvo5314b7db-50,qvo5fa2f7f8-dc,qvo2109e4b2-5f,qvo6a6c5e96-d4,qvoa24febd4-f2,qvoaa171250-43,qvo770bd7e9-5e,qvo4e027af9-11,qvo0141feb2-24,qvo6c6fa4d8-a8,qvob99e6745-c1,qvo8146dfd0-44,qvo14384418-be,qvo717a8aa0-d1,qvob72850c1-61,qvo58d02a5b-c6,qvo3bd7afec-33,qvo12094398-44,qvo43a8477f-0f,qvoc4b8967d-aa,qvo7c9a2fc5-d8,qvo18386cf6-80,qvofff5f36c-9a,qvo4d94603b-4d,qvo859ad01a-e4,qvo15424c9b-39,qvo2cb03ed6-cf,qvo164c1cb3-bb,qvoa2e774a2-99,qvocf443be5-00,qvo1a6a9128-99,qvo856b9c31-05,qvo8ebce7d0-2b,qvo275fa6d0-eb,qvoc23c1240-23,qvo188a9f16-87,qvo3a7f739d-4f,qvob16dec02-bd,qvo42866d95-85,qvo5e2a740e-d9,qvo59f987d1-00,qvoda305925-06,qvo93716f6f-b3,qvo09779d2a-05,qvo0ee20cd3-6c,qvof3ec5e2c-f7,qvoc99c8adc-9c,qvo247f4a61-25,qvo37afdff9-ae,qvo2be9227b-92,qvoa7bbe7f5-dc,qvo13cb70c6-fc,qvo6e401242-6b,qvobb0e0aa7-37,qvo558a21e6-1f,qvo8ba1e00e-c4,qvo9678c945-75,qvob3a5f3bd-a2,qvo372845b8-6b,qvo48e94eef-e4,qvo54c9247f-cb,qvo1a874a7e-c4,qvo1843079b-25,qvoed84e59e-6f,qvoa9d0e97b-74,qvo8a0ed220-7c,qvo754cb887-b0,qvoa5ace75e-c3,qvo81a716e2-e4,qvo593583f1-8d,qvo6906170d-29,qvoc4348cd2-16,qvo8a91e999-3f,qvo176121c4-84,qvo65c8e69a-81,qvo30b8405a-8e,qvo143a6f67-f8,qvoec17ed11-b8,qvo4bbd3ba1-3f,qvo082f993b-27,qvod87400cc-c7,qvocec3c286-3d,qvoff998d4d-1e,qvo5c487b25-d8,qvo345aff9c-1d,qvo19def9c0-65,qvo719967bf-35,qvo6d471ef9-71,qvo0a2987a8-37,qvo0414709e-37,qvo88951c2d-9b,qvoc20d0524-8a,qvo866e87d4-c7,qvo36fb8674-af,qvocf00a53f-c0,qvo419f7d79-32,qvofcf6bd06-c2,qvo9d9edfbb-40,qvoa4c13c27-1c,qvo2eb5960b-2e,qvoa2bbdca2-d7,qvoebfbfe41-a7,qvo1e8082f0-24,qvo3bbd7fc3-2a,qvo71b963ab-04,qvoe2cfe588-ca,qvofe831dfc-aa,qvob8fff0e4-6d,qvo99ed1108-18,qvoda56152e-1e,qvof8226556-cb,qvof7c6864a-d9,qvo71572993-b4,qvo507dea90-18,qvo68d11041-32,qvo034c93a7-95,qvo5e712bd3-0d,qvo7780d983-85,qvoe3c06efc-9c,qvo6c6bb01d-aa,qvode811669-cc,qvofd1589cd-9c,qvo3bffe932-7c,qvo25e0194a-db,qvoc2c50fc4-8a,qvo5219cbf1-14,qvo525a9921-52,qvo6844ec6d-c5,qvoe1eb1a5b-3b,qvo4751266b-04,qvocd44df0c-44,qvo03f56a18-de,qvo2819e9e3-b0,qvod9312a15-aa,qvob1317cff-20,qvo7a51b575-9d,qvo212aaf3e-6f,qvo901a2c38-7f,qvo73ad2d8f-9c,qvo92be6baa-16,qvoba1cd678-97,qvocae76d4f-2c,qvocbadbe6a-9a,qvodd5e984b-0a,qvo10de37dd-2d,qvocc233dfa-d3,qvobd6c7bc9-bf,qvo0f2cd1f1-95,qvo73609527-a2,qvo7463554d-29,qvo224c605e-cc,qvo9b5710dd-4c,qvo699185b8-21,qvo1c62dbf8-5a,qvod9ce5b90-06,qvo2c7aacf0-8a,qvod861fc03-91,qvoa3f25056-ca,qvo2c2f23e1-95,qvo1ad1682a-69,qvo7882f39f-c6,qvo66b9fc5c-67,qvo29623856-ad,qvoe1faa9db-82,qvoa9b7ab7e-fb,qvo03ae9b97-b9,qvof2e008e6-28,qvo6cd5a584-ab,qvodebb4991-88,qvo71a8e018-ab,qvo5f1843d5-2a,qvo0ba9c621-6e,qvoe926d334-3d,qvo30582bf0-cf,qvo7f298d2f-be,qvo4b36731a-4f,qvo640b0362-eb,qvo0afa750a-d4,qvo2040b4dd-02,qvo0b28a6f2-d6,qvo2ab75592-11,qvoedfc1a6e-5b,qvo39e98e41-32,qvodeb0663b-ba,qvo97b396c8-68,qvob8611c58-4b,qvoe63eb954-07,qvo64662f93-76,qvo895f5dbb-7a,qvo4c937dae-10,qvo05496549-d1,qvo44d371e0-7a,qvo107a2f27-91,qvo382284ae-5e,qvof9b820be-a1,qvod1b2710a-17,qvoe2e3c915-a1"}'


producer.send(CONFIG_TOPIC, a)
print a
producer.flush()
