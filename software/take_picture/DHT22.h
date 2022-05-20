#ifndef DHT22_H_
#define DHT22_H_

typedef struct{
    float temp;
    float hum;
}  DHT_DATA;


int dht_read_data(DHT_DATA * dht_data, int dht_pin, int retry);


extern int GPIO_TO_WIRING_PI_MAP[28];

#endif