#include "MFUthings.h" 

WiFiClient wifiClient;					// WiFi instance
PubSubClient mqttClient(wifiClient); 	// MQTT instance

/**
* MFUthings 	=> the class's constructor
* @param id 	=> equipment id
* @param key 	=> project key
* @param type 	=> equipment type
* @return 	constructor
*/
MFUthings::MFUthings(uint16_t id,std::string key, std::string type){
	Serial.begin(115200); 	// initialize serial monitor
	ID = id; 				// equipment id
	KEY = key; 				// project key
	TYPE = type;			// equipment type
}

/**
* MFUthings 	=> the class's destructor
* @return 	destructor
*/
MFUthings::~MFUthings(){/*nothing to destruct*/}

/**
*
* authorized	=>	check the ownership 
* @param id 	=>	equipment id
* @param key 	=>	equipment key
* @return 	bool
*/
bool MFUthings::authorized(uint16_t id, std::string key){
	if(id == ID && key == KEY)	// check if id and key are correct
		return true;			// if coorect, return true		
	return false;				// if not, return false
}

/**
*
* begin 	=> the function for initializing stuff
* @return 	void
*/
void MFUthings::begin(){
	/* display connecting message */
	if(WiFi.status() != WL_CONNECTED)
		Serial.printf("# Error: please, provides internet connection!\n");

	setMQTT(MQTT_SERVER,MQTT_PORT);
	connectMQTT();

	/* display successful message */
	Serial.printf("\n\n=============================\n");
	Serial.printf("====== READY TO USE =========\n");
	Serial.printf("=============================\n");
	sentConnectMessage();
}


/**
*
* callback 	=>	callback function for mqtt message arrived
* @param topic 		=>	mqtt topic
* @param payload 	=>	mqtt message
* @param length 	=>	mqtt message length
* @return 	void
*/
void MFUthings::callback(char* topic, byte* payload, unsigned int length){
	char message[length];					// initialize message[] to store the message
	std::string messageStr;
	std::vector<std::string> messageArr;
	for (int i = 0; i < length; i++) 
		message[i] = (char)payload[i];		// store the message into message[] 
	messageStr = message;					// convert into string
	messageArr = split(messageStr,"/");
	if(authorized(atoi(messageArr[0].c_str()),messageArr[1])){
		update(atoi(messageArr[2].c_str()));
		response();
	}
	
}

/**
*
* connectMQTT 	=>	the function for connecting to mqtt broker
* @return	void
*/
void MFUthings::connectMQTT(){
	Serial.printf("# Connecting to mqtt broker...");
	while (!mqttClient.connected()) {
		if (mqttClient.connect(genMQTTID(10).c_str(), MQTT_USERNAME, MQTT_PASSWORD)) {
			Serial.printf("connected\n");
			if(TYPE == "OUTPUT"){
				mqttClient.subscribe(MQTT_TOPIC);
			}
		} else {
			Serial.print("failed, rc=");
			Serial.print(mqttClient.state());
			Serial.println(" try again in 5 seconds");
			delay(5000);
		}
	}
}

/**
*
* connectWiFi 	=>	the function for connecting to WiFi
* @param ssid 	=>	WiFi ssid
* @param password 	=> 	WiFi password
* @return 	void
*/
void MFUthings::connectWiFi(std::string ssid, std::string password){
	if (ssid != "")
	{
		WIFI_SSID = ssid;
		WIFI_PASSWD = password;
		if (WiFi.status() != WL_CONNECTED)
		{
			Serial.printf("# Connecting to %s",ssid.c_str());
			WiFi.begin(ssid.c_str(), password.c_str());
			while (WiFi.status() != WL_CONNECTED) {
				Serial.print('.');
				delay(500);
			}

		}
		Serial.println();
		Serial.print("# Connected, IP address: ");
		Serial.println(WiFi.localIP());
	}
	else{
		Serial.printf("# Error: no ssid is specific!\n");
	}
}

