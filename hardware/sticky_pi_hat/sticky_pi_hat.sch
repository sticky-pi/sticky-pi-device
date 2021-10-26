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
L Device:R R3
U 1 1 613829B2
P 7350 1850
F 0 "R3" V 7250 1750 50  0000 C CNN
F 1 "100Ω" V 7350 1850 50  0000 C CNN
F 2 "Resistor_SMD:R_2010_5025Metric" V 7280 1850 50  0001 C CNN
F 3 "https://www.koaspeer.com/pdfs/RK73H.pdf" H 7350 1850 50  0001 C CNN
F 4 "RC2010JK-0710KL" H 7350 1850 50  0001 C CNN "part_number"
F 5 "KOA Speer Electronics, Inc." H 7350 1850 50  0001 C CNN "Manufacturer"
F 6 "" H 7350 1850 50  0001 C CNN "Vendor"
F 7 "RC2010JK-0710KL" H 7350 1850 50  0001 C CNN "Part"
	1    7350 1850
	-1   0    0    1   
$EndComp
$Comp
L Device:R R1
U 1 1 6138329F
P 4650 1900
F 0 "R1" V 4750 1950 50  0000 C CNN
F 1 "75k" V 4650 1900 50  0000 C CNN
F 2 "Resistor_SMD:R_2010_5025Metric" V 4580 1900 50  0001 C CNN
F 3 "https://www.koaspeer.com/pdfs/RK73H.pdf" H 4650 1900 50  0001 C CNN
F 4 "RK73H2HTTE7502F" H 4650 1900 50  0001 C CNN "part_number"
F 5 "KOA Speer Electronics, Inc." H 4650 1900 50  0001 C CNN "Manufacturer"
F 6 "" H 4650 1900 50  0001 C CNN "Vendor"
F 7 "RK73H2HTTE7502F" H 4650 1900 50  0001 C CNN "Part"
	1    4650 1900
	0    -1   -1   0   
$EndComp
$Comp
L power:Earth #PWR0101
U 1 1 61383BCF
P 5050 1900
F 0 "#PWR0101" H 5050 1650 50  0001 C CNN
F 1 "Earth" H 5050 1750 50  0001 C CNN
F 2 "" H 5050 1900 50  0001 C CNN
F 3 "~" H 5050 1900 50  0001 C CNN
	1    5050 1900
	1    0    0    -1  
$EndComp
Wire Wire Line
	4900 1850 4900 1900
Wire Wire Line
	7550 1800 7550 1700
$Comp
L Regulator_Switching:TPS63002 U3
U 1 1 6136C756
P 7950 1800
F 0 "U3" H 7950 2467 50  0000 C CNN
F 1 "TPS63002" H 7950 2376 50  0000 C CNN
F 2 "Package_SON:Texas_DSC0010J_ThermalVias" H 8800 1250 50  0001 C CNN
F 3 "http://www.ti.com/lit/ds/symlink/tps63002.pdf" H 7650 2350 50  0001 C CNN
F 4 "Texas Instruments" H 7950 1800 50  0001 C CNN "Manufacturer"
F 5 "TPS63002DRCR" H 7950 1800 50  0001 C CNN "part_number"
F 6 "" H 7950 1800 50  0001 C CNN "Vendor"
F 7 "TPS63002DRCR" H 7950 1800 50  0001 C CNN "Part"
	1    7950 1800
	1    0    0    -1  
$EndComp
Connection ~ 7550 1800
Connection ~ 7550 2000
Wire Wire Line
	7550 2000 7550 1800
$Comp
L Timer:TPL5110 U2
U 1 1 6136C237
P 4900 1350
F 0 "U2" H 4600 1850 50  0000 C CNN
F 1 "TPL5110" H 4650 1750 50  0000 C CNN
F 2 "Package_TO_SOT_SMD:SOT-23-6" H 4900 1350 50  0001 C CNN
F 3 "http://www.ti.com/lit/ds/symlink/tpl5110.pdf" H 4700 950 50  0001 C CNN
F 4 "Texas Instruments" H 4900 1350 50  0001 C CNN "Manufacturer"
F 5 "TPL5110QDDCTQ1" H 4900 1350 50  0001 C CNN "part_number"
F 6 "" H 4900 1350 50  0001 C CNN "Vendor"
F 7 "TPL5110QDDCTQ1" H 4900 1350 50  0001 C CNN "Part"
	1    4900 1350
	1    0    0    -1  
$EndComp
$Comp
L power:Earth #PWR0102
U 1 1 613B7C69
P 8150 2400
F 0 "#PWR0102" H 8150 2150 50  0001 C CNN
F 1 "Earth" H 8150 2250 50  0001 C CNN
F 2 "" H 8150 2400 50  0001 C CNN
F 3 "~" H 8150 2400 50  0001 C CNN
	1    8150 2400
	1    0    0    -1  
$EndComp
Wire Wire Line
	7950 2400 7850 2400
Connection ~ 7850 2400
Wire Wire Line
	4300 1350 4150 1350
$Comp
L Switch:SW_Push SW1
U 1 1 613B9875
P 2100 3200
F 0 "SW1" H 2100 3485 50  0000 C CNN
F 1 "SW_Push" H 2100 3394 50  0000 C CNN
F 2 "#none" H 2100 3400 50  0001 C CNN
F 3 "~" H 2100 3400 50  0001 C CNN
F 4 "#none" H 2100 3200 50  0001 C CNN "Manufacturer"
F 5 "#none" H 2100 3200 50  0001 C CNN "Part"
	1    2100 3200
	1    0    0    -1  
$EndComp
$Comp
L Device:L L1
U 1 1 613BC649
P 7950 1050
F 0 "L1" V 7769 1050 50  0000 C CNN
F 1 "2.2μH" V 7860 1050 50  0000 C CNN
F 2 "Inductor_SMD:L_Abracon_ASPI-3012S" H 7950 1050 50  0001 C CNN
F 3 "https://product.tdk.com/en/system/files?file=dam/doc/product/inductor/inductor/smd/catalog/inductor_commercial_power_vls3012hbx_en.pdf" H 7950 1050 50  0001 C CNN
F 4 "VLS3012HBX-2R2M" V 7950 1050 50  0001 C CNN "part_number"
F 5 "TDK Corporation" H 7950 1050 50  0001 C CNN "Manufacturer"
F 6 "" H 7950 1050 50  0001 C CNN "Vendor"
F 7 "VLS3012HBX-2R2M" H 7950 1050 50  0001 C CNN "Part"
	1    7950 1050
	0    1    1    0   
$EndComp
Wire Wire Line
	8350 1400 8350 1050
Wire Wire Line
	8350 1050 8100 1050
Wire Wire Line
	7800 1050 7550 1050
Wire Wire Line
	7550 1050 7550 1400
