EESchema Schematic File Version 4
EELAYER 30 0
EELAYER END
$Descr A4 11693 8268
encoding utf-8
Sheet 1 1
Title ""
Date ""
Rev ""
Comp ""
Comment1 ""
Comment2 ""
Comment3 ""
Comment4 ""
$EndDescr
$Comp
L Timer_RTC:DS1307+ U4
U 1 1 6136FBC0
P 8300 2150
F 0 "U4" H 8844 2196 50  0000 L CNN
F 1 "DS1307Z+" H 8844 2105 50  0000 L CNN
F 2 "Package_SO:SOIC-8_3.9x4.9mm_P1.27mm" H 8300 1650 50  0001 C CNN
F 3 "https://datasheets.maximintegrated.com/en/ds/DS1307.pdf" H 8300 1950 50  0001 C CNN
F 4 "Maxim Integrated" H 8300 2150 50  0001 C CNN "Manufacturer"
F 5 "DS1307+" H 8300 2150 50  0001 C CNN "part_number"
F 6 "" H 8300 2150 50  0001 C CNN "Vendor"
F 7 "DS1307Z+" H 8300 2150 50  0001 C CNN "Part"
	1    8300 2150
	0    -1   -1   0   
$EndComp
$Comp
L Device:R R3
U 1 1 613829B2
P 5600 2800
F 0 "R3" V 5807 2800 50  0000 C CNN
F 1 "100Ω" V 5716 2800 50  0000 C CNN
F 2 "Resistor_SMD:R_2010_5025Metric" V 5530 2800 50  0001 C CNN
F 3 "https://www.koaspeer.com/pdfs/RK73H.pdf" H 5600 2800 50  0001 C CNN
F 4 "RC2010JK-0710KL" H 5600 2800 50  0001 C CNN "part_number"
F 5 "KOA Speer Electronics, Inc." H 5600 2800 50  0001 C CNN "Manufacturer"
F 6 "" H 5600 2800 50  0001 C CNN "Vendor"
F 7 "RC2010JK-0710KL" H 5600 2800 50  0001 C CNN "Part"
	1    5600 2800
	1    0    0    -1  
$EndComp
$Comp
L Device:R R1
U 1 1 6138329F
P 3850 3300
F 0 "R1" V 4057 3300 50  0000 C CNN
F 1 "75k" V 3966 3300 50  0000 C CNN
F 2 "Resistor_SMD:R_2010_5025Metric" V 3780 3300 50  0001 C CNN
F 3 "https://www.koaspeer.com/pdfs/RK73H.pdf" H 3850 3300 50  0001 C CNN
F 4 "RK73H2HTTE7502F" H 3850 3300 50  0001 C CNN "part_number"
F 5 "KOA Speer Electronics, Inc." H 3850 3300 50  0001 C CNN "Manufacturer"
F 6 "" H 3850 3300 50  0001 C CNN "Vendor"
F 7 "RK73H2HTTE7502F" H 3850 3300 50  0001 C CNN "Part"
	1    3850 3300
	0    -1   -1   0   
$EndComp
$Comp
L power:Earth #PWR0101
U 1 1 61383BCF
P 4300 3300
F 0 "#PWR0101" H 4300 3050 50  0001 C CNN
F 1 "Earth" H 4300 3150 50  0001 C CNN
F 2 "" H 4300 3300 50  0001 C CNN
F 3 "~" H 4300 3300 50  0001 C CNN
	1    4300 3300
	1    0    0    -1  
$EndComp
Wire Wire Line
	4000 3300 4050 3300
Wire Wire Line
	4300 3150 4300 3300
Connection ~ 4300 3300
Wire Wire Line
	5900 2450 5900 2350
$Comp
L Regulator_Switching:TPS63002 U3
U 1 1 6136C756
P 6300 2450
F 0 "U3" H 6300 3117 50  0000 C CNN
F 1 "TPS63002" H 6300 3026 50  0000 C CNN
F 2 "Package_SON:Texas_DSC0010J_ThermalVias" H 7150 1900 50  0001 C CNN
F 3 "http://www.ti.com/lit/ds/symlink/tps63002.pdf" H 6000 3000 50  0001 C CNN
F 4 "Texas Instruments" H 6300 2450 50  0001 C CNN "Manufacturer"
F 5 "TPS63002" H 6300 2450 50  0001 C CNN "part_number"
F 6 "" H 6300 2450 50  0001 C CNN "Vendor"
F 7 "TPS63002" H 6300 2450 50  0001 C CNN "Part"
	1    6300 2450
	1    0    0    -1  
$EndComp
Wire Wire Line
	5900 2250 5100 2250
Connection ~ 5900 2450
Connection ~ 5900 2650
Wire Wire Line
	5900 2650 5900 2450
$Comp
L Timer:TPL5110 U2
U 1 1 6136C237
P 4300 2650
F 0 "U2" H 4250 3231 50  0000 C CNN
F 1 "TPL5110" H 4250 3140 50  0000 C CNN
F 2 "Package_TO_SOT_SMD:SOT-23-6" H 4300 2650 50  0001 C CNN
F 3 "http://www.ti.com/lit/ds/symlink/tpl5110.pdf" H 4100 2250 50  0001 C CNN
F 4 "Texas Instruments" H 4300 2650 50  0001 C CNN "Manufacturer"
F 5 "TPL5110" H 4300 2650 50  0001 C CNN "part_number"
F 6 "" H 4300 2650 50  0001 C CNN "Vendor"
F 7 "TPL5110" H 4300 2650 50  0001 C CNN "Part"
	1    4300 2650
	1    0    0    -1  
