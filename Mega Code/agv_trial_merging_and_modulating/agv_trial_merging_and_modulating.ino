                    #define no_of_sensors 12
                    #define colour_of_track 1
  /*-----------*/   #define interrupt_pin 42                           //Interrupt pin for reading the coded strip----(L7)
  /*-----------*/   #define false_trigger_avoiding_delay 15            //to avoid false triggering while sensing the coded strip--(millisec)
  /*-----------*/   #define right_side_code_sensor 9                   //code sensor pin----(H6)
  
                    #include <ArduinoJson.h>
 
            //Variables for pid calculation
                    boolean Sensor[no_of_sensors]={0};
                    float KP=0,KI=0.3,KD=0, error , p_error , i_error , d_error , f_error , pre_error=0, pre_i_error=0, i_error_array[10]={0}; 
                    int Error[no_of_sensors]={-340,-290,-240,-190,-155,-130,130,155,190,240,290,340};

            //Variables for distance measurement
                    void measure_distance();
                    const int trigPin = 9, echoPin = 10;
                    long duration;
                    int distance;

            //Variables for direction at an intersection
                    boolean right=0, straight=0, left=0, started1=0 , started2=0; 
                    int no_of_possible_paths=0;
                                        
            //Variables for sensing the coded strip and decoding
                    int  code[1], millisec=0, code_index=0;

            //control signals to the motor controller
                    int left_motor, right_motor;


            //Variables for the UART communication
                    String received_string; // complete message from arduino, which consistors of snesors data
                    char rdata; // received charactors
                    boolean flag1=0;
                    char path[10], node[10]="0123456789";
                    int count=0;
                    const char* AGV_ID= "AGV01";


            //Extras
                    //int array_pointer=0;
                    //unsigned long time_period_1, time_period_2,time_period;                 //for callibration before sensing the coded strips


                    
void setup() {
                    DDRL = 0x00;                    //pins PL0 tO PL7 as input for sensors
                    DDRH = 0x00;                    //pins PH0 to PH7 as input for sensors
                   // DDRL = (DDRL & 0x18) | 0x18;    //pins 49,48,47,43 (PL 0,1,2,6,7) as input for sensors and pins 46(PL3) and 45(PL4) as output for motor pwm 
                    
                    attachInterrupt(digitalPinToInterrupt(interrupt_pin), read_the_strip, CHANGE);
                    pinMode(trigPin, OUTPUT);       // Sets the trigPin as an Output
                    pinMode(echoPin, INPUT);        // Sets the echoPin as an Input
                    

              //For Communication
                  //  Serial.begin(115200);
                  //  Serial1.begin(9600);
}                   