$Comp
L Device:C C2
U 1 1 613BF7CA
P 7500 2400
F 0 "C2" V 7248 2400 50  0000 C CNN
F 1 "0.1μF" V 7339 2400 50  0000 C CNN
F 2 "Capacitor_SMD:C_1206_3216Metric" H 7538 2250 50  0001 C CNN
F 3 "https://content.kemet.com/datasheets/KEM_C1002_X7R_SMD.pdf" H 7500 2400 50  0001 C CNN
F 4 "C1206C104K8RAC7800" H 7500 2400 50  0001 C CNN "part_number"
F 5 "KEMET" H 7500 2400 50  0001 C CNN "Manufacturer"
F 6 "" H 7500 2400 50  0001 C CNN "Vendor"
F 7 "C1206C104K8RAC7800" H 7500 2400 50  0001 C CNN "Part"
	1    7500 2400
	0    1    1    0   
$EndComp
$Comp
L Device:C C4
U 1 1 613BFECA
P 8900 1750
F 0 "C4" H 8750 1850 50  0000 L CNN
F 1 "10μF" H 8800 1650 50  0000 L CNN
F 2 "Capacitor_SMD:C_1206_3216Metric" H 8938 1600 50  0001 C CNN
F 3 "https://global.kyocera.com/prdct/electro/product/pdf/cm_e.pdf" H 8900 1750 50  0001 C CNN
F 4 "CM316X5R106K10AT" H 8900 1750 50  0001 C CNN "part_number"
F 5 "Kyocera International Inc. Electronic Components" H 8900 1750 50  0001 C CNN "Manufacturer"
F 6 "" H 8900 1750 50  0001 C CNN "Vendor"
F 7 "CM316X5R106K10AT" H 8900 1750 50  0001 C CNN "Part"
	1    8900 1750
	1    0    0    -1  
$EndComp
$Comp
L Device:C C3
U 1 1 613C025D
P 8600 1750
F 0 "C3" H 8450 1850 50  0000 L CNN
F 1 "10μF" H 8500 1650 50  0000 L CNN
F 2 "Capacitor_SMD:C_1206_3216Metric" H 8638 1600 50  0001 C CNN
F 3 "https://global.kyocera.com/prdct/electro/product/pdf/cm_e.pdf" H 8600 1750 50  0001 C CNN
F 4 "CM316X5R106K10AT" H 8600 1750 50  0001 C CNN "part_number"
F 5 "Kyocera International Inc. Electronic Components" H 8600 1750 50  0001 C CNN "Manufacturer"
F 6 "" H 8600 1750 50  0001 C CNN "Vendor"
F 7 "CM316X5R106K10AT" H 8600 1750 50  0001 C CNN "Part"
	1    8600 1750
	1    0    0    -1  
$EndComp
Wire Wire Line
	7350 2000 7350 2400
Wire Wire Line
	7350 2000 7550 2000
Wire Wire Line
	7600 2400 7650 2400
Connection ~ 7650 2400
Wire Wire Line
	7650 2400 7850 2400
Wire Wire Line
	8350 1800 8350 1600
Wire Wire Line
	8350 1600 8600 1600
Connection ~ 8350 1600
Connection ~ 8600 1600
$Comp
L power:Earth #PWR0104
U 1 1 613CD4D4
P 8600 1900
F 0 "#PWR0104" H 8600 1650 50  0001 C CNN
F 1 "Earth" H 8600 1750 50  0001 C CNN
F 2 "" H 8600 1900 50  0001 C CNN
F 3 "~" H 8600 1900 50  0001 C CNN
	1    8600 1900
	1    0    0    -1  
$EndComp
$Comp
L power:Earth #PWR0105
U 1 1 613CD9F7
P 8900 1900
F 0 "#PWR0105" H 8900 1650 50  0001 C CNN
F 1 "Earth" H 8900 1750 50  0001 C CNN
F 2 "" H 8900 1900 50  0001 C CNN
F 3 "~" H 8900 1900 50  0001 C CNN
	1    8900 1900
	1    0    0    -1  
$EndComp
Connection ~ 8450 4400
Wire Wire Line
	8450 4400 8650 4400
Wire Wire Line
	8650 3650 8650 4300
$Comp
L Connector:Screw_Terminal_01x11 J1
U 1 1 613EDD1C
P 3200 3500
F 0 "J1" H 3150 2900 50  0000 L CNN
F 1 "Screw_Terminal_01x11" H 2600 2650 50  0000 L CNN
F 2 "TerminalBlock_TE-Connectivity:TerminalBlock_TE_1-282834-1_1x11_P2.54mm_Horizontal" H 3200 3500 50  0001 C CNN
F 3 "https://www.aliexpress.com/item/33010961562.html?spm=a2g0o.productlist.0.0.48c03c2cpAilqm&algo_pvid=d662f399-6825-4aba-b03d-2694688fa9f9&algo_exp_id=d662f399-6825-4aba-b03d-2694688fa9f9-37&pdp_ext_f=%7B%22sku_id%22%3A%2210000000147204690%22%7D" H 3200 3500 50  0001 C CNN
F 4 "" H 3200 3500 50  0001 C CNN "part_number"
F 5 "#none" H 3200 3500 50  0001 C CNN "Manufacturer"
F 6 "#none" H 3200 3500 50  0001 C CNN "Part"
	1    3200 3500
	1    0    0    -1  
$EndComp
Wire Wire Line
	3000 3200 2300 3200
Wire Wire Line
	4300 1450 4300 1900
Connection ~ 3000 3300
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
Connection ~ 3000 3000
Wire Wire Line
	3000 3100 2850 3100
Connection ~ 3000 3100
$Comp
L Device:Battery_Cell BT1
U 1 1 613E98EC
P 2850 2750
F 0 "BT1" H 2550 2850 50  0000 L CNN
F 1 "Battery_Cell" H 2400 2950 50  0000 L CNN
F 2 "#none" V 2850 2810 50  0001 C CNN
F 3 "~" V 2850 2810 50  0001 C CNN
F 4 "CR1220" H 2850 2750 50  0001 C CNN "part_number"
F 5 "CR1220" H 2850 2750 50  0001 C CNN "Part"
	1    2850 2750
	1    0    0    -1  
$EndComp
Connection ~ 3000 3200
Wire Wire Line
	3350 3100 3350 2900
Wire Wire Line
	3350 2900 3450 2900
$Comp
L power:Earth #PWR0107
U 1 1 61458F16
P 9800 4300
F 0 "#PWR0107" H 9800 4050 50  0001 C CNN
F 1 "Earth" H 9800 4150 50  0001 C CNN
F 2 "" H 9800 4300 50  0001 C CNN
F 3 "~" H 9800 4300 50  0001 C CNN
	1    9800 4300
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
F 5 "#none" H 2250 3400 50  0001 C CNN "Manufacturer"
F 6 "WP7113SECK/J3" H 2250 3400 50  0001 C CNN "Part"
	1    2250 3400
	-1   0    0    1   
