#include <ESP8266WiFi.h>
#include <PubSubClient.h>
#include <ArduinoJson.h>
#include <WiFiUdp.h>
#include <IRremoteESP8266.h>

extern "C" {
#include "user_interface.h"
}

const char* ssid = "IoTPolimi";
const char* password = "ZpvYs=gT-p3DK3wb";
const char* mqtt_server = "10.172.0.11";

unsigned int localPort = 2390; 

int RECV_PIN = 4; //ricevitore infrarossi D2

long int tempo = 0;
long int counter = 0;
const int pir0b = 14;      //Pir0B = D5 = 14 
const int pir1b = 16;      //Pir1B = D0 = 16
const int pAn = A0;       // pir analogico.

const int led = 15;   // led Blue D8
const int ledRed = 2; // led Red  D4

const int durata = 86400000;
const int ultimi_secondi = 300000;
char JSONmessagebuffer[5000];

StaticJsonBuffer<5000> JSONbuffer;
JsonObject& root = JSONbuffer.createObject();
JsonArray& ir = root.createNestedArray("IR");
JsonArray& an = root.createNestedArray("AN");
JsonArray& p1b = root.createNestedArray("P1B");
JsonArray& p0b = root.createNestedArray("P0B");

// Tempo di calibrazione del sensore
int calibrationTime = 45;
int c = 0;

int secondi = 1;
int sequenceNumber = 0;

WiFiClient espClient;
PubSubClient client(espClient);
IRrecv irrecv(RECV_PIN);
decode_results results;

void setup() {
  
  Serial.begin(115200);
  setup_wifi();
  client.setServer(mqtt_server, 1883);
  client.setCallback(callback);
  
  //setup Pir 1B
  pinMode(pir1b, INPUT);
  digitalWrite(pir1b, LOW);

  //setup Pir 0B
  pinMode(pir0b, INPUT);
  digitalWrite(pir0b, LOW);

  pinMode(led,OUTPUT);
  pinMode(ledRed,OUTPUT);

  //Fase di calibrazione
  digitalWrite(ledRed,HIGH);
  Serial.print("Calibrazione del sensore ");
  for (int i = 0; i < calibrationTime; i++) {
    Serial.print(".");
    delay(1000);
  }
  Serial.println(" Fatto");
  Serial.println("SENSORE ATTIVO");
  delay(50); 
  digitalWrite(ledRed,LOW);
  digitalWrite(led,HIGH);

  
  if(!client.connected())
  {
    reconnect();
  }
  client.loop();
  
  counter=millis();
  irrecv.enableIRIn();
}


void setup_wifi() {
  delay(10);
  // We start by connecting to a WiFi network
  Serial.println();
  Serial.print("Connecting to ");
  Serial.println(ssid);
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) 
  {
    delay(250);
    Serial.print(".");
  }
  Serial.println("");
  Serial.println("WiFi connected");
  Serial.println("IP address: ");
  Serial.println(WiFi.localIP());
}

void callback(char* topic, byte* payload, unsigned int length) {
  Serial.print("Message arrived [");
  Serial.print(topic);
  Serial.print("] ");
  for (int i = 0; i < length; i++) {
    Serial.print((char)payload[i]);
  }
  Serial.println();
}

void reconnect() {
  // Loop until we're reconnected
  while (!client.connected()) {
    Serial.print("Attempting MQTT connection...");
    // Attempt to connect
    if (client.connect("")) {
      Serial.println("connected");
      // Once connected, publish an announcement...
      //client.publish("outTopic", "hello world");
      // ... and resubscribe
      //client.subscribe("inTopic");
    } else {
      Serial.print("failed, rc=");
      Serial.print(client.state());
      Serial.println(" try again in 5 seconds");
      // Wait 5 seconds before retrying
      delay(5000);
    }
  }
}

void loop() 
{
  //Permette di dare un limite al tempo di funzionamento nella rilevazione dei dati
  /*    
  if((millis()-counter)>(durata-ultimi_secondi) && (millis()-counter)<durata)
  {
    digitalWrite(ledRed,HIGH);
  }
  else
  {
    digitalWrite(ledRed,LOW);
  }
  
  if((millis()-counter)<durata)
  { 
*/
          
  // lettura dei dati e salvataggio di un secondo di dati
  
  if (irrecv.decode(&results)) 
  {
      ir.add(1);
      irrecv.resume(); // Receive the next value
  }
  else
  {
      ir.add(0);
  }
  
  sleep_bello(10);
  
  an.add(analogRead(pAn));
  
  if(digitalRead(pir1b)==HIGH)
  {
    p1b.add(1);  
  }
  else
  {
    p1b.add(0);
  }   
  
  if(digitalRead(pir0b)==HIGH)
  {
    p0b.add(1);
  }
  else
  {
    p0b.add(0);
  }

  c=c+1;
  
  while(WiFi.status() != WL_CONNECTED)
  { 
    WiFi.begin(ssid, password);
    Serial.print("Stato WiFi: ");
    Serial.print(WiFi.status());
  }
  
  // ogni secondo invio tutto quello che ho ricevuto
  if((millis()-counter)>secondi*1000)
    {
      root["SN"]=sequenceNumber;
      root["Lato"]="B";   
         
      //verifico connessione server MQTT
      if(!client.connected())
      {
        reconnect();
      }
      client.loop();         
       

      
      Serial.print("#SN ");
      Serial.print(sequenceNumber);     
      Serial.print(" Campioni= ");
      Serial.print(c);
      Serial.print(" istante= ");
      Serial.print(millis()-counter); 
           
      const int BUFFER_SIZE = JSON_OBJECT_SIZE(6) + JSON_ARRAY_SIZE(c*4);
      Serial.println(BUFFER_SIZE);
      
      c=0;
      secondi=round((millis()-counter)/1000)+1;     
      sequenceNumber = sequenceNumber+1;

      //pubblicazione dei messaggi formato json
      root.printTo(JSONmessagebuffer, sizeof(JSONmessagebuffer));
      client.publish("smartgate/sg1/mls/sb",JSONmessagebuffer);
      
      Serial.println ("Free memory is: ");
      uint32_t freeMemory = system_get_free_heap_size();
      Serial.print (freeMemory); 
      
      //root.printTo(Serial);
      
      JSONbuffer.clear();
      JsonObject& root = JSONbuffer.createObject();
      JsonArray& ir = root.createNestedArray("IR");
      JsonArray& an = root.createNestedArray("AN");
      JsonArray& p1b = root.createNestedArray("P1B");
      JsonArray& p0b = root.createNestedArray("P0B");
    }    
}

void sleep_bello(int time_to_wait)  
{
  int millis2 = millis();
  while ((millis() - millis2 ) < time_to_wait) {
    
  }
}

