/**
*
* connectWiFi 	=>	the function for connecting to WiFi and let an LED blinking to show the WiFi status
* @param ssid 		=>	WiFi ssid
* @param password 	=> 	WiFi password
* @param pin 		=>	LED pin
* @return 	void
*/
void MFUthings::connectWiFi(std::string ssid, std::string password, uint16_t pin){
	pinMode(pin,OUTPUT);
	if (ssid != "")
	{
		WIFI_SSID = ssid;
		WIFI_PASSWD = password;
		if (WiFi.status() != WL_CONNECTED)
		{
			Serial.printf("# Connecting to %s",ssid.c_str());
			WiFi.begin(ssid.c_str(), password.c_str());
			while (WiFi.status() != WL_CONNECTED) {
				digitalWrite(pin,HIGH);
				delay(500);
				digitalWrite(pin,LOW);
				delay(500);
				yield();
			}
		}
		digitalWrite(pin,HIGH);
		Serial.println();
		Serial.print("# Connected, IP address: ");
		Serial.println(WiFi.localIP());
	}
	else{
		Serial.printf("# Error: no ssid is specific!\n");
	}
}

void MFUthings::connectionResponse(){
	char* id = new char[10];
	id = itoa(ID,id,10);
	std::string value = "-999";
	std::string response = std::string(id)+"/"+std::string(KEY)+"/"+value;
	mqttClient.publish(MQTT_DESTINATION,response.c_str());
}

/**
*
* genMQTTID 	=> generate random string and assign to MQTT ID
* @param length	=> the length of string to generate
* @return string
*/
std::string MFUthings::genMQTTID( size_t length )
{
	auto randchar = []() -> char
	{
		const char charset[] =
		"0123456789"
		"ABCDEFGHIJKLMNOPQRSTUVWXYZ"
		"abcdefghijklmnopqrstuvwxyz";
		const size_t max_index = (sizeof(charset) - 1);
		return charset[ rand() % max_index ];
	};
	std::string str(length,0);
	std::generate_n( str.begin(), length, randchar );
	return str;
}

/**
*
* handle 	=> the function the keep program alive and keep update things
* @return 	void
*/
void MFUthings::handle(){
	if(FIRST_CONNECTED == 1){
		delay(3000);
		response();
		FIRST_CONNECTED = 0;
	}
	if (WiFi.status() != WL_CONNECTED)
	{
		Serial.print("Reconnecting");
		WiFi.begin(WIFI_SSID.c_str(), WIFI_PASSWD.c_str());
		while (WiFi.status() != WL_CONNECTED) {
			Serial.print('.');
			delay(500);
		}
		Serial.println();
		Serial.print("Connected, IP address: ");
		Serial.println(WiFi.localIP());
	}
	CURRENT_MILLIS = millis();
	if (CURRENT_MILLIS - CONNECTION_PREVIOUS_MILLIS >= CONNECTION_INTERVAL) {
		CONNECTION_PREVIOUS_MILLIS = CURRENT_MILLIS;
		if (!mqttClient.connected()) {
			connectMQTT();
		}
		connectionResponse();
	}
	if (CURRENT_MILLIS - PREVIOUS_MILLIS >= INTERVAL) {
		PREVIOUS_MILLIS = CURRENT_MILLIS;
		if (!mqttClient.connected()) {
			connectMQTT();
		}
		response();
		Serial.print("#");
	}
	mqttClient.loop();
	delay(1);
}