$EndComp
Wire Wire Line
	3000 3400 2400 3400
$Comp
L Device:R R2
U 1 1 6146BE2F
P 3550 3500
F 0 "R2" V 3600 3650 50  0000 C CNN
F 1 "560Ω" V 3550 3500 50  0000 C CNN
F 2 "Resistor_SMD:R_2010_5025Metric" V 3480 3500 50  0001 C CNN
F 3 "https://www.yageo.com/upload/media/product/productsearch/datasheet/rchip/PYu-AC_51_RoHS_L_7.pdf" H 3550 3500 50  0001 C CNN
F 4 "AC2010JK-07560RL" H 3550 3500 50  0001 C CNN "part_number"
F 5 "YAGEO" H 3550 3500 50  0001 C CNN "Manufacturer"
F 6 "" H 3550 3500 50  0001 C CNN "Vendor"
F 7 "AC2010JK-07560RL" H 3550 3500 50  0001 C CNN "Part"
	1    3550 3500
	0    -1   -1   0   
$EndComp
Wire Wire Line
	3000 3600 1900 3600
Wire Wire Line
	3000 3800 1900 3800
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
F 4 "#none" H 1650 3700 50  0001 C CNN "Manufacturer"
F 5 "#none" H 1650 3700 50  0001 C CNN "Part"
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
P 2650 4000
F 0 "D1" H 2643 4217 50  0000 C CNN
F 1 "LED" H 2643 4126 50  0000 C CNN
F 2 "#none" H 2650 4000 50  0001 C CNN
F 3 "~" H 2650 4000 50  0001 C CNN
F 4 "500mA at 5V. Adding a 5.5R resistor reduces current to 200mA" H 2650 4000 50  0001 C CNN "Notes"
F 5 "#none" H 2650 4000 50  0001 C CNN "Manufacturer"
F 6 "#none" H 2650 4000 50  0001 C CNN "Part"
	1    2650 4000
	-1   0    0    1   
$EndComp
$Comp
L power:Earth #PWR0108
U 1 1 615E52C8
P 4200 4000
F 0 "#PWR0108" H 4200 3750 50  0001 C CNN
F 1 "Earth" H 4200 3850 50  0001 C CNN
F 2 "" H 4200 4000 50  0001 C CNN
F 3 "~" H 4200 4000 50  0001 C CNN
	1    4200 4000
	1    0    0    -1  
$EndComp
Wire Wire Line
	8950 4800 8950 5300
$Comp
L Device:Crystal Y1
U 1 1 616F7111
P 9300 5000
F 0 "Y1" H 9300 5000 50  0000 C CNN
F 1 "Crystal" H 9500 4850 50  0000 C CNN
F 2 "Crystal:Crystal_SMD_MicroCrystal_CM9V-T1A-2Pin_1.6x1.0mm" H 9300 5000 50  0001 C CNN
F 3 "https://www.microcrystal.com/fileadmin/Media/Products/32kHz/Datasheet/CM9V-T1A.pdf" H 9300 5000 50  0001 C CNN
F 4 "CM9V-T1A" H 9300 5000 50  0001 C CNN "part_number"
F 5 "Micro Crystal AG" H 9300 5000 50  0001 C CNN "Manufacturer"
F 6 "" H 9300 5000 50  0001 C CNN "Vendor"
F 7 "CM9V-T1A-32.768KHZ-12.5PF-20PPM-TA-QC" H 9300 5000 50  0001 C CNN "Part"
	1    9300 5000
	1    0    0    -1  
$EndComp
Wire Wire Line
	9150 4800 9150 5000
Wire Wire Line
	9450 5000 9500 5000
Wire Wire Line
	9500 5000 9500 4800
Wire Wire Line
	9500 4800 9250 4800
$Comp
L Device:R R5
U 1 1 61708319
P 8600 5300
F 0 "R5" V 8500 5300 50  0000 C CNN
F 1 "10k" V 8600 5300 50  0000 C CNN
F 2 "Resistor_SMD:R_2010_5025Metric" V 8530 5300 50  0001 C CNN
F 3 "https://www.yageo.com/upload/media/product/productsearch/datasheet/rchip/PYu-RC_Group_51_RoHS_L_11.pdf" H 8600 5300 50  0001 C CNN
F 4 "RC2010JK-0710KL" H 8600 5300 50  0001 C CNN "part_number"
F 5 "YAGEO" H 8600 5300 50  0001 C CNN "Manufacturer"
F 6 "" H 8600 5300 50  0001 C CNN "Vendor"
F 7 "RC2010JK-0710KL" H 8600 5300 50  0001 C CNN "Part"
	1    8600 5300
	0    1    1    0   
$EndComp
Wire Wire Line
	8750 5300 8950 5300
Wire Wire Line
	8600 1600 8900 1600
$Comp
L Device:CP1 C5
U 1 1 617B1883
P 8300 4550
F 0 "C5" H 8100 4650 50  0000 L CNN
F 1 "100nF" H 8100 4450 50  0000 L CNN
F 2 "Capacitor_SMD:CP_Elec_4x4.5" H 8300 4550 50  0001 C CNN
F 3 "https://www.we-online.de/katalog/datasheet/865230640001.pdf" H 8300 4550 50  0001 C CNN
F 4 "865230640001" H 8300 4550 50  0001 C CNN "part_number"
F 5 "Würth Elektronik" H 8300 4550 50  0001 C CNN "Manufacturer"
F 6 "" H 8300 4550 50  0001 C CNN "Vendor"
F 7 "865230640001" H 8300 4550 50  0001 C CNN "Part"
	1    8300 4550
	1    0    0    -1  
$EndComp
Wire Wire Line
	9450 4300 9800 4300
Connection ~ 8300 4400
Wire Wire Line
	8300 4400 8450 4400
$Comp
L power:Earth #PWR0110
U 1 1 618910BE
P 8300 4700
F 0 "#PWR0110" H 8300 4450 50  0001 C CNN
F 1 "Earth" H 8300 4550 50  0001 C CNN
F 2 "" H 8300 4700 50  0001 C CNN
F 3 "~" H 8300 4700 50  0001 C CNN
	1    8300 4700
	1    0    0    -1  
$EndComp
Connection ~ 8900 1600
Wire Wire Line
	8900 1600 8950 1600
Connection ~ 3000 3600
$Comp
L Device:R R7
U 1 1 61A13B53
P 4150 4300
F 0 "R7" V 4250 4300 50  0000 C CNN
F 1 "10k" V 4150 4300 50  0000 C CNN
F 2 "Resistor_SMD:R_2010_5025Metric" V 4080 4300 50  0001 C CNN
F 3 "https://www.yageo.com/upload/media/product/productsearch/datasheet/rchip/PYu-RC_Group_51_RoHS_L_11.pdf" H 4150 4300 50  0001 C CNN
F 4 "RC2010JK-0710KL" H 4150 4300 50  0001 C CNN "part_number"
F 5 "YAGEO" H 4150 4300 50  0001 C CNN "Manufacturer"
F 6 "" H 4150 4300 50  0001 C CNN "Vendor"
F 7 "RC2010JK-0710KL" H 4150 4300 50  0001 C CNN "Part"
	1    4150 4300
	0    -1   -1   0   
