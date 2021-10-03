typedef struct{
    float temp;
    float hum;
}  DHT_DATA;


int dht_read_data(DHT_DATA * dht_data, int retry);

//int dht_init();