$EndComp
$Comp
L power:Earth #PWR0102
U 1 1 613B7C69
P 6200 3200
F 0 "#PWR0102" H 6200 2950 50  0001 C CNN
F 1 "Earth" H 6200 3050 50  0001 C CNN
F 2 "" H 6200 3200 50  0001 C CNN
F 3 "~" H 6200 3200 50  0001 C CNN
	1    6200 3200
	1    0    0    -1  
$EndComp
Wire Wire Line
	6300 3050 6200 3050
Wire Wire Line
	6200 3200 6200 3050
Connection ~ 6200 3050
Wire Wire Line
	4300 2250 3550 2250
Wire Wire Line
	3550 2250 3550 2650
Wire Wire Line
	3550 2650 3300 2650
Connection ~ 4300 2250
Wire Wire Line
	3700 2650 3550 2650
Connection ~ 3550 2650
$Comp
L Switch:SW_Push SW1
U 1 1 613B9875
P 2100 3200
F 0 "SW1" H 2100 3485 50  0000 C CNN
F 1 "SW_Push" H 2100 3394 50  0000 C CNN
F 2 "#none" H 2100 3400 50  0001 C CNN
F 3 "~" H 2100 3400 50  0001 C CNN
	1    2100 3200
	1    0    0    -1  
$EndComp
$Comp
L Device:L L1
U 1 1 613BC649
P 6300 1700
F 0 "L1" V 6119 1700 50  0000 C CNN
F 1 "2.2μH" V 6210 1700 50  0000 C CNN
F 2 "Inductor_SMD:L_Abracon_ASPI-3012S" H 6300 1700 50  0001 C CNN
F 3 "https://product.tdk.com/en/system/files?file=dam/doc/product/inductor/inductor/smd/catalog/inductor_commercial_power_vls3012hbx_en.pdf" H 6300 1700 50  0001 C CNN
F 4 "VLS3012HBX-2R2M" V 6300 1700 50  0001 C CNN "part_number"
F 5 "TDK Corporation" H 6300 1700 50  0001 C CNN "Manufacturer"
F 6 "" H 6300 1700 50  0001 C CNN "Vendor"
F 7 "VLS3012HBX-2R2M" H 6300 1700 50  0001 C CNN "Part"
	1    6300 1700
	0    1    1    0   
$EndComp
Wire Wire Line
	6700 2050 6700 1700
Wire Wire Line
	6700 1700 6450 1700
Wire Wire Line
	6150 1700 5900 1700
Wire Wire Line
	5900 1700 5900 2050
$Comp
L Device:C C2
U 1 1 613BF7CA
P 5850 3050
F 0 "C2" V 5598 3050 50  0000 C CNN
F 1 "0.1μF" V 5689 3050 50  0000 C CNN
F 2 "Capacitor_SMD:C_1206_3216Metric" H 5888 2900 50  0001 C CNN
F 3 "https://content.kemet.com/datasheets/KEM_C1002_X7R_SMD.pdf" H 5850 3050 50  0001 C CNN
F 4 "C1206C104K8RAC7800" H 5850 3050 50  0001 C CNN "part_number"
F 5 "KEMET" H 5850 3050 50  0001 C CNN "Manufacturer"
F 6 "" H 5850 3050 50  0001 C CNN "Vendor"
F 7 "C1206C104K8RAC7800" H 5850 3050 50  0001 C CNN "Part"
	1    5850 3050
	0    1    1    0   
$EndComp
$Comp
L Device:C C4
U 1 1 613BFECA
P 7250 2400
F 0 "C4" H 7365 2446 50  0000 L CNN
F 1 "10μF" H 7365 2355 50  0000 L CNN
F 2 "Capacitor_SMD:C_1206_3216Metric" H 7288 2250 50  0001 C CNN
F 3 "https://global.kyocera.com/prdct/electro/product/pdf/cm_e.pdf" H 7250 2400 50  0001 C CNN
F 4 "CM316X5R106K10AT" H 7250 2400 50  0001 C CNN "part_number"
F 5 "Kyocera International Inc. Electronic Components" H 7250 2400 50  0001 C CNN "Manufacturer"
F 6 "" H 7250 2400 50  0001 C CNN "Vendor"
F 7 "CM316X5R106K10AT" H 7250 2400 50  0001 C CNN "Part"
	1    7250 2400
	1    0    0    -1  
$EndComp
$Comp
L Device:C C3
U 1 1 613C025D
P 6950 2400
F 0 "C3" H 7065 2446 50  0000 L CNN
F 1 "10μF" H 7065 2355 50  0000 L CNN
F 2 "Capacitor_SMD:C_1206_3216Metric" H 6988 2250 50  0001 C CNN
F 3 "https://global.kyocera.com/prdct/electro/product/pdf/cm_e.pdf" H 6950 2400 50  0001 C CNN
F 4 "CM316X5R106K10AT" H 6950 2400 50  0001 C CNN "part_number"
F 5 "Kyocera International Inc. Electronic Components" H 6950 2400 50  0001 C CNN "Manufacturer"
F 6 "" H 6950 2400 50  0001 C CNN "Vendor"
F 7 "CM316X5R106K10AT" H 6950 2400 50  0001 C CNN "Part"
	1    6950 2400
	1    0    0    -1  