$EndComp
$Comp
L power:+5V #PWR0113
U 1 1 613DA831
P 8950 1600
F 0 "#PWR0113" H 8950 1450 50  0001 C CNN
F 1 "+5V" H 8965 1773 50  0000 C CNN
F 2 "" H 8950 1600 50  0001 C CNN
F 3 "" H 8950 1600 50  0001 C CNN
	1    8950 1600
	1    0    0    -1  
$EndComp
$Comp
L power:+5V #PWR0114
U 1 1 613DBCF2
P 8200 4400
F 0 "#PWR0114" H 8200 4250 50  0001 C CNN
F 1 "+5V" H 8215 4573 50  0000 C CNN
F 2 "" H 8200 4400 50  0001 C CNN
F 3 "" H 8200 4400 50  0001 C CNN
	1    8200 4400
	1    0    0    -1  
$EndComp
Wire Wire Line
	8200 4400 8300 4400
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
L power:+5V #PWR0118
U 1 1 613FA3A6
P 3700 3500
F 0 "#PWR0118" H 3700 3350 50  0001 C CNN
F 1 "+5V" H 3800 3550 50  0000 C CNN
F 2 "" H 3700 3500 50  0001 C CNN
F 3 "" H 3700 3500 50  0001 C CNN
	1    3700 3500
	1    0    0    -1  
$EndComp
$Comp
L Connector:Conn_01x02_Male J3
U 1 1 61484E4C
P 3650 6700
F 0 "J3" H 3712 6744 50  0000 L CNN
F 1 "Conn_01x02_Male" H 3400 6850 50  0000 L CNN
F 2 "Connector_PinHeader_2.54mm:PinHeader_1x02_P2.54mm_Vertical" H 3650 6700 50  0001 C CNN
F 3 "~" H 3650 6700 50  0001 C CNN
F 4 "#none" H 3650 6700 50  0001 C CNN "Manufacturer"
F 5 "#none" H 3650 6700 50  0001 C CNN "Part"
	1    3650 6700
	-1   0    0    1   
$EndComp
$Comp
L power:+3.3V #PWR0120
U 1 1 614ACC28
P 3450 6600
F 0 "#PWR0120" H 3450 6450 50  0001 C CNN
F 1 "+3.3V" H 3450 6750 50  0000 C CNN
F 2 "" H 3450 6600 50  0001 C CNN
F 3 "" H 3450 6600 50  0001 C CNN
	1    3450 6600
	1    0    0    -1  
$EndComp
$Comp
L Device:R R8
U 1 1 614F2EDD
P 3650 4000
F 0 "R8" V 3550 4000 50  0000 C CNN
F 1 "5.5Ω" V 3650 4000 50  0000 C CNN
F 2 "Resistor_SMD:R_2010_5025Metric" V 3580 4000 50  0001 C CNN
F 3 "https://www.yageo.com/upload/media/product/productsearch/datasheet/rchip/PYu-AC_51_RoHS_L_7.pdf" H 3650 4000 50  0001 C CNN
F 4 "RC2010FK-075R49L" H 3650 4000 50  0001 C CNN "part_number"
F 5 "YAGEO" H 3650 4000 50  0001 C CNN "Manufacturer"
F 6 "" H 3650 4000 50  0001 C CNN "Vendor"
F 7 "RC2010FK-075R49L" H 3650 4000 50  0001 C CNN "Part"
	1    3650 4000
	0    -1   -1   0   
$EndComp
Connection ~ 3000 4000
Wire Wire Line
	3500 4000 3000 4000
Connection ~ 3000 3900
Wire Wire Line
	3000 3900 4150 3900
$Comp
L power:Earth #PWR0103
U 1 1 613C9F6B
P 7050 1450
F 0 "#PWR0103" H 7050 1200 50  0001 C CNN
F 1 "Earth" H 7050 1300 50  0001 C CNN
F 2 "" H 7050 1450 50  0001 C CNN
F 3 "~" H 7050 1450 50  0001 C CNN
	1    7050 1450
	1    0    0    -1  
$EndComp
Wire Wire Line
	6750 1600 6550 1600
$Comp
L Device:C C1
U 1 1 613C0503
P 6900 1450
F 0 "C1" V 6950 1300 50  0000 L CNN
F 1 "10μF" V 7050 1350 50  0000 L CNN
F 2 "Capacitor_SMD:C_1206_3216Metric" H 6938 1300 50  0001 C CNN
F 3 "https://global.kyocera.com/prdct/electro/product/pdf/cm_e.pdf" H 6900 1450 50  0001 C CNN
F 4 "CM316X5R106K10AT" H 6900 1450 50  0001 C CNN "part_number"
F 5 "Kyocera International Inc. Electronic Components" H 6900 1450 50  0001 C CNN "Manufacturer"
F 6 "" H 6900 1450 50  0001 C CNN "Vendor"
F 7 "CM316X5R106K10AT" H 6900 1450 50  0001 C CNN "Part"
	1    6900 1450
	0    -1   -1   0   
$EndComp
Wire Wire Line
	3400 3500 3000 3500
Connection ~ 3000 3500
Wire Wire Line
	6300 5450 6300 5350
$Comp
L power:Earth #PWR0121
U 1 1 61749DDC
P 6300 5450
F 0 "#PWR0121" H 6300 5200 50  0001 C CNN
F 1 "Earth" H 6300 5300 50  0001 C CNN
F 2 "" H 6300 5450 50  0001 C CNN
F 3 "~" H 6300 5450 50  0001 C CNN
	1    6300 5450
	1    0    0    -1  
$EndComp
$Comp
L power:Earth #PWR0122
U 1 1 617550CA
P 4050 3450
F 0 "#PWR0122" H 4050 3200 50  0001 C CNN
F 1 "Earth" H 4050 3300 50  0001 C CNN
F 2 "" H 4050 3450 50  0001 C CNN
F 3 "~" H 4050 3450 50  0001 C CNN
	1    4050 3450
	1    0    0    -1  
$EndComp
Connection ~ 3000 3400
Wire Wire Line
	3000 3400 3950 3400
Wire Wire Line
	4050 3450 4050 3400
Connection ~ 4900 1900
Wire Wire Line
	4900 1900 5050 1900
Wire Wire Line
	6900 5250 6850 5250
