#include <wiringPi.h>
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include "DHT22.h"

// CONSTANTS
#define MAX_TIMINGS	85
#define MAX_RETRIES 6
#define WAIT_BETWEEN_RETRIES 250 //ms





int dht_read_data(DHT_DATA * dht_data, int dht_pin, int retry) {

    int data[5] = { 0, 0, 0, 0, 0 };

	uint8_t laststate = HIGH;
	uint8_t counter	= 0;
	uint8_t j = 0;
	uint8_t i;


    pinMode(dht_pin, OUTPUT);
    digitalWrite(dht_pin, HIGH);
	digitalWrite(dht_pin, LOW);

	/* pull pin down for 2 milliseconds */
	delayMicroseconds( 2000);

	/* prepare to read the pin */
	pinMode(dht_pin, INPUT);
	/* detect change and read data */
	for ( i = 0; i < MAX_TIMINGS; i++ ) {
		counter = 0;
		while ( digitalRead( dht_pin ) == laststate ) {
			counter++;
			delayMicroseconds( 1 );
			if ( counter == 255 ) {
				break;
			}
		}
		laststate = digitalRead( dht_pin );

		if ( counter == 255 )
			break;

		/* ignore first 3 transitions */
		if ( (i >= 4) && (i % 2 == 0) ) {
			/* shove each bit into the storage bytes */
            if(j/8 > 4){
                if(retry< MAX_RETRIES){
                    delay(WAIT_BETWEEN_RETRIES);
                    return dht_read_data(dht_data, dht_pin, retry+1);
                    }

                else {
                    return 1; // NOK
                }
            }
			data[j / 8] <<= 1;
			if ( counter > 16 )
				data[j / 8] |= 1;
			j++;
		}
	}

	/*
	 * check we read 40 bits (8bit x 5 ) + verify checksum in the last byte
	 * print it out if data is good
	 */
	if ( (j >= 40) && (data[4] == ( (data[0] + data[1] + data[2] + data[3]) & 0xFF) ) ) {
		float h = (float)((data[0] << 8) + data[1]) / 10;
		if ( h > 100 ) {
			h = data[0];	// for DHT11
		}
		float c = (float)(((data[2] & 0x7F) << 8) + data[3]) / 10;
		if ( c > 125 ) {
			c = data[2];	// for DHT11
		}
		if ( data[2] & 0x80 ) {
			c = -c;
		}
		dht_data->temp = c;
		dht_data->hum = h;


		return 0; // OK
	}

	else if(retry< MAX_RETRIES){
	    delay(WAIT_BETWEEN_RETRIES);
	    return dht_read_data(dht_data, dht_pin, retry+1);
	    }

	else {
		return 1; // NOK
	}
}

