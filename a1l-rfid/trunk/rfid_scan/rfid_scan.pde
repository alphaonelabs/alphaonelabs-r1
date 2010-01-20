#include <Client.h>
#include <Ethernet.h>
#include <Server.h>
#include <Dhcp.h>

// RFID reader for Arduino 
// Wiring version by BARRAGAN <http://people.interaction-ivrea.it/h.barragan> 
// Modified for Arudino by djmatic
// Modified to send to a URL by rmd6502


int  val = 0; 
char code[10]; 
int bytesread = 0; 
byte mac[] = { 0xDE, 0xAD, 0xBE, 0xEF, 0xFE, 0xED };
byte ip[]  = { 192,168,1,50 };
//byte server[] = { 192,168,1,118 };
byte server[] = { 74,125,91,141 };
Client client(server, 80);


void setup() { 
  Ethernet.begin(mac, ip);
  Serial.begin(2400); // RFID reader SOUT pin connected to Serial RX pin at 2400bps 
  pinMode(2,OUTPUT);   // Set digital pin 2 as OUTPUT to connect it to the RFID /ENABLE pin 
  digitalWrite(2, LOW);                  // Activate the RFID reader
}  


 void loop() { 

  if(Serial.available() > 0) {          // if data available from reader 
    if((val = Serial.read()) == 10) {   // check for header 
      bytesread = 0; 
      while(bytesread<10) {              // read 10 digit code 
        if( Serial.available() > 0) { 
          val = Serial.read(); 
          if((val == 10)||(val == 13)) { // if header or stop bytes before the 10 digit reading 
            break;                       // stop reading 
          } 
          code[bytesread] = val;         // add the digit           
          bytesread++;                   // ready to read next digit  
        } 
      } 
      if(bytesread == 10) {              // if 10 digit read is complete 
        Serial.print("TAG code is: ");   // possibly a good TAG 
        Serial.println(code);            // print the TAG code 
        if (client.connect())
        {
            char getbuf[80];
            sprintf(getbuf, "GET http://a1lrfid.appspot.com/rfid?scanned_id=%s HTTP/1.0\r\n",
                code);
            Serial.print("Sending command ");
            Serial.println(getbuf);
            client.println(getbuf);
            client.stop();
        }
        else
        {
          Serial.println("Client connect failed");
        }
      } 
      bytesread = 0; 
      delay(500);                       // wait for a second            
    } 
  } 
  if ((millis() & 0x7fff) == 0x7fff) // about twice a minute
  {
    digitalWrite(2,HIGH);
    delay(2);
    digitalWrite(2,LOW);
  }
} 

// extra stuff
// digitalWrite(2, HIGH);             // deactivate RFID reader 

