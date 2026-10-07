#include <ArduinoJson.h>
#include <ESP8266WiFi.h>
#include<SoftwareSerial.h>

const char* ssid = "wiFi"; // Wifi SSID
const char* password = "pass";// WiFi Password
SoftwareSerial s(D7,D8);

const char* host = "192.168.0.103"; // Server IP address
String msg="";
int port = 1234; // Port Number of the Socket Server
const char* AGV_ID= "AGV01"; //Unique ID for each AGV
WiFiClient client;
String line;
String transmit_string;
int i=0;
boolean flag1=0;        //to know when a new set of data has been received
String received_string; // complete message from arduino, which consistors of snesors data
char rdata; // received charactors

void setup() {
 Serial.begin(115200);
 s.begin(9600);
 s.println("started");
 Serial.printf("Connecting to %s ", ssid);
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED)
  {
    delay(500);
    Serial.print(".");
  }
  Serial.println(" connected");
  
  while(1)
  {
  if (client.connect(host,port))
  {
    Serial.println("connected]");
    while (client.connected())
    {
    request("B"); // Updates the current location to the Server
    break;
    }
    break;
  }
  else
  {
    Serial.println("connection failed!]");
    client.stop();
  }
  
  }
}

void loop() {
  if(!client.connected())
  {
      if (client.connect(host,port))
      {
        Serial.println("connected]");
      }
      else
      {
        Serial.println("connection failed!]");
        client.stop();
      }
  }
 while (client.connected() || client.available())
    {
      if(client.available())
    {
      String json="";
      json = client.readString();
      
      Serial.println(json);
      s.println(json);
    }
     uart_receive();
   
      if (flag1==1){
           Serial.println(received_string);
           client.print(received_string);
           flag1=0;
           received_string="";
         }
    
    }
    Serial.println("\n[Disconnected]");
    
  
  }

 // Creates a JSON String and send the information containing Current Location & Idle Status to the server 
void request(String current_location)
{
  StaticJsonDocument<500> doc;
   JsonObject root = doc.to<JsonObject>();
  root["AGV_ID"]=AGV_ID;
  root["STATUS"]="idle";
  root["CURRENT_LOCATION"]=current_location;
  root["START"]=0;
  root["DESTINATION"]=0;
  root["FINAL"]="OK";
  String jsondata;
  serializeJsonPretty(doc, jsondata);
  Serial.println(jsondata);
  client.print(jsondata);
}

// Recieves the data from the MEGA through UART
void uart_receive(){
  
  while (s.available() > 0 )
  {
    rdata = s.read();
    if(rdata != '\n')
    {
       received_string = received_string + rdata;
    continue;
    }
    if(rdata == '\n')
    {
       flag1=1;
       break;
       s.flush();
    }
    if(s.overflow())
    {
      Serial.println("Overflow");
    }
   }

}