$Comp
L Diode:SM4001 D3
U 1 1 6184195A
P 6150 5050
F 0 "D3" H 6250 5150 50  0000 C CNN
F 1 "SM4001PL" H 6150 4950 50  0000 C CNN
F 2 "Diode_SMD:D_SOD-123F" H 6150 4875 50  0001 C CNN
F 3 "http://cdn-reichelt.de/documents/datenblatt/A400/SMD1N400%23DIO.pdf" H 6150 5050 50  0001 C CNN
F 4 "Micro Commercial Co" H 6150 5050 50  0001 C CNN "Manufacturer"
F 5 "SM4001PL" H 6150 5050 50  0001 C CNN "Part"
F 6 "SM4001PL" H 6150 5050 50  0001 C CNN "part_number"
	1    6150 5050
	-1   0    0    1   
$EndComp
Wire Wire Line
	5350 6300 5150 6300
$Comp
L power:Earth #PWR0123
U 1 1 618E310E
P 5150 6300
F 0 "#PWR0123" H 5150 6050 50  0001 C CNN
F 1 "Earth" H 5150 6150 50  0001 C CNN
F 2 "" H 5150 6300 50  0001 C CNN
F 3 "~" H 5150 6300 50  0001 C CNN
	1    5150 6300
	1    0    0    -1  
$EndComp
$Comp
L power:+3.3V #PWR0124
U 1 1 618F1751
P 5100 6950
F 0 "#PWR0124" H 5100 6800 50  0001 C CNN
F 1 "+3.3V" H 5115 7123 50  0000 C CNN
F 2 "" H 5100 6950 50  0001 C CNN
F 3 "" H 5100 6950 50  0001 C CNN
	1    5100 6950
	1    0    0    -1  
$EndComp
Wire Wire Line
	5350 7000 5350 6800
Wire Wire Line
	5350 7000 5100 7000
Wire Wire Line
	5100 7000 5100 6950
Text GLabel 4850 6000 0    50   Input ~ 0
drv
$Comp
L power:Earth #PWR0125
U 1 1 619114BA
P 6350 7000
F 0 "#PWR0125" H 6350 6750 50  0001 C CNN
F 1 "Earth" H 6350 6850 50  0001 C CNN
F 2 "" H 6350 7000 50  0001 C CNN
F 3 "~" H 6350 7000 50  0001 C CNN
	1    6350 7000
	1    0    0    -1  
$EndComp
Text GLabel 6350 6200 2    50   Output ~ 0
GPIO_9_MISO
Text GLabel 5350 6600 0    50   Input ~ 0
GPIO_11_clk
Text GLabel 5350 6500 0    50   Input ~ 0
GPIO_8_C0
Connection ~ 9450 4300
Wire Wire Line
	9450 3650 9200 3650
Wire Wire Line
	9450 4300 9450 3650
$Comp
L Timer_RTC:DS1307+ U4
U 1 1 6136FBC0
P 9050 4300
F 0 "U4" V 9594 4346 50  0000 L CNN
F 1 "DS1307Z+" V 8900 4050 50  0000 L CNN
F 2 "Package_SO:SOIC-8_3.9x4.9mm_P1.27mm" H 9050 3800 50  0001 C CNN
F 3 "https://datasheets.maximintegrated.com/en/ds/DS1307.pdf" H 9050 4100 50  0001 C CNN
F 4 "Maxim Integrated" H 9050 4300 50  0001 C CNN "Manufacturer"
F 5 "DS1307+" H 9050 4300 50  0001 C CNN "part_number"
F 6 "" H 9050 4300 50  0001 C CNN "Vendor"
F 7 "DS1307Z+" H 9050 4300 50  0001 C CNN "Part"
	1    9050 4300
	0    -1   -1   0   
$EndComp
Connection ~ 5350 7000
$Comp
L 3001:MCP3001-I_ST U5
U 1 1 618D6486
P 5250 6200
F 0 "U5" H 5850 6465 50  0000 C CNN
F 1 "MCP3001-I_ST" H 5850 6374 50  0000 C CNN
F 2 "Microchip-MCP3001-I_ST-*:Microchip-MCP3001-I_ST-Level_A" H 5250 6600 50  0001 L CNN
F 3 "http://ww1.microchip.com/downloads/en/DeviceDoc/21293C.pdf" H 5250 6700 50  0001 L CNN
F 4 "MO-153" H 5250 6800 50  0001 L CNN "Code  JEDEC"
F 5 "Manufacturer URL" H 5250 6900 50  0001 L CNN "Component Link 1 Description"
F 6 "http://www.microchip.com/" H 5250 7000 50  0001 L CNN "Component Link 1 URL"
F 7 "Package Specification" H 5250 7100 50  0001 L CNN "Component Link 3 Description"
F 8 "http://www.microchip.com/stellent/groups/techpub_sg/documents/packagingspec/en012702.pdf" H 5250 7200 50  0001 L CNN "Component Link 3 URL"
F 9 "revC, Jan-2007" H 5250 7300 50  0001 L CNN "Datasheet Version"
F 10 "8-Lead Plastic Thin Shrink Small Outline (ST) - 4.4mm Body [TSSOP]" H 5250 7400 50  0001 L CNN "Package Description"
F 11 "revBB, Aug-2009" H 5250 7500 50  0001 L CNN "Package Version"
F 12 "IC" H 5250 7600 50  0001 L CNN "category"
F 13 "3238973" H 5250 7700 50  0001 L CNN "ciiva ids"
F 14 "5e7d3c293717b223" H 5250 7800 50  0001 L CNN "library id"
F 15 "Microchip" H 5250 7900 50  0001 L CNN "manufacturer"
F 16 "TSSOP-ST8" H 5250 8000 50  0001 L CNN "package"
F 17 "1331963341" H 5250 8100 50  0001 L CNN "release date"
F 18 "88B0E8EE-158B-47D3-B67F-4A413DE97F63" H 5250 8200 50  0001 L CNN "vault revision"
F 19 "yes" H 5250 8300 50  0001 L CNN "imported"
F 20 "Microchip Technology" H 5250 6200 50  0001 C CNN "Manufacturer"
F 21 "MCP3001-I_ST" H 5250 6200 50  0001 C CNN "part_number"
	1    5250 6200
	1    0    0    -1  
$EndComp
Connection ~ 5150 6300
$Comp
L Device:C C6
U 1 1 619E8632
P 6300 5200
F 0 "C6" H 6150 5100 50  0000 L CNN
F 1 "10μF" H 6050 5000 50  0000 L CNN
F 2 "Capacitor_SMD:C_1206_3216Metric" H 6338 5050 50  0001 C CNN
F 3 "https://global.kyocera.com/prdct/electro/product/pdf/cm_e.pdf" H 6300 5200 50  0001 C CNN
F 4 "CM316X5R106K10AT" H 6300 5200 50  0001 C CNN "part_number"
F 5 "Kyocera International Inc. Electronic Components" H 6300 5200 50  0001 C CNN "Manufacturer"
F 6 "" H 6300 5200 50  0001 C CNN "Vendor"
F 7 "CM316X5R106K10AT" H 6300 5200 50  0001 C CNN "Part"
	1    6300 5200
	1    0    0    -1  