$EndComp
Wire Wire Line
	5600 2650 5700 2650
Wire Wire Line
	5700 2650 5700 3050
Connection ~ 5700 2650
Wire Wire Line
	5700 2650 5900 2650
Wire Wire Line
	5950 3050 6000 3050
Connection ~ 6000 3050
Wire Wire Line
	6000 3050 6200 3050
Wire Wire Line
	6700 2450 6700 2250
Wire Wire Line
	6700 2250 6950 2250
Connection ~ 6700 2250
Connection ~ 6950 2250
$Comp
L power:Earth #PWR0104
U 1 1 613CD4D4
P 6950 2550
F 0 "#PWR0104" H 6950 2300 50  0001 C CNN
F 1 "Earth" H 6950 2400 50  0001 C CNN
F 2 "" H 6950 2550 50  0001 C CNN
F 3 "~" H 6950 2550 50  0001 C CNN
	1    6950 2550
	1    0    0    -1  
$EndComp
$Comp
L power:Earth #PWR0105
U 1 1 613CD9F7
P 7250 2550
F 0 "#PWR0105" H 7250 2300 50  0001 C CNN
F 1 "Earth" H 7250 2400 50  0001 C CNN
F 2 "" H 7250 2550 50  0001 C CNN
F 3 "~" H 7250 2550 50  0001 C CNN
	1    7250 2550
	1    0    0    -1  
$EndComp
Wire Wire Line
	7700 2250 7700 3150
Connection ~ 7700 2250
Wire Wire Line
	7700 2250 7900 2250
Wire Wire Line
	7900 1500 7900 2150
$Comp
L Connector:Screw_Terminal_01x11 J1
U 1 1 613EDD1C
P 3200 3500
F 0 "J1" H 3280 3492 50  0000 L CNN
F 1 "Screw_Terminal_01x11" H 3280 3401 50  0000 L CNN
F 2 "TerminalBlock_TE-Connectivity:TerminalBlock_TE_1-282834-1_1x11_P2.54mm_Horizontal" H 3200 3500 50  0001 C CNN
F 3 "https://www.aliexpress.com/item/33010961562.html?spm=a2g0o.productlist.0.0.48c03c2cpAilqm&algo_pvid=d662f399-6825-4aba-b03d-2694688fa9f9&algo_exp_id=d662f399-6825-4aba-b03d-2694688fa9f9-37&pdp_ext_f=%7B%22sku_id%22%3A%2210000000147204690%22%7D" H 3200 3500 50  0001 C CNN
F 4 "" H 3200 3500 50  0001 C CNN "part_number"
	1    3200 3500
	1    0    0    -1  
$EndComp
Wire Wire Line
	3000 3200 2300 3200
Wire Wire Line
	3700 2750 3700 3300
Connection ~ 3000 3300
Connection ~ 3700 3300
Wire Wire Line
	3000 3300 3700 3300
Wire Wire Line
	3000 3000 3300 3000
Wire Wire Line
	3300 3000 3300 2650
Wire Wire Line
	3000 3100 3350 3100
$Comp
L power:Earth #PWR0106
U 1 1 61428091
P 3450 2900
F 0 "#PWR0106" H 3450 2650 50  0001 C CNN
F 1 "Earth" H 3450 2750 50  0001 C CNN
F 2 "" H 3450 2900 50  0001 C CNN
F 3 "~" H 3450 2900 50  0001 C CNN
	1    3450 2900
	1    0    0    -1  
$EndComp
Wire Wire Line
	3000 3000 3000 2550
Wire Wire Line
	3000 2550 2250 2550
Connection ~ 3000 3000
Wire Wire Line
	3000 3100 2500 3100
Wire Wire Line
	2500 3100 2500 2850
Wire Wire Line
	2500 2850 2250 2850
Connection ~ 3000 3100
$Comp
L Device:Battery_Cell BT1
U 1 1 613E98EC
P 2250 2750
F 0 "BT1" H 2368 2846 50  0000 L CNN
F 1 "Battery_Cell" H 2368 2755 50  0000 L CNN
F 2 "#none" V 2250 2810 50  0001 C CNN
F 3 "~" V 2250 2810 50  0001 C CNN
F 4 "CR1220" H 2250 2750 50  0001 C CNN "part_number"
F 5 "CR1220" H 2250 2750 50  0001 C CNN "Part"
	1    2250 2750
	1    0    0    -1  
$EndComp
Wire Wire Line
	3550 2650 3550 3200
Wire Wire Line
	3550 3200 3000 3200
Connection ~ 3000 3200
Wire Wire Line
	3350 3100 3350 2900
Wire Wire Line
	3350 2900 3450 2900
$Comp
L power:Earth #PWR0107
U 1 1 61458F16
P 9050 2150
F 0 "#PWR0107" H 9050 1900 50  0001 C CNN
F 1 "Earth" H 9050 2000 50  0001 C CNN
F 2 "" H 9050 2150 50  0001 C CNN
F 3 "~" H 9050 2150 50  0001 C CNN
	1    9050 2150
	1    0    0    -1  
