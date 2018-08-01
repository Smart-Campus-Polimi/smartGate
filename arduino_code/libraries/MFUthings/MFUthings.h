
#ifndef MFUthings_H
#define MFUthings_H

#include <Arduino.h>
#include <ESP8266WiFi.h>
#include <PubSubClient.h>
#include <string>
#include <vector>
#include <stdlib.h>
#include <random>
#include <functional> //for std::function
#include <algorithm>  //for std::generate_n

class MFUthings {

public:
	MFUthings(uint16_t id,std::string key, std::string type);
	~MFUthings();
	void begin();
	void connectWiFi(std::string ssid, std::string password);
	void connectWiFi(std::string ssid, std::string password, uint16_t pin);
	void handle();
	void handle(signed int val);
	void output(int output);

private:
	const char* 		MQTT_SERVER = "mqtt.dioty.co";
	const char* 		MQTT_USERNAME = "5731501049@lamduan.mfu.ac.th";
	const char* 		MQTT_PASSWORD = "0452c4fd";
	const char* 		MQTT_TOPIC = "/5731501049@lamduan.mfu.ac.th/MFUTHINGS-EQ";
	const char* 		MQTT_DESTINATION = "/5731501049@lamduan.mfu.ac.th/MFUTHINGS-APP";
	const uint16_t 		MQTT_PORT = 1883;
	const uint16_t 		INTERVAL = 60000;
	const uint16_t		CONNECTION_INTERVAL = 10000;
	const signed int 	ON_VALUE = 1;
	const signed int 	OFF_VALUE = -1;
	const signed int 	CONNECTING_VALUE = -777;
	int					OUT_PIN;
	int 				FIRST_CONNECTED = 1;
	uint16_t 			ID;
	unsigned long 		PREVIOUS_MILLIS = 0;
	unsigned long 		CONNECTION_PREVIOUS_MILLIS = 0;
	unsigned long 		CURRENT_MILLIS;
	signed int 			VALUE = -1;
	std::string			KEY;
	std::string			TYPE;
	std::string			WIFI_SSID;
	std::string			WIFI_PASSWD;
	bool authorized(uint16_t id, std::string key);
	void callback(char* topic, byte* payload, unsigned int length);
	void connectMQTT();
	void connectionResponse();
	void response();
	void sentConnectMessage();
	void setMQTT(const char* server, const uint16_t port);
	void update(signed int val);
	std::string genMQTTID( size_t length );
	std::vector<std::string> split(const std::string& str, const std::string& delim);
};
#endif