$EndComp
Connection ~ 6300 5050
Text GLabel 6900 5250 3    50   Input ~ 0
GPIO_17_R
Text GLabel 4300 4300 2    50   Input ~ 0
GPIO_23
Text GLabel 3450 3700 2    50   BiDi ~ 0
GPIO_27
Wire Wire Line
	3000 3700 3450 3700
Connection ~ 3000 3700
Connection ~ 3000 3800
$Comp
L Transistor_FET:BSS123 Q1
U 1 1 619D1B75
P 4000 4100
F 0 "Q1" V 3950 4200 50  0000 L CNN
F 1 "BSS806NH6327XTSA1" V 3600 3800 50  0000 L CNN
F 2 "Package_TO_SOT_SMD:SOT-23" H 4200 4025 50  0001 L CIN
F 3 "https://www.infineon.com/dgdl/BSS806N_Rev2.3_.pdf?folderId=db3a3043156fd573011622e10b5c1f67&fileId=db3a304330f686060131185f0553451c" H 4000 4100 50  0001 L CNN
F 4 "Infineon Technologies" H 4000 4100 50  0001 C CNN "Manufacturer"
F 5 "BSS806NH6327XTSA1" H 4000 4100 50  0001 C CNN "part_number"
F 6 "" H 4000 4100 50  0001 C CNN "Vendor"
F 7 "BSS806NH6327XTSA1" H 4000 4100 50  0001 C CNN "Part"
	1    4000 4100
	0    -1   -1   0   
$EndComp
Wire Wire Line
	2500 3900 2500 4000
Wire Wire Line
	2950 4000 3000 4000
Wire Wire Line
	2500 3900 3000 3900
Wire Wire Line
	2800 4000 3000 4000
$Comp
L Device:Battery_Cell BT2
U 1 1 616EDF57
P 9100 3650
F 0 "BT2" V 8845 3700 50  0000 C CNN
F 1 "Battery_Cell" V 8936 3700 50  0000 C CNN
F 2 "Battery:BatteryHolder_Keystone_3000_1x12mm" V 9100 3710 50  0001 C CNN
F 3 "https://www.keyelco.com/userAssets/file/M65p9.pdf" V 9100 3710 50  0001 C CNN
F 4 "Keystone Electronics" H 9100 3650 50  0001 C CNN "Manufacturer"
F 5 "3000" H 9100 3650 50  0001 C CNN "part_number"
F 6 "" H 9100 3650 50  0001 C CNN "Vendor"
F 7 "3000" H 9100 3650 50  0001 C CNN "Part"
	1    9100 3650
	0    -1   -1   0   
$EndComp
Wire Wire Line
	8150 2400 7950 2400
Connection ~ 7950 2400
Text GLabel 7450 5350 2    50   Output ~ 0
GPIO_22
Text GLabel 9000 5300 2    50   BiDi ~ 0
GPIO_2
Wire Wire Line
	9000 5300 8950 5300
Connection ~ 8950 5300
Wire Wire Line
	3000 2550 2850 2550
Wire Wire Line
	2850 2850 2850 3100
Wire Wire Line
	4500 1900 4300 1900
Wire Wire Line
	4900 1900 4800 1900
Wire Wire Line
	6750 1450 6750 1600
Wire Wire Line
	6550 1600 6550 1700
Connection ~ 7350 2000
Wire Wire Line
	6800 1700 6550 1700
Wire Wire Line
	7350 1700 7200 1700
Text GLabel 5400 1450 2    50   Input ~ 0
GPIO_17_R
Wire Wire Line
	3700 3500 3700 3600
Connection ~ 3700 3500
Wire Wire Line
	3700 3600 3000 3600
Wire Wire Line
	3950 3800 3950 3400
Wire Wire Line
	3000 3800 3950 3800
Connection ~ 3950 3400
Wire Wire Line
	3950 3400 4050 3400
$Comp
L Device:R R6
U 1 1 61707D76
P 8650 4850
F 0 "R6" V 8550 4850 50  0000 C CNN
F 1 "10k" V 8650 4850 50  0000 C CNN
F 2 "Resistor_SMD:R_2010_5025Metric" V 8580 4850 50  0001 C CNN
F 3 "https://www.yageo.com/upload/media/product/productsearch/datasheet/rchip/PYu-RC_Group_51_RoHS_L_11.pdf" H 8650 4850 50  0001 C CNN
F 4 "RC2010JK-0710KL" H 8650 4850 50  0001 C CNN "part_number"
F 5 "YAGEO" H 8650 4850 50  0001 C CNN "Manufacturer"
F 6 "" H 8650 4850 50  0001 C CNN "Vendor"
F 7 "RC2010JK-0710KL" H 8650 4850 50  0001 C CNN "Part"
	1    8650 4850
	0    1    1    0   
$EndComp
Wire Wire Line
	8850 4850 8800 4850
Wire Wire Line
	8450 4400 8450 4850
Wire Wire Line
	8850 4850 8850 4800
Wire Wire Line
	8500 4850 8450 4850
Connection ~ 8450 4850
Wire Wire Line
	8450 4850 8450 5300
Text GLabel 8850 4850 3    50   Input ~ 0
GPIO_3
$Comp
L Device:R R4
U 1 1 615AD828
P 2350 6400
F 0 "R4" V 2450 6450 50  0000 L CNN
F 1 "2.2k" V 2350 6300 50  0000 L CNN
F 2 "Resistor_SMD:R_2010_5025Metric" V 2280 6400 50  0001 C CNN
F 3 "https://www.seielect.com/catalog/sei-rmcf_rmcp.pdf" H 2350 6400 50  0001 C CNN
F 4 "RMCF2010JT2K20" H 2350 6400 50  0001 C CNN "part_number"
F 5 "Stackpole Electronics, Inc." H 2350 6400 50  0001 C CNN "Manufacturer"
F 6 "" H 2350 6400 50  0001 C CNN "Vendor"
F 7 "RMCF2010JT2K20" H 2350 6400 50  0001 C CNN "Part"
	1    2350 6400
	0    -1   -1   0   
$EndComp
Text GLabel 2550 6100 0    50   Output ~ 0
GPIO_3
Text GLabel 2550 6000 0    50   BiDi ~ 0
GPIO_2
Text GLabel 2550 6600 0    50   Input ~ 0
GPIO_22
Text GLabel 2550 6500 0    50   BiDi ~ 0
GPIO_27
Connection ~ 3200 6100
Wire Wire Line
	3350 6100 3200 6100
Text GLabel 3050 6600 2    50   Output ~ 0
GPIO_23
Wire Wire Line
	2550 6400 2500 6400