$EndComp
$Comp
L Device:LED D2
U 1 1 6145E678
P 2250 3400
F 0 "D2" H 2243 3145 50  0000 C CNN
F 1 "LED" H 2243 3236 50  0000 C CNN
F 2 "#none" H 2250 3400 50  0001 C CNN
F 3 "https://www.kingbrightusa.com/images/catalog/SPEC/WP7113SECK-J3.pdf" H 2250 3400 50  0001 C CNN
F 4 "WP7113SECK/J3" H 2250 3400 50  0001 C CNN "part_number"
	1    2250 3400
	-1   0    0    1   
$EndComp
Wire Wire Line
	3000 3400 2400 3400
Wire Wire Line
	3000 3400 4050 3400
Wire Wire Line
	4050 3400 4050 3300
Connection ~ 3000 3400
Connection ~ 4050 3300
Wire Wire Line
	4050 3300 4300 3300
$Comp
L Device:R R2
U 1 1 6146BE2F
P 4650 3500
F 0 "R2" V 4857 3500 50  0000 C CNN
F 1 "560Ω" V 4766 3500 50  0000 C CNN
F 2 "Resistor_SMD:R_2010_5025Metric" V 4580 3500 50  0001 C CNN
F 3 "https://www.yageo.com/upload/media/product/productsearch/datasheet/rchip/PYu-AC_51_RoHS_L_7.pdf" H 4650 3500 50  0001 C CNN
F 4 "AC2010JK-07560RL" H 4650 3500 50  0001 C CNN "part_number"
F 5 "YAGEO" H 4650 3500 50  0001 C CNN "Manufacturer"
F 6 "" H 4650 3500 50  0001 C CNN "Vendor"
F 7 "AC2010JK-07560RL" H 4650 3500 50  0001 C CNN "Part"
	1    4650 3500
	0    -1   -1   0   
$EndComp
Wire Wire Line
	4500 3500 3000 3500
Connection ~ 3000 3500
Wire Wire Line
	3000 3600 1900 3600
Wire Wire Line
	3000 3800 1900 3800
Wire Wire Line
	2900 3900 2900 4150
Wire Wire Line
	2900 4150 2250 4150
Wire Wire Line
	2950 4000 2950 4250
Wire Wire Line
	1900 3300 1900 3200
Wire Wire Line
	1900 3300 3000 3300
Wire Wire Line
	2100 3500 2100 3400
Wire Wire Line
	2100 3500 3000 3500
$Comp
L Sensor:DHT11 U1
U 1 1 614AC764
P 1650 3700
F 0 "U1" H 1406 3746 50  0000 R CNN
F 1 "DHT22" H 1406 3655 50  0000 R CNN
F 2 "#none" H 1650 3300 50  0001 C CNN
F 3 "http://akizukidenshi.com/download/ds/aosong/DHT11.pdf" H 1800 3950 50  0001 C CNN
	1    1650 3700
	1    0    0    -1  
$EndComp
Wire Wire Line
	1900 3600 1900 3400
Wire Wire Line
	1900 3400 1650 3400
Wire Wire Line
	1900 4000 1650 4000
Wire Wire Line
	1950 3700 3000 3700
Wire Wire Line
	1900 3800 1900 4000
$Comp
L Device:LED D1
U 1 1 614D68D2
P 2100 4150
F 0 "D1" H 2093 4367 50  0000 C CNN
F 1 "LED" H 2093 4276 50  0000 C CNN
F 2 "#none" H 2100 4150 50  0001 C CNN
F 3 "~" H 2100 4150 50  0001 C CNN
F 4 "500mA at 5V. Adding a 5.5R resistor reduces current to 200mA" H 2100 4150 50  0001 C CNN "Notes"
	1    2100 4150
	1    0    0    -1  
$EndComp
Wire Wire Line
	2950 4250 1850 4250
Wire Wire Line
	1950 4150 1850 4150
Wire Wire Line
	1850 4150 1850 4250
$Comp
L Device:R R4
U 1 1 615AD828
P 5550 4150
F 0 "R4" H 5620 4196 50  0000 L CNN
F 1 "2.2k" H 5620 4105 50  0000 L CNN
F 2 "Resistor_SMD:R_2010_5025Metric" V 5480 4150 50  0001 C CNN
F 3 "https://www.seielect.com/catalog/sei-rmcf_rmcp.pdf" H 5550 4150 50  0001 C CNN
F 4 "RMCF2010JT2K20" H 5550 4150 50  0001 C CNN "part_number"
F 5 "Stackpole Electronics, Inc." H 5550 4150 50  0001 C CNN "Manufacturer"
F 6 "" H 5550 4150 50  0001 C CNN "Vendor"
F 7 "RMCF2010JT2K20" H 5550 4150 50  0001 C CNN "Part"
	1    5550 4150
	1    0    0    -1  
$EndComp
$Comp
L power:Earth #PWR0108
U 1 1 615E52C8
P 4300 4000
F 0 "#PWR0108" H 4300 3750 50  0001 C CNN
F 1 "Earth" H 4300 3850 50  0001 C CNN
F 2 "" H 4300 4000 50  0001 C CNN
F 3 "~" H 4300 4000 50  0001 C CNN
	1    4300 4000
	1    0    0    -1  
