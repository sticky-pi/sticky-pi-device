#ifndef DHT22_H_
#define DHT22_H_

typedef struct{
    float temp;
    float hum;
}  DHT_DATA;


int dht_read_data(DHT_DATA * dht_data, int retry);


extern int GPIO_TO_WIRING_PI_MAP[28];

/*

int GPIO_TO_WIRING_PI_MAP[]= {
30,
31,
8,
9,
7,
21,
22,
11,
10,
13,
12,
14,
26,
23,
15,
16,
27,
0,
1,
24,
28,
29,
3,
4,
5,
6,
25,
2
};
*/

//int dht_init();
#endif