Text GLabel 2200 6400 0    50   Output ~ 0
GPIO_17_R
Text GLabel 3050 7000 2    50   Input ~ 0
GPIO_8_C0
Text GLabel 2550 7000 0    50   Output ~ 0
GPIO_11_clk
Text GLabel 2550 6900 0    50   Input ~ 0
GPIO_9_MISO
Wire Wire Line
	3200 6500 3050 6500
Wire Wire Line
	3200 6100 3200 6500
Wire Wire Line
	3050 6100 3200 6100
Connection ~ 3050 6100
Wire Wire Line
	3000 6100 3050 6100
Connection ~ 3050 5900
Wire Wire Line
	3050 5900 3050 6000
Wire Wire Line
	3050 6200 3000 6200
$Comp
L power:+3.3V #PWR0119
U 1 1 614AB6FD
P 2550 5900
F 0 "#PWR0119" H 2550 5750 50  0001 C CNN
F 1 "+3.3V" H 2565 6073 50  0000 C CNN
F 2 "" H 2550 5900 50  0001 C CNN
F 3 "" H 2550 5900 50  0001 C CNN
	1    2550 5900
	1    0    0    -1  
$EndComp
$Comp
L power:+5V #PWR0115
U 1 1 613DEB6E
P 3050 5900
F 0 "#PWR0115" H 3050 5750 50  0001 C CNN
F 1 "+5V" H 3065 6073 50  0000 C CNN
F 2 "" H 3050 5900 50  0001 C CNN
F 3 "" H 3050 5900 50  0001 C CNN
	1    3050 5900
	1    0    0    -1  
$EndComp
$Comp
L power:Earth #PWR0112
U 1 1 61990DB5
P 2550 6300
F 0 "#PWR0112" H 2550 6050 50  0001 C CNN
F 1 "Earth" H 2550 6150 50  0001 C CNN
F 2 "" H 2550 6300 50  0001 C CNN
F 3 "~" H 2550 6300 50  0001 C CNN
	1    2550 6300
	0    1    1    0   
$EndComp
$Comp
L Connector_Generic:Conn_02x13_Odd_Even J2
U 1 1 6157EF99
P 2750 6500
F 0 "J2" H 2800 7200 50  0000 C CNN
F 1 "Conn_02x13_Odd_Even" H 2800 5800 50  0000 C CNN
F 2 "Connector_PinSocket_2.54mm:PinSocket_2x13_P2.54mm_Vertical" H 2750 6500 50  0001 C CNN
F 3 "https://www.te.com/commerce/DocumentDelivery/DDEController?Action=srchrtrv&DocNm=215307&DocType=Customer+Drawing&DocLang=English" H 2750 6500 50  0001 C CNN
F 4 "1-215307-0" H 2750 6500 50  0001 C CNN "part_number"
F 5 "1-215307-3 " H 2750 6500 50  0001 C CNN "Part"
F 6 "TE Connectivity AMP Connectors" H 2750 6500 50  0001 C CNN "Manufacturer"
	1    2750 6500
	1    0    0    -1  
$EndComp
$Comp
L power:Earth #PWR0109
U 1 1 615F83BE
P 3350 6100
F 0 "#PWR0109" H 3350 5850 50  0001 C CNN
F 1 "Earth" H 3350 5950 50  0001 C CNN
F 2 "" H 3350 6100 50  0001 C CNN
F 3 "~" H 3350 6100 50  0001 C CNN
	1    3350 6100
	1    0    0    -1  
$EndComp
$Comp
L power:+BATT #PWR0111
U 1 1 61C8F31F
P 3300 2650
F 0 "#PWR0111" H 3300 2500 50  0001 C CNN
F 1 "+BATT" H 3315 2823 50  0000 C CNN
F 2 "" H 3300 2650 50  0001 C CNN
F 3 "" H 3300 2650 50  0001 C CNN
	1    3300 2650
	1    0    0    -1  
$EndComp
$Comp
L power:+BATT #PWR0117
U 1 1 61C8FB4E
P 4150 1350
F 0 "#PWR0117" H 4150 1200 50  0001 C CNN
F 1 "+BATT" H 4165 1523 50  0000 C CNN
F 2 "" H 4150 1350 50  0001 C CNN
F 3 "" H 4150 1350 50  0001 C CNN
	1    4150 1350
	1    0    0    -1  
$EndComp
$Comp
L power:+BATT #PWR0127
U 1 1 61C915C3
P 4900 950
F 0 "#PWR0127" H 4900 800 50  0001 C CNN
F 1 "+BATT" H 4915 1123 50  0000 C CNN
F 2 "" H 4900 950 50  0001 C CNN
F 3 "" H 4900 950 50  0001 C CNN
	1    4900 950 
	1    0    0    -1  
$EndComp
$Comp
L power:+BATT #PWR0128
U 1 1 61C9375C
P 6550 1600
F 0 "#PWR0128" H 6550 1450 50  0001 C CNN
F 1 "+BATT" H 6565 1773 50  0000 C CNN
F 2 "" H 6550 1600 50  0001 C CNN
F 3 "" H 6550 1600 50  0001 C CNN
	1    6550 1600
	1    0    0    -1  
$EndComp
Connection ~ 6550 1600
Wire Wire Line
	7050 2000 7000 2000
Wire Wire Line
	7550 1600 6750 1600
$Comp
L Transistor_FET:BSS84 Q2
U 1 1 6167A20B
P 7000 1800
F 0 "Q2" V 7000 1950 50  0000 C CNN
F 1 "AO3415A" V 6950 1550 50  0000 C CNN
F 2 "Package_TO_SOT_SMD:SOT-23" H 7200 1725 50  0001 L CIN
F 3 "https://media.digikey.com/pdf/Data%20Sheets/Alpha%20&%20Omega/AO3415A.pdf" H 7000 1800 50  0001 L CNN
F 4 "Alpha & Omega Semiconductor Inc." H 7000 1800 50  0001 C CNN "Manufacturer"
F 5 "AO3415A" H 7000 1800 50  0001 C CNN "Part"
F 6 "AO3415A" H 7000 1800 50  0001 C CNN "part_number"
	1    7000 1800
	0    1    -1   0   
$EndComp
Text GLabel 7050 2000 2    50   Input ~ 0
drv
Connection ~ 6750 1600
Wire Wire Line
	3000 3300 3450 3300
Wire Notes Line
	9950 5550 8000 5550
Wire Notes Line
	8000 5550 8000 3200
Wire Notes Line
	8000 3200 9950 3200
Wire Notes Line
	9950 3200 9950 5550
Text Notes 8050 3300 0    50   ~ 0
RTC\n
Wire Notes Line
	6350 800  9150 800 
Wire Notes Line
	9150 800  9150 2550
Wire Notes Line
	9150 2550 6350 2550
Wire Notes Line
	6350 2550 6350 800 
Wire Notes Line
	4550 5850 6900 5850
Wire Notes Line
	6900 5850 6900 7150
Wire Notes Line
	6900 7150 4550 7150