$EndComp
$Comp
L power:Earth #PWR0109
U 1 1 615F83BE
P 9100 4450
F 0 "#PWR0109" H 9100 4200 50  0001 C CNN
F 1 "Earth" H 9100 4300 50  0001 C CNN
F 2 "" H 9100 4450 50  0001 C CNN
F 3 "~" H 9100 4450 50  0001 C CNN
	1    9100 4450
	1    0    0    -1  
$EndComp
$Comp
L Connector_Generic:Conn_02x13_Odd_Even J2
U 1 1 6157EF99
P 8500 4450
F 0 "J2" H 8650 5100 50  0000 C CNN
F 1 "Conn_02x13_Odd_Even" H 8550 3750 50  0000 C CNN
F 2 "Connector_PinSocket_2.54mm:PinSocket_2x13_P2.54mm_Vertical" H 8500 4450 50  0001 C CNN
F 3 "https://www.te.com/commerce/DocumentDelivery/DDEController?Action=srchrtrv&DocNm=215307&DocType=Customer+Drawing&DocLang=English" H 8500 4450 50  0001 C CNN
F 4 "1-215307-0" H 8500 4450 50  0001 C CNN "part_number"
F 5 "1-215307-0" H 8500 4450 50  0001 C CNN "Part"
F 6 "TE Connectivity AMP Connectors" H 8500 4450 50  0001 C CNN "Manufacturer"
	1    8500 4450
	1    0    0    -1  
$EndComp
Wire Wire Line
	9100 4450 8950 4450
Connection ~ 8950 4450
Wire Wire Line
	8200 2650 8200 3150
$Comp
L Device:Battery_Cell BT2
U 1 1 616EDF57
P 8250 1500
F 0 "BT2" V 7995 1550 50  0000 C CNN
F 1 "Battery_Cell" V 8086 1550 50  0000 C CNN
F 2 "Battery:BatteryHolder_Keystone_3000_1x12mm" V 8250 1560 50  0001 C CNN
F 3 "https://www.keyelco.com/userAssets/file/M65p9.pdf" V 8250 1560 50  0001 C CNN
F 4 "Keystone Electronics" H 8250 1500 50  0001 C CNN "Manufacturer"
F 5 "3000" H 8250 1500 50  0001 C CNN "part_number"
F 6 "" H 8250 1500 50  0001 C CNN "Vendor"
F 7 "3000" H 8250 1500 50  0001 C CNN "Part"
	1    8250 1500
	0    1    1    0   
$EndComp
$Comp
L Device:Crystal Y1
U 1 1 616F7111
P 8550 2850
F 0 "Y1" H 8550 3118 50  0000 C CNN
F 1 "Crystal" H 8550 3027 50  0000 C CNN
F 2 "Crystal:Crystal_SMD_MicroCrystal_CM9V-T1A-2Pin_1.6x1.0mm" H 8550 2850 50  0001 C CNN
F 3 "https://www.microcrystal.com/fileadmin/Media/Products/32kHz/Datasheet/CM9V-T1A.pdf" H 8550 2850 50  0001 C CNN
F 4 "CM9V-T1A" H 8550 2850 50  0001 C CNN "part_number"
F 5 "Micro Crystal AG" H 8550 2850 50  0001 C CNN "Manufacturer"
F 6 "" H 8550 2850 50  0001 C CNN "Vendor"
F 7 "CM9V-T1A-32.768KHZ-12.5PF-20PPM-TA-QC" H 8550 2850 50  0001 C CNN "Part"
	1    8550 2850
	1    0    0    -1  
$EndComp
Wire Wire Line
	8400 2650 8400 2850
Wire Wire Line
	8700 2850 8750 2850
Wire Wire Line
	8750 2850 8750 2650
Wire Wire Line
	8750 2650 8500 2650
$Comp
L Device:R R5
U 1 1 61708319
P 7850 3150
F 0 "R5" V 7643 3150 50  0000 C CNN
F 1 "10k" V 7734 3150 50  0000 C CNN
F 2 "Resistor_SMD:R_2010_5025Metric" V 7780 3150 50  0001 C CNN
F 3 "https://www.yageo.com/upload/media/product/productsearch/datasheet/rchip/PYu-RC_Group_51_RoHS_L_11.pdf" H 7850 3150 50  0001 C CNN
F 4 "RC2010JK-0710KL" H 7850 3150 50  0001 C CNN "part_number"
F 5 "YAGEO" H 7850 3150 50  0001 C CNN "Manufacturer"
F 6 "" H 7850 3150 50  0001 C CNN "Vendor"
F 7 "RC2010JK-0710KL" H 7850 3150 50  0001 C CNN "Part"
	1    7850 3150
	0    1    1    0   
$EndComp
Wire Wire Line
	8000 3150 8200 3150
Connection ~ 8200 3150
$Comp
L Device:R R6
U 1 1 61707D76
P 7850 3500
F 0 "R6" V 7643 3500 50  0000 C CNN
F 1 "10k" V 7734 3500 50  0000 C CNN
F 2 "Resistor_SMD:R_2010_5025Metric" V 7780 3500 50  0001 C CNN
F 3 "https://www.yageo.com/upload/media/product/productsearch/datasheet/rchip/PYu-RC_Group_51_RoHS_L_11.pdf" H 7850 3500 50  0001 C CNN
F 4 "RC2010JK-0710KL" H 7850 3500 50  0001 C CNN "part_number"
F 5 "YAGEO" H 7850 3500 50  0001 C CNN "Manufacturer"
F 6 "" H 7850 3500 50  0001 C CNN "Vendor"
F 7 "RC2010JK-0710KL" H 7850 3500 50  0001 C CNN "Part"
	1    7850 3500
	0    1    1    0   