/**
*
* handle 		=>	the function the keep program alive and keep update things
* @param val 	=>	the value that be sent from MQTT 
* @return 	void
*/
void MFUthings::handle(signed int val){
	if(FIRST_CONNECTED == 1){
		VALUE = val;
		delay(3000);
		response();
		FIRST_CONNECTED = 0;
	}
	if (WiFi.status() != WL_CONNECTED)
	{
		Serial.print("Reconnecting");
		WiFi.begin(WIFI_SSID.c_str(), WIFI_PASSWD.c_str());
		while (WiFi.status() != WL_CONNECTED) {
			Serial.print('.');
			delay(500);
		}
		Serial.println();
		Serial.print("Connected, IP address: ");
		Serial.println(WiFi.localIP());
	}
	CURRENT_MILLIS = millis();
	if (CURRENT_MILLIS - CONNECTION_PREVIOUS_MILLIS >= CONNECTION_INTERVAL) {
		CONNECTION_PREVIOUS_MILLIS = CURRENT_MILLIS;
		if (!mqttClient.connected()) {
			connectMQTT();
		}
		connectionResponse();
	}
	if (CURRENT_MILLIS - PREVIOUS_MILLIS >= INTERVAL) {
		VALUE = val;
		PREVIOUS_MILLIS = CURRENT_MILLIS;
		if (!mqttClient.connected()) {
			connectMQTT();
		}
		response();
		Serial.print("#");
	}
	mqttClient.loop();
	delay(1);
}

/**
*
* output 	=>	set output pin
* @param output 	=>	output pin
* @return	void
*/
void MFUthings::output(int output){
	OUT_PIN = output;			// assign output to OUT_PIN
	pinMode(OUT_PIN,OUTPUT);	// declare OUT_PIN to output mode
	Serial.printf("# You've setup D%d as output pin\n",OUT_PIN-2);
}

/**
*
* response 	=> 	response the status to MQTT client
* @return	void
*/
void MFUthings::response(){
	char* id = new char[10];
	char* value = new char[5];
	id = itoa(ID,id,10);
	value = itoa(VALUE,value,10);
	std::string response = std::string(id)+"/"+std::string(KEY)+"/"+std::string(value);
	mqttClient.publish(MQTT_DESTINATION,response.c_str());
}

/**
*
* sendConnectMessage 	=> the function for sending a first-time connecting message
* @return 	void
*/
void MFUthings::sentConnectMessage(){
	char* id = new char[10];
	char* value = new char[5];
	id = itoa(ID,id,10);
	value = itoa(CONNECTING_VALUE,value,10);
	std::string message = std::string(id)+"/"+std::string(KEY)+"/"+std::string(value);
	mqttClient.publish(MQTT_DESTINATION,message.c_str());
}

/**
*
* setMQTT 	=>	initialize MQTT server and callback
* @param server 	=>	MQTT server
* @param port 		=> 	MQTT port
* @return 	void
*/
void MFUthings::setMQTT(const char* server, const uint16_t port){
	mqttClient.setServer(server,port);
	mqttClient.setCallback(std::bind(&MFUthings::callback, this, std::placeholders::_1, std::placeholders::_2, std::placeholders::_3));
}

/**
*
* split 		=> 	the function for spliting a string into an array
* @param str 	=>	the input string 
* @param delim	=>	the delimeter
* @return 	array
*/
std::vector<std::string> MFUthings::split(const std::string& str, const std::string& delim){
	std::vector<std::string> tokens;
	size_t prev = 0, pos = 0;
	do
	{
		pos = str.find(delim, prev);
		if (pos == std::string::npos) pos = str.length();
		std::string token = str.substr(prev, pos-prev);
		if (!token.empty()) tokens.push_back(token);
		prev = pos + delim.length();
	}
	while (pos < str.length() && prev < str.length());
	return tokens;
}

/**
*
* update 		=> the function for update value
* @param val 	=> the value to update
* @return 	void
*/
void MFUthings::update(signed int val){
	VALUE = val;
	if (VALUE == 1)
		digitalWrite(OUT_PIN,HIGH);
	else if(VALUE == -1)
		digitalWrite(OUT_PIN,LOW);
	else
		Serial.printf("Invalid value!\n");
	Serial.printf("=================== Update =================\n");
	Serial.printf("STATUS : %d\n",VALUE);
	Serial.printf("============================================\n\n\n");
}