Wire Notes Line
	4550 7150 4550 5850
Wire Wire Line
	3050 6700 3450 6700
Wire Notes Line
	4050 7350 4050 5650
Wire Notes Line
	4050 5650 1700 5650
Wire Notes Line
	1700 5650 1700 7350
Wire Notes Line
	1700 7350 4050 7350
Text Notes 1750 5750 0    50   ~ 0
Raspberry Pi Pins\n
Text Notes 4600 5950 0    50   ~ 0
Battery Level ADC Reader
Text GLabel 4300 1900 0    50   Input ~ 0
push_button
$Comp
L power:+BATT #PWR0129
U 1 1 61DCB539
P 3700 3200
F 0 "#PWR0129" H 3700 3050 50  0001 C CNN
F 1 "+BATT" H 3715 3373 50  0000 C CNN
F 2 "" H 3700 3200 50  0001 C CNN
F 3 "" H 3700 3200 50  0001 C CNN
	1    3700 3200
	1    0    0    -1  
$EndComp
Text GLabel 3450 3300 2    50   Output ~ 0
push_button
Wire Wire Line
	3000 3200 3700 3200
Wire Notes Line
	5450 5700 5450 4750
Wire Notes Line
	7850 4750 7850 5700
Wire Notes Line
	5950 700  5950 2100
Wire Notes Line
	5950 2100 3750 2100
Wire Notes Line
	3750 2100 3750 700 
Wire Notes Line
	3750 700  5950 700 
Text Notes 5500 4850 0    50   ~ 0
Button State Holder
Text Notes 3800 800  0    50   ~ 0
Wake Up Timer
Wire Notes Line
	4900 4750 3000 4750
Wire Notes Line
	3000 4750 3000 2400
Wire Notes Line
	3000 2400 4900 2400
Wire Notes Line
	4900 2400 4900 4750
Text GLabel 6000 5050 0    50   Input ~ 0
push_button
Wire Wire Line
	6550 5450 6300 5450
Connection ~ 6300 5450
Wire Wire Line
	8650 3650 8900 3650
Text GLabel 5400 1350 2    50   Output ~ 0
drv
$Comp
L Transistor_FET:BSS123 Q4
U 1 1 617890CF
P 7250 5250
F 0 "Q4" V 7100 5050 50  0000 L CNN
F 1 "BSS806NH6327XTSA1" V 7600 4700 50  0000 L CNN
F 2 "Package_TO_SOT_SMD:SOT-23" H 7450 5175 50  0001 L CIN
F 3 "https://www.infineon.com/dgdl/BSS806N_Rev2.3_.pdf?folderId=db3a3043156fd573011622e10b5c1f67&fileId=db3a304330f686060131185f0553451c" H 7250 5250 50  0001 L CNN
F 4 "Infineon Technologies" H 7250 5250 50  0001 C CNN "Manufacturer"
F 5 "BSS806NH6327XTSA1" H 7250 5250 50  0001 C CNN "part_number"
F 6 "" H 7250 5250 50  0001 C CNN "Vendor"
F 7 "BSS806NH6327XTSA1" H 7250 5250 50  0001 C CNN "Part"
	1    7250 5250
	0    -1   1    0   
$EndComp
Wire Wire Line
	6300 5050 6550 5050
Connection ~ 6550 5050
$Comp
L Transistor_FET:BSS123 Q3
U 1 1 616A96A0
P 6650 5250
F 0 "Q3" H 6500 5050 50  0000 L CNN
F 1 "BSS806NH6327XTSA1" H 6550 4900 50  0000 L CNN
F 2 "Package_TO_SOT_SMD:SOT-23" H 6850 5175 50  0001 L CIN
F 3 "https://www.infineon.com/dgdl/BSS806N_Rev2.3_.pdf?folderId=db3a3043156fd573011622e10b5c1f67&fileId=db3a304330f686060131185f0553451c" H 6650 5250 50  0001 L CNN
F 4 "Infineon Technologies" H 6650 5250 50  0001 C CNN "Manufacturer"
F 5 "BSS806NH6327XTSA1" H 6650 5250 50  0001 C CNN "part_number"
F 6 "" H 6650 5250 50  0001 C CNN "Vendor"
F 7 "BSS806NH6327XTSA1" H 6650 5250 50  0001 C CNN "Part"
	1    6650 5250
	-1   0    0    -1  
$EndComp
$Comp
L power:+3.3V #PWR0126
U 1 1 617BA907
P 7050 5350
F 0 "#PWR0126" H 7050 5200 50  0001 C CNN
F 1 "+3.3V" H 7065 5523 50  0000 C CNN
F 2 "" H 7050 5350 50  0001 C CNN
F 3 "" H 7050 5350 50  0001 C CNN
	1    7050 5350
	1    0    0    -1  
$EndComp
Wire Wire Line
	6550 5050 7250 5050
$Comp
L Device:R R9
U 1 1 617E4831
P 5000 6000
F 0 "R9" V 4900 6050 50  0000 C CNN
F 1 "49.9k" V 5000 6000 50  0000 C CNN
F 2 "Resistor_SMD:R_0805_2012Metric" V 4930 6000 50  0001 C CNN
F 3 "https://www.vishay.com/docs/28758/tnpw_e3.pdf" H 5000 6000 50  0001 C CNN
F 4 "TNPW080549K9FHEA" H 5000 6000 50  0001 C CNN "part_number"
F 5 "Vishay Dale" H 5000 6000 50  0001 C CNN "Manufacturer"
F 6 "" H 5000 6000 50  0001 C CNN "Vendor"
F 7 "TNPW080549K9FHEA" H 5000 6000 50  0001 C CNN "Part"
	1    5000 6000
	0    -1   -1   0   
$EndComp
$Comp
L Device:R R10
U 1 1 617EEEAC
P 5150 6150
F 0 "R10" V 5250 6150 50  0000 C CNN
F 1 "75k" V 5150 6150 50  0000 C CNN
F 2 "Resistor_SMD:R_2010_5025Metric" V 5080 6150 50  0001 C CNN
F 3 "https://www.koaspeer.com/pdfs/RK73H.pdf" H 5150 6150 50  0001 C CNN
F 4 "RK73H2HTTE7502F" H 5150 6150 50  0001 C CNN "part_number"
F 5 "KOA Speer Electronics, Inc." H 5150 6150 50  0001 C CNN "Manufacturer"
F 6 "" H 5150 6150 50  0001 C CNN "Vendor"
F 7 "RK73H2HTTE7502F" H 5150 6150 50  0001 C CNN "Part"
	1    5150 6150
	1    0    0    -1  
$EndComp
Wire Wire Line
	5150 6000 5350 6000
Wire Wire Line
	5350 6000 5350 6200
Connection ~ 5150 6000
Wire Notes Line
	5450 5700 7850 5700
Wire Notes Line
	5450 4750 7850 4750
$EndSCHEMATC