$EndComp
Wire Wire Line
	8000 3500 8100 3500
Connection ~ 8100 3500
Wire Wire Line
	8100 2650 8100 3500
Wire Wire Line
	6950 2250 7250 2250
$Comp
L Device:CP1 C5
U 1 1 617B1883
P 7550 2400
F 0 "C5" H 7665 2446 50  0000 L CNN
F 1 "100nF" H 7665 2355 50  0000 L CNN
F 2 "Capacitor_SMD:CP_Elec_4x4.5" H 7550 2400 50  0001 C CNN
F 3 "https://www.we-online.de/katalog/datasheet/865230640001.pdf" H 7550 2400 50  0001 C CNN
F 4 "865230640001" H 7550 2400 50  0001 C CNN "part_number"
F 5 "Würth Elektronik" H 7550 2400 50  0001 C CNN "Manufacturer"
F 6 "" H 7550 2400 50  0001 C CNN "Vendor"
F 7 "865230640001" H 7550 2400 50  0001 C CNN "Part"
	1    7550 2400
	1    0    0    -1  
$EndComp
Wire Wire Line
	8150 1500 7900 1500
Wire Wire Line
	8700 2150 8700 1500
Wire Wire Line
	8700 1500 8450 1500
Connection ~ 8700 2150
Wire Wire Line
	8700 2150 9050 2150
Connection ~ 7700 3150
Wire Wire Line
	7700 3150 7700 3500
Connection ~ 7550 2250
Wire Wire Line
	7550 2250 7700 2250
$Comp
L power:Earth #PWR0110
U 1 1 618910BE
P 7550 2550
F 0 "#PWR0110" H 7550 2300 50  0001 C CNN
F 1 "Earth" H 7550 2400 50  0001 C CNN
F 2 "" H 7550 2550 50  0001 C CNN
F 3 "~" H 7550 2550 50  0001 C CNN
	1    7550 2550
	1    0    0    -1  
$EndComp
Connection ~ 7250 2250
Wire Wire Line
	7250 2250 7300 2250
Wire Wire Line
	3000 4000 2950 4000
Wire Wire Line
	3000 3900 2900 3900
Wire Wire Line
	3000 3700 5050 3700
Connection ~ 3000 3700
Wire Wire Line
	5200 3600 3000 3600
Connection ~ 3000 3600
$Comp
L power:Earth #PWR0111
U 1 1 6195680C
P 3600 3750
F 0 "#PWR0111" H 3600 3500 50  0001 C CNN
F 1 "Earth" H 3600 3600 50  0001 C CNN
F 2 "" H 3600 3750 50  0001 C CNN
F 3 "~" H 3600 3750 50  0001 C CNN
	1    3600 3750
	1    0    0    -1  
$EndComp
Wire Wire Line
	3000 3800 3450 3800
Wire Wire Line
	3450 3800 3450 3750
Wire Wire Line
	3450 3750 3600 3750
Connection ~ 3000 3800
Wire Wire Line
	7900 4150 7650 4150
Wire Wire Line
	7650 4150 7650 4300
$Comp
L power:Earth #PWR0112
U 1 1 61990DB5
P 7650 4300
F 0 "#PWR0112" H 7650 4050 50  0001 C CNN
F 1 "Earth" H 7650 4150 50  0001 C CNN
F 2 "" H 7650 4300 50  0001 C CNN
F 3 "~" H 7650 4300 50  0001 C CNN
	1    7650 4300
	1    0    0    -1  
$EndComp
$Comp
L Transistor_FET:Si2319CDS Q1
U 1 1 619D1B75
P 4000 4200
F 0 "Q1" H 4205 4154 50  0000 L CNN
F 1 "BSS806NH6327XTSA1" H 5100 4650 50  0000 L CNN
F 2 "Package_TO_SOT_SMD:SOT-23" H 4200 4125 50  0001 L CIN
F 3 "https://www.infineon.com/dgdl/BSS806N_Rev2.3_.pdf?folderId=db3a3043156fd573011622e10b5c1f67&fileId=db3a304330f686060131185f0553451c" H 4000 4200 50  0001 L CNN
F 4 "Infineon Technologies" H 4000 4200 50  0001 C CNN "Manufacturer"
F 5 "BSS806NH6327XTSA1" H 4000 4200 50  0001 C CNN "part_number"
F 6 "" H 4000 4200 50  0001 C CNN "Vendor"
F 7 "BSS806NH6327XTSA1" H 4000 4200 50  0001 C CNN "Part"
	1    4000 4200
	-1   0    0    1   