void loop() {
  
// reads the sensor values and storing them in the Sensor array
                        for(int i=0;i<6;i++)
                         Sensor[5-i]=(PINL &  _BV(i))>>i;          

                        for(int i=0;i<6;i++)
                          Sensor[6+i]=(PINH & _BV(i))>>i;


//Code for debugging                             

//                              for(int i=0;i<12;i++){
//                                Serial.print(Sensor[i]);
//                                Serial.print("\t");
//                              }
//                              Serila.println("");


// Calculation for number of possible paths
                        
                        no_of_possible_paths=0;               //resets the number of possible paths at the begining of every iterration
                                       
                        for(int i=0 ;i<no_of_sensors;i++)      //calculates the number of possible paths by sensing the white spaces between the tracks
                        {  
                           if (Sensor[i]==colour_of_track)                  //colour of line
                             {
                                while(Sensor[i]==colour_of_track && i<no_of_sensors)        //colour of line
                                  i++;
                                
                                no_of_possible_paths++;
                             }
                             
                        } 



//To go left at an intersection
                        if(left==1)                                                        //Erases all the tracks from the memory except the left most track
                          {
                                     for(int i=0;i<no_of_sensors;i++)                       // starts from the left most sensor
                                        {  
                                           if (Sensor[i]==colour_of_track)                                //loops without going into the while loop until a track has been found
                                             {
                                                 while(Sensor[i]==colour_of_track && i<no_of_sensors)     //skips the left most track
                                                    i++;
                                                while(i<no_of_sensors)                      //Erases all the remaining tracks
                                                    {
                                                      Sensor[i]=1-colour_of_track;
                                                      i++;
                                                    }
                                             }
                                        
                                        }
                          }

//Code for debugging
                          

//                              Serial.print("/");
//                              Serial.print("/");
//                              Serial.print("/");
//                              for(int i=0;i<12;i++){
//                                Serial.print(Sensor[i]);
//                                Serial.print("\t");
//                              }
//                              Serial.println("");



//To go right at an intersection
                        if(right==1)                                               //Erases all the tracks from the memory except the left most track
                          {
                                     for(int i=(no_of_sensors-1);i>=0;i--)         //starts from the right most sensor
                                        {                                          //loops without going into the while loop until a track has been found
                                           if (Sensor[i]==colour_of_track)
                                             {
                                                 while(Sensor[i]==colour_of_track && i>=0)       //skips the right most track 
                                                    i--;
                                                 while(i>=0)
                                                    {
                                                      Sensor[i]=1-colour_of_track;                 //Erases all the remaining tracks
                                                      i--;
                                                    }
                                             }
                                        
                                        }
                          }

//Code for debugging


//                              Serial.print("/");
//                              Serial.print("/");
//                              Serial.print("/");
//                              for(int i=0;i<12;i++){
//                                Serial.print(Sensor[i]);
//                                Serial.print("\t");
//                              }
//                              Serial.println("");





                        if(straight==1 && no_of_possible_paths==3)                          //going straight option is availiable only when there are three possible paths for the agv
                        {
//Erasing left line from the memory
                                  for(int i=0;i<no_of_sensors;i++)                          //starts from the left most sensor
                                        {  
                                           if (Sensor[i]==colour_of_track)
                                             {
                                                 while(Sensor[i]==colour_of_track && i<no_of_sensors)     //Erases the left most track 
                                                    {
                                                      Sensor[i]=1-colour_of_track;
                                                      i++;
                                                    }
                                                 break;                                     //once the left most track has been erased then it comes out the loop
                                             }
                                        }

//Erasing right line from the memeory 
                                  for(int i=(no_of_sensors-1);i>=0;i--)            //starts from the right most sensor
                                        {  
                                           if (Sensor[i]==colour_of_track)              
                                             {
                                                 while(Sensor[i]==colour_of_track && i>=0)
                                                    {
                                                      Sensor[i]=1-colour_of_track;                 //Erases the right most track 
                                                      i--;
                                                    }
                                                 break;                            //once the right most track has been erased then it comes out the loop
                                             }
                                        }           
                        }



//Code for debugging


//                              Serial.print("/");
//                              Serial.print("/");
//                              Serial.print("/");
//                              for(int i=0;i<12;i++){
//                                Serial.print(Sensor[i]);
//                                Serial.print("\t");
//                              }
//                              Serial.println("");




//Calculation of simple error                        
                               
                          for(int i=0;i<no_of_sensors;i++)
                          {
                                if (Sensor[i]==colour_of_track)
                                      {     int j=0;
                                            error=Error[i];                             //calculates the error according to the place value of the sensors
                                            for(j=i+1;j<no_of_sensors;j++)
                                                  { 
                                               
                                                          if (Sensor[i]==Sensor[j])
                                                               error=error+Error[j];    //Adds the errors untill the track has been completed. Takes into account only the first track
                                                          else
                                                               break;                   
                                                  }
                                             error=error/(j-i);                         //Averages the error with respect to the number of sensors that have detected the track. useful for variable track width
                                             break;
                                      }
                          }

                              



//Calculation of pid error
                    
                    p_error = error*KP;                   // P Error
                    
                    i_error = pre_i_error+(error*KI);     //I Error
                    if (error==0)                                 //if current error =0 then i value =0
                           i_error=0;

                    d_error = (error-pre_error)*KD;       //D Error
                    if (error==0)
                            d_error=0;                            //if current error =0 then d value =0

                    
//Only the last 10 values of i_error are use for the calculation in the next iteration. So as to have a smooth tracking along a curve
                    for(int i=8;i>=0;i--)
                            i_error_array[i+1]=i_error_array[i];      //Shifts the previous I Error values so as to make room for the fresh I Error
                            i_error_array[0] = i_error;                       //includes the fresh I Error the i_error array

                    pre_i_error=0;
                    for(int i=0;i<9;i++)
                        pre_i_error=pre_i_error+i_error_array[i];     //Calculates the pre_i_error by summing up the i_error array



                    if(pre_i_error>=3068839424)                       //Checking for overflow. Useful during PID tuning
                        Serial.println("Overflow of pre_i_error");
                        
                    pre_error=error;                                  //For calculation of d_error

                        f_error= p_error + i_error + d_error;         //Calculates the pid error
                        f_error=f_error/10;                           //Reduces the scale of the pid error by a factor of 10


//Code for debugging
                              

//                              Serial.print("/");
//                              Serial.print("/");
//                              Serial.print("/");
//                              for(int i=0;i<10;i++)                             
//                              Serial.print(i_error_array[i]);
//                              Serial.println("");





//Control signals to the motor controller
                     left_motor  = 255;
                     right_motor = 255;                  
                     
                     if(f_error > 0)
                          left_motor  = 255 - f_error;
                   
                     else if(f_error < 0)
                          right_motor = 255 - f_error;
                     
                     analogWrite(44, left_motor);
                     analogWrite(45, right_motor);

}     

void code_print(){
  
  if(code[0]!=NULL && code_index==4)          //to make sure that code is not emplty but fully filled
      {
        for(int i=0;i<5;i++)                    //Prints the code
           Serial.print(code[i]);
         Serial.println("");

         code[0]=NULL;                        //Resets the code array
         code_index=0;                        //Resets the code index
      }
      
}