$EndComp
$Comp
L Device:R R7
U 1 1 61A13B53
P 4750 4350
F 0 "R7" V 4957 4350 50  0000 C CNN
F 1 "10k" V 4866 4350 50  0000 C CNN
F 2 "Resistor_SMD:R_2010_5025Metric" V 4680 4350 50  0001 C CNN
F 3 "https://www.yageo.com/upload/media/product/productsearch/datasheet/rchip/PYu-RC_Group_51_RoHS_L_11.pdf" H 4750 4350 50  0001 C CNN
F 4 "RC2010JK-0710KL" H 4750 4350 50  0001 C CNN "part_number"
F 5 "YAGEO" H 4750 4350 50  0001 C CNN "Manufacturer"
F 6 "" H 4750 4350 50  0001 C CNN "Vendor"
F 7 "RC2010JK-0710KL" H 4750 4350 50  0001 C CNN "Part"
	1    4750 4350
	1    0    0    -1  
$EndComp
Wire Wire Line
	4750 4200 4200 4200
Wire Wire Line
	7900 4150 7900 4250
Wire Wire Line
	5550 4300 5550 4550
Wire Wire Line
	5050 3700 5050 4650
Connection ~ 5100 2250
$Comp
L power:+5V #PWR0113
U 1 1 613DA831
P 7300 2250
F 0 "#PWR0113" H 7300 2100 50  0001 C CNN
F 1 "+5V" H 7315 2423 50  0000 C CNN
F 2 "" H 7300 2250 50  0001 C CNN
F 3 "" H 7300 2250 50  0001 C CNN
	1    7300 2250
	1    0    0    -1  
$EndComp
$Comp
L power:+5V #PWR0114
U 1 1 613DBCF2
P 7450 2250
F 0 "#PWR0114" H 7450 2100 50  0001 C CNN
F 1 "+5V" H 7465 2423 50  0000 C CNN
F 2 "" H 7450 2250 50  0001 C CNN
F 3 "" H 7450 2250 50  0001 C CNN
	1    7450 2250
	1    0    0    -1  
$EndComp
Wire Wire Line
	7450 2250 7550 2250
$Comp
L power:+5V #PWR0115
U 1 1 613DEB6E
P 8800 3850
F 0 "#PWR0115" H 8800 3700 50  0001 C CNN
F 1 "+5V" H 8815 4023 50  0000 C CNN
F 2 "" H 8800 3850 50  0001 C CNN
F 3 "" H 8800 3850 50  0001 C CNN
	1    8800 3850
	1    0    0    -1  
$EndComp
$Comp
L power:+5V #PWR0116
U 1 1 613E357C
P 4150 3900
F 0 "#PWR0116" H 4150 3750 50  0001 C CNN
F 1 "+5V" H 4165 4073 50  0000 C CNN
F 2 "" H 4150 3900 50  0001 C CNN
F 3 "" H 4150 3900 50  0001 C CNN
	1    4150 3900
	1    0    0    -1  
$EndComp
$Comp
L power:+5V #PWR0117
U 1 1 613E427A
P 5300 3750
F 0 "#PWR0117" H 5300 3600 50  0001 C CNN
F 1 "+5V" H 5315 3923 50  0000 C CNN
F 2 "" H 5300 3750 50  0001 C CNN
F 3 "" H 5300 3750 50  0001 C CNN
	1    5300 3750
	1    0    0    -1  
$EndComp
Wire Wire Line
	5300 3750 5200 3750
Wire Wire Line
	5200 3750 5200 3600
$Comp
L power:+5V #PWR0118
U 1 1 613FA3A6
P 4800 3500
F 0 "#PWR0118" H 4800 3350 50  0001 C CNN
F 1 "+5V" H 4815 3673 50  0000 C CNN
F 2 "" H 4800 3500 50  0001 C CNN
F 3 "" H 4800 3500 50  0001 C CNN
	1    4800 3500
	1    0    0    -1  
$EndComp
Wire Wire Line
	8100 3500 8100 4050
Wire Wire Line
	8200 3150 8200 3950
$Comp
L Connector:Conn_01x02_Male J3
U 1 1 61484E4C
P 9550 5000
F 0 "J3" H 9612 5044 50  0000 L CNN
F 1 "Conn_01x02_Male" H 9300 5150 50  0000 L CNN
F 2 "Connector_PinHeader_2.54mm:PinHeader_1x02_P2.54mm_Vertical" H 9550 5000 50  0001 C CNN
F 3 "~" H 9550 5000 50  0001 C CNN
	1    9550 5000
	-1   0    0    1   
$EndComp
Wire Wire Line
	4750 5100 9900 5100
$Comp
L power:+3.3V #PWR0119
U 1 1 614AB6FD
P 8300 3850
F 0 "#PWR0119" H 8300 3700 50  0001 C CNN
F 1 "+3.3V" H 8315 4023 50  0000 C CNN
F 2 "" H 8300 3850 50  0001 C CNN
F 3 "" H 8300 3850 50  0001 C CNN
	1    8300 3850
	1    0    0    -1  
$EndComp
$Comp
L power:+3.3V #PWR0120
U 1 1 614ACC28
P 9350 4900
F 0 "#PWR0120" H 9350 4750 50  0001 C CNN
F 1 "+3.3V" H 9250 4850 50  0000 C CNN
F 2 "" H 9350 4900 50  0001 C CNN
F 3 "" H 9350 4900 50  0001 C CNN
	1    9350 4900
	1    0    0    -1  
$EndComp
Wire Wire Line
	9350 5000 9100 5000
Wire Wire Line
	8300 3950 8200 3950
Wire Wire Line
	8300 4050 8100 4050
Wire Wire Line
	8800 4150 8750 4150
Wire Wire Line
	8800 3850 8800 3950
Connection ~ 8800 3850
Wire Wire Line
	8750 4050 8800 4050
Connection ~ 8800 4050
Wire Wire Line
	8800 4050 8950 4050
Wire Wire Line
	8950 4050 8950 4450
Wire Wire Line
	8950 4450 8800 4450
Wire Wire Line
	9900 4550 8800 4550
Wire Wire Line
	9900 4550 9900 5100
Wire Wire Line
	9100 4650 8800 4650
Wire Wire Line
	9100 4650 9100 5000
Wire Wire Line
	8300 4250 7900 4250
Wire Wire Line
	8300 4350 7850 4350
Wire Wire Line
	7850 4350 7850 4550
Wire Wire Line
	7850 4550 5550 4550
Wire Wire Line
	8300 4450 7950 4450
Wire Wire Line
	7950 4450 7950 4650
Wire Wire Line
	7950 4650 5050 4650
$Comp
L Device:R R8
U 1 1 614F2EDD
P 3650 4400
F 0 "R8" V 3857 4400 50  0000 C CNN
F 1 "5.5Ω" V 3766 4400 50  0000 C CNN
F 2 "Resistor_SMD:R_2010_5025Metric" V 3580 4400 50  0001 C CNN
F 3 "https://www.yageo.com/upload/media/product/productsearch/datasheet/rchip/PYu-AC_51_RoHS_L_7.pdf" H 3650 4400 50  0001 C CNN
F 4 "AC2010JK-07560RL" H 3650 4400 50  0001 C CNN "part_number"
F 5 "YAGEO" H 3650 4400 50  0001 C CNN "Manufacturer"
F 6 "" H 3650 4400 50  0001 C CNN "Vendor"
F 7 "AC2010JK-07560RL" H 3650 4400 50  0001 C CNN "Part"
	1    3650 4400
	0    -1   -1   0   
$EndComp
Wire Wire Line
	4750 4500 4750 5100
Wire Wire Line
	3900 4000 4300 4000
Wire Wire Line
	3800 4400 3900 4400
Connection ~ 3000 4000
Wire Wire Line
	3500 4400 3500 4000
Wire Wire Line
	3500 4000 3000 4000
Connection ~ 3000 3900
Wire Wire Line
	3000 3900 4150 3900
Wire Wire Line
	4800 2750 4800 3200
Wire Wire Line
	4800 3200 5550 3200
Wire Wire Line
	5550 3200 5550 4000
$Comp
L power:Earth #PWR0103
U 1 1 613C9F6B
P 5100 2550
F 0 "#PWR0103" H 5100 2300 50  0001 C CNN
F 1 "Earth" H 5100 2400 50  0001 C CNN
F 2 "" H 5100 2550 50  0001 C CNN
F 3 "~" H 5100 2550 50  0001 C CNN
	1    5100 2550
	1    0    0    -1  
$EndComp
Wire Wire Line
	5100 2250 4900 2250
$Comp
L Device:C C1
U 1 1 613C0503
P 5100 2400
F 0 "C1" H 5215 2446 50  0000 L CNN
F 1 "10μF" H 5215 2355 50  0000 L CNN
F 2 "Capacitor_SMD:C_1206_3216Metric" H 5138 2250 50  0001 C CNN
F 3 "https://global.kyocera.com/prdct/electro/product/pdf/cm_e.pdf" H 5100 2400 50  0001 C CNN
F 4 "CM316X5R106K10AT" H 5100 2400 50  0001 C CNN "part_number"
F 5 "Kyocera International Inc. Electronic Components" H 5100 2400 50  0001 C CNN "Manufacturer"
F 6 "" H 5100 2400 50  0001 C CNN "Vendor"
F 7 "CM316X5R106K10AT" H 5100 2400 50  0001 C CNN "Part"
	1    5100 2400
	1    0    0    -1  
$EndComp
Connection ~ 4900 2250
Wire Wire Line
	4900 2250 4300 2250
$Comp
L Transistor_FET:BSS84 Q2
U 1 1 6167A20B
P 5250 2850
F 0 "Q2" V 5499 2850 50  0000 C CNN
F 1 "AO3415A" V 5590 2850 50  0000 C CNN
F 2 "Package_TO_SOT_SMD:SOT-23" H 5450 2775 50  0001 L CIN
F 3 "https://media.digikey.com/pdf/Data%20Sheets/Alpha%20&%20Omega/AO3415A.pdf" H 5250 2850 50  0001 L CNN
F 4 "Alpha & Omega Semiconductor Inc." H 5250 2850 50  0001 C CNN "Manufacturer"
F 5 "AO3415A" H 5250 2850 50  0001 C CNN "Part"
F 6 "AO3415A" H 5250 2850 50  0001 C CNN "part_number"
	1    5250 2850
	0    1    1    0   
$EndComp
Wire Wire Line
	5600 2950 5450 2950
Connection ~ 5450 2950
Wire Wire Line
	5450 2950 5400 2950
Wire Wire Line
	4800 2650 5250 2650
Wire Wire Line
	5050 2950 4900 2950
Wire Wire Line
	4900 2250 4900 2950
$EndSCHEMATC