void read_the_strip(){                                  //function to read the coded strip
          if(started1==0)                               
          {
            millisec = millis();                        //starts the millis timer when a black strip is detected
            started1 = 1;   
            Serial.println("started1");                            
          }

          else if (started1==1 && started2==0)          //Goes into this condition only if it was started2==0 which is used to find when the sensor has moved from black strip to the white strip
          {
            millisec = millisec - millis();             //finds the time taken to move over the black strip 
            started2 = 1;
            code_index=0;
            Serial.println("started1 and started 2");                                        
          }   

          else if (started1==1 && started2==1 && millisec >= false_trigger_avoiding_delay)  //Goes into this condition only if it has measures the width of the 
          {                                                                               //black strip and it is greater than a apecific value which is used to avoid false triggering
            code[code_index]=digitalRead(right_side_code_sensor);                                  //Reads the Right Sensor Code and Strores it in the memory
            code_index++;
            started1=0;              //Resets the variables
            started2=0;
            Serial.println("read");
          }

//false triggering
          else    
          {
            started1=0;             //Executed when it is a false trigger
            started2=0;
            Serial.println("false trigger");
          }
}




void measure_distance(){
    // Clears the trigPin
          digitalWrite(trigPin, LOW);
          delayMicroseconds(2);
          
    // Sets the trigPin on HIGH state for 10 micro seconds
          digitalWrite(trigPin, HIGH);
          delayMicroseconds(10);
          digitalWrite(trigPin, LOW);
          
    // Reads the echoPin, returns the sound wave travel time in microseconds
          duration = pulseIn(echoPin, HIGH);
          
    // Calculating the distance
          distance= duration*0.034/2;
}


void receive_data() {                                       //Call this fumction to receive data
    request("A");             
    uart_receive();
   if (flag1==1){
           Serial.println(received_string);
           parse_json(received_string);
           flag1=0;
           received_string="";
           Serial.println(node);
           Serial.println(path);
         }
}



void uart_receive(){
  while (Serial1.available() > 0 )                      
  {
    rdata = Serial1.read();                     //stores one character
    if(rdata != '\n')
    {
      //Serial.print(rdata);
       received_string = received_string + rdata;       //concatates if the string hasn't ended
       continue;                                        //continues to the next iteration
    }
    if(rdata == '\n')                       //when the string has ended
    {
       flag1=1;
       break;
       Serial1.flush();                     //flushes the serial buffer
    }
   }

}


void parse_json(String json)
{     
  StaticJsonDocument<500> doc;                                            //Creates a jsonn buffer
      DeserializationError error = deserializeJson(doc, json);            //Checks for deserialiaztion errors
      if (error) {
            Serial.print(F("deserializeJson() failed: "));
            Serial.println(error.c_str());                                //Prints the errors if any
            
          }
      String arrayy=doc["PATH"];
      Serial.println(arrayy);
      JsonArray direction_array = doc["PATH"].as<JsonArray>();
      int ind=0;
      for(JsonVariant v : direction_array) {
        char buf[2];
          v.as<String>().toCharArray(buf, 2);
          path[ind++]= buf[0];
          Serial.println(buf[0]);
      }
      path[ind++]=NULL;
      JsonArray node_array = doc["NODE"].as<JsonArray>();
      ind=0;
      for(JsonVariant v : node_array) {
        char buf[2];
        
          v.as<String>().toCharArray(buf, 2);
          node[ind++]= buf[0];
          Serial.println(buf[0]);

      }
      node[ind++]=NULL;
      count = doc["COUNT"];
       Serial.println(count);
}


void request(String A,String B)
{
  StaticJsonDocument<500> doc;                    //Creates a jsonn buffer
  JsonObject root = doc.to<JsonObject>();         //Creates a json object names root
  root["AGV_ID"]=AGV_ID;                          //Adds key-value pairs to the json object names 'root'
  root["STATUS"]="busy";
  root["START"]=A;
  root["DESTINATION"]=B;
  root["FINAL"]="OK";
  String jsondata = "";
  serializeJson(doc,jsondata);                        
  Serial.println(jsondata); 
  Serial1.println(jsondata);                      //Sends the Json string via UART
}


void request(String current_location)
{
  StaticJsonDocument<500> doc;                    //Creates a jsonn buffer
   JsonObject root = doc.to<JsonObject>();        //Creates a json object names root
  root["AGV_ID"]=AGV_ID;                          //Adds key-value pairs to the json object names 'root'
  root["STATUS"]="idle";
  root["CURRENT_LOCATION"]=current_location;
  root["START"]=0;
  root["DESTINATION"]=0;
  root["FINAL"]="OK";
  String jsondata = "";
  serializeJson(doc, jsondata);
  Serial.println(jsondata);
  Serial1.println(jsondata);                       //Sends the Json string via UART
}
