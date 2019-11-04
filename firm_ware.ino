#include "Wire.h"
#include <stdio.h>
#include <string.h>
#include <limits.h>
#include <math.h>


#define button 2
#define SLAVE_ADDR 0x0D
#define ADDR_PTR 0xB0
#define START_FREQ_R1 0x82
#define START_FREQ_R2 0x83
#define START_FREQ_R3 0x84
#define FREG_INCRE_R1 0x85
#define FREG_INCRE_R2 0x86
#define FREG_INCRE_R3 0x87
#define NUM_INCRE_R1 0x88
#define NUM_INCRE_R2 0x89
#define NUM_SCYCLES_R1 0x8A
#define NUM_SCYCLES_R2 0x8B
#define RE_DATA_R1 0x94
#define RE_DATA_R2 0x95
#define IMG_DATA_R1 0x96
#define IMG_DATA_R2 0x97
#define TEMP_R1 0x92
#define TEMP_R2 0x93
#define CTRL_REG 0x80
#define CTRL_REG2 0x81
#define STATUS_REG 0x8F


// const float MCLK = 16.776*pow(10,6);// AD5933 Internal Clock Speed 16.776 MHz

const float MCLK = 16.000*pow(10,6);// AD5933 External Precision Clock Speed 16.000 MHz
const float start_freq = 1*pow(10,3);// Set start freq, < 100Khz
const float incre_freq = 1*pow(10,3);// Set freq increment
const int incre_num = 99;// Set number of increments,< 511
int state;


//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
//  MAIN METHODS
//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////


void setup() {
  Wire.begin();
  Serial.begin(38400);

  // LED
  pinMode(LED_BUILTIN, OUTPUT); // REAR DATA TRANSFER LED
  pinMode(13, OUTPUT); // FRONT ORANGE INDICATOR LED

  // SG-615
  pinMode(49, OUTPUT); // XTAL-EN ENABLES AD5933 EXTERNAL XTAL

  // AD8130
  pinMode(A10, OUTPUT); // PD-AD8130 ENABLE CURRENT SOURCE

  // ADG774
  pinMode(A8, OUTPUT); // CAL_EN ADG774 CALIBRATION OR LEAD SELECTION
  pinMode(A9, OUTPUT); // CAL_IN ADG774 CALIBRATION OR LEAD SELECTION

  // ADG1608-1
  pinMode(30, OUTPUT); // RESIS_EN ADG1608 R/RC CALIBRATION SELECTION
  pinMode(32, OUTPUT); // RESIS_A0 ADG1608 R/RC CALIBRATION SELECTION
  pinMode(33, OUTPUT); // RESIS_A1 ADG1608 R/RC CALIBRATION SELECTION
  pinMode(34, OUTPUT); // RESIS_A2 ADG1608 R/RC CALIBRATION SELECTION

  // ADG1608-2
  pinMode(43, OUTPUT); // RG_EN ADG1608 IN-AMP RESISTOR GAIN SELECTION
  pinMode(45, OUTPUT); // RG_A0 ADG1608 IN-AMP RESISTOR GAIN SELECTION
  pinMode(46, OUTPUT); // RG_A1 ADG1608 IN-AMP RESISTOR GAIN SELECTION
  pinMode(47, OUTPUT); // RG_A2 ADG1608 IN-AMP RESISTOR GAIN SELECTION

  // ADG1608-3
  pinMode(22, OUTPUT); // IN_AMP_EN ADG1608 RFB SELECTION
  pinMode(24, OUTPUT); // IN_AMP_A0 ADG1608 RFB SELECTION
  pinMode(25, OUTPUT); // IN_AMP_A1 ADG1608 RFB SELECTION
  pinMode(26, OUTPUT); // IN_AMP_A2 ADG1608 RFB SELECTION

  writeData(CTRL_REG,0x0);   //nop - clear ctrl-reg
  writeData(CTRL_REG2,0x10);   //reset ctrl register

  // SG-615
  digitalWrite(49, HIGH); // XTAL-EN ENABLES AD5933 EXTERNAL XTAL

  programReg();

  // Front LED three flashes to indicate setup
  flashLED();
}


void loop(){
  //Read state and enter FSM
    if(Serial.available()>0) {
      state = Serial.parseInt();
      //FSM
      switch(state) {

//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
        // AD5933 commands
//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

        case 59330:
          runSweep();
          break;

        case 59331:  //Program Registers
          programReg();
          break;

        case 59332:  //Measure Temperature
          measureTemperature();
          break;

//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
        // R/RRC calibration selection
//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

        case 116080:
          ADG1608_RC(0); // R73 (1001 1k resistor)
          break;

        case 116081:
          ADG1608_RC(1); // R71 (1002 10k resistor)
          break;

        case 116082:
          ADG1608_RC(2); // R69 (101 100RO resistor)
          break;

        case 116083:
          ADG1608_RC(3); // R67 (751 10k resistor)
          break;

        case 116084:
          ADG1608_RC(4); // R65 (C65 actually 10nF cap)
          break;

        case 116085:
          ADG1608_RC(5);
          break;

        case 116086:
          ADG1608_RC(6);
          break;

        case 116087:
          ADG1608_RC(7);
          break;

//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
        // IN-AMP gain selection
//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

        case 216080:
          ADG1608_GAIN(0);
          break;

        case 216081:
          ADG1608_GAIN(1);
          break;

        case 216082:
          ADG1608_GAIN(2);
          break;

        case 216083:
          ADG1608_GAIN(3);
          break;

        case 216084:
          ADG1608_GAIN(4);
          break;

        case 216085:
          ADG1608_GAIN(5);
          break;

        case 216086:
          ADG1608_GAIN(6);
          break;

        case 216087:
          ADG1608_GAIN(7);
          break;

//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
        // RFB selection
//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

        case 316080:
          ADG1608_RFB(0);
          break;

        case 316081:
          ADG1608_RFB(1);
          break;

        case 316082:
          ADG1608_RFB(2);
          break;

        case 316083:
          ADG1608_RFB(3);
          break;

        case 316084:
          ADG1608_RFB(4);
          break;

        case 316085:
          ADG1608_RFB(5);
          break;

        case 316086:
          ADG1608_RFB(6);
          break;

        case 316087:
          ADG1608_RFB(7);
          break;

//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
        // Leads or Calibration selection
//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

        case 7740:
          ADG774('Z');
          break;

        case 7741:
          ADG774('A');
          break;

        case 7742:
          ADG774('B');
          break;

//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
        // Front LED indicator state selection
//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

        case 10:
          LED(false);
          break;

        case 11:
          LED(true);
          break;

      /////Programming Device Registers/////
      }
      Serial.flush();
    }
}


//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
//  SWEEP METHODS
//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////


void programReg(){
  // Set Range 1, PGA gain 1
  writeData(CTRL_REG,0x01); // # D8/0x80/10000000 0x01/1 // turn to 0x07 to change p-p to 1
  writeData(CTRL_REG2,0x08); // Enable AD5933 external clock setting (delete to turn off)
  // Set settling cycles
  writeData(NUM_SCYCLES_R1, 0x07);
  writeData(NUM_SCYCLES_R2, 0xFF);
  // Start frequency of 1kHz
  writeData(START_FREQ_R1, getFrequency(start_freq,1));
  writeData(START_FREQ_R2, getFrequency(start_freq,2));
  writeData(START_FREQ_R3, getFrequency(start_freq,3));
  // Increment by 1 kHz
  writeData(FREG_INCRE_R1, getFrequency(incre_freq,1)),
  writeData(FREG_INCRE_R2, getFrequency(incre_freq,2)),
  writeData(FREG_INCRE_R3, getFrequency(incre_freq,3));
  // Points in frequency sweep (100), max 511
  writeData(NUM_INCRE_R1, (incre_num & 0x001F00)>>0x08 );
  writeData(NUM_INCRE_R2, (incre_num & 0x0000FF));
}


//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
//  RUN SWEEP
//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////


void runSweepOFF() {
  short re;
  short img;
  double freq;
  double kfreq;
  double mag;
  double phase;
  double phasei;
  double phasex;
  double phasey;
  double gain;
  double impedance;
  double sys_phase;
  int flop=0;
  int i=0;
  int gf=1;
  double x;
  double y;
  double z;
  double t;
  double ycal;
  double zcal;
  programReg();


  LED(true);
  AD8130(true);
  ADG774('A');
  ADG1608_RC(0);
  ADG1608_GAIN(1);
  ADG1608_RFB(1);

  delay(500);

  writeData(CTRL_REG,(readData(CTRL_REG) & 0x07) | 0xB0); // 1. Standby '10110000' Mask D8-10 of avoid tampering with gains
  writeData(CTRL_REG,(readData(CTRL_REG) & 0x07) | 0x10); // 2. Initialize sweep
  writeData(CTRL_REG,(readData(CTRL_REG) & 0x07) | 0x20); // 3. Start sweep

  while((readData(STATUS_REG) & 0x07) < 4 ) {  // Check that status reg != 4, sweep not complete
    delay(1000); // delay between measurements
    int flag = readData(STATUS_REG)& 2;
    if (flag==2) {

        freq = start_freq + i*incre_freq;
        freq = freq/1000;
        double x = freq * 1.0;

        byte R1 = readData(RE_DATA_R1);
        byte R2 = readData(RE_DATA_R2);
        re = (R1 << 8) | R2;
        R1  = readData(IMG_DATA_R1);
        R2  = readData(IMG_DATA_R2);
        img = (R1 << 8) | R2;
        double y = (double)re * 1.0;
        double z = (double)img * 1.0;
        R1 = readData(RE_DATA_R1);
        R2 = readData(RE_DATA_R2);
        re = (R1 << 8) | R2;
        R1  = readData(IMG_DATA_R1);
        R2  = readData(IMG_DATA_R2);
        img = (R1 << 8) | R2;
        double ycal = (double)re * 1.0;
        double zcal = (double)img * 1.0;
        double t = measureTemperatureDouble();
        t = (double)t * 1.0;

        sendToPC(&x, &y, &z, &t, &ycal, &zcal);

        if((readData(STATUS_REG) & 0x07) < 4 ){ //Increment frequency
           writeData(CTRL_REG,(readData(CTRL_REG) & 0x07) | 0x30); // increment
           i++;
           gf++;
           flop = 0;
         }

      //digitalWrite(LED_BUILTIN, LOW);    // turn the LED off by making the voltage LOW
    }
  }
//  writeData(CTRL_REG,0xA0);
  writeData(CTRL_REG,(readData(CTRL_REG) & 0x07) | 0xA0); //Power down

  delay(2000);
  allLOW();

}

//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
//  RUN SWEEP
//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////


void runSweep() {
  short re;
  short img;
  double freq;
  double kfreq;
  double mag;
  double phase;
  double phasei;
  double phasex;
  double phasey;
  double gain;
  double impedance;
  double sys_phase;
  int flop=0;
  int i=0;
  int gf=1;
  double x;
  double y;
  double z;
  double t;
  double ycal;
  double zcal;
  programReg();


  LED(true);
  AD8130(true);
  ADG774('A');
  ADG1608_RC(0);
  ADG1608_GAIN(1);
  ADG1608_RFB(1);

  delay(500);

  writeData(CTRL_REG,(readData(CTRL_REG) & 0b111) | 0b10110000); // 1. Standby '10110000' Mask D8-10 of avoid tampering with gains
  writeData(CTRL_REG,(readData(CTRL_REG) & 0b111) | 0b10000); // 2. Initialize sweep
  writeData(CTRL_REG,(readData(CTRL_REG) & 0b111) | 0b100000); // 3. Start sweep

// run while the Status register says that the sweep is not complete
  while((readData(STATUS_REG) & 0b111) < 0b100 ) {  // reads Status Register, to see if D2 is less than 1 (i.e. 0), 0 in at D2 in this register ('Status Register') indicates that the frequency sweep is complete
    delay(1000); // delay between measurements
    int flag = readData(STATUS_REG)& 0b10; // reads Status Register, uses an and '&' bit wise operator to see if the register is equal to 1 at the D1 bit, this indicates if there is valid real or imaginary data is avaliable
    if (flag==2) {

        freq = start_freq + i*incre_freq;
        freq = freq/1000;
        double x = freq * 1.0;

      if (flop==0) {
        delay(100);
        ADG774('A'); // shifts leads to external lead circuit

        byte R1 = readData(RE_DATA_R1);
        byte R2 = readData(RE_DATA_R2);
        re = (R1 << 8) | R2;
        R1  = readData(IMG_DATA_R1);
        R2  = readData(IMG_DATA_R2);
        img = (R1 << 8) | R2;
        y = (double)re * 1.0;
        z = (double)img * 1.0;

      if((readData(STATUS_REG) & 0b111) < 0b100 ){ //Increment frequency
        writeData(CTRL_REG,(readData(CTRL_REG) & 0x07) | 0x40); // repeats
        flop = 1; // i++;
        flag = readData(STATUS_REG)& 0b10;
        }
      }
      if (flag==2) {
        if (flop==1) {
            ADG774('B'); // shifts leads to internal calibration circuit
            ADG1608_RC(1); // shifts to R73 (1001 1k resistor)
            delay(100); // wait for 10 ms

            byte R1 = readData(RE_DATA_R1);
            byte R2 = readData(RE_DATA_R2);
            re = (R1 << 8) | R2;
            R1  = readData(IMG_DATA_R1);
            R2  = readData(IMG_DATA_R2);
            img = (R1 << 8) | R2;
            ycal = (double)re * 1.0;
            zcal = (double)img * 1.0;
            delay(150);
            t = measureTemperatureDouble();
            t = (double)t * 1.0;

            sendToPC(&x, &y, &z, &t, &ycal, &zcal);
      }
        if((readData(STATUS_REG) & 0b111) < 0b100 ){ //Increment frequency
           writeData(CTRL_REG,(readData(CTRL_REG) & 0x07) | 0x30); // increment
           i++;
           gf++;
           flop = 0;
        }
      }




      //digitalWrite(LED_BUILTIN, LOW);    // turn the LED off by making the voltage LOW
    }
  }
//  writeData(CTRL_REG,0xA0);
  writeData(CTRL_REG,(readData(CTRL_REG) & 0x07) | 0xA0); //Power down

  delay(2000);
  allLOW();

}


//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
//  DATA METHODS
//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////


void writeData(int addr, int data) {
 Wire.beginTransmission(SLAVE_ADDR);
 Wire.write(addr);
 Wire.write(data);
 Wire.endTransmission();
 delay(1);
}

int readData(int addr){
  int data;
  Wire.beginTransmission(SLAVE_ADDR);
  Wire.write(ADDR_PTR);
  Wire.write(addr);
  Wire.endTransmission();
  delay(1);

  Wire.requestFrom(SLAVE_ADDR,1);
  if (Wire.available() >= 1){
    data = Wire.read();
  }
  else {
    data = -1;
  }
  delay(1);
  return data;
}


//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
//  EXTRA METHODS
//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////


boolean measureTemperature() {
  // Measure temperature '10010000'
  writeData(CTRL_REG, 0x90);
  //TODO: necessary to write to second control register?
  delay(10); // wait for 10 ms
  //Check status reg for temp measurement available
  int flag = readData(STATUS_REG)& 1;
  if (flag == 1) {
    // Temperature is available
    int temperatureData = readData(TEMP_R1) << 8;
    temperatureData |= readData(TEMP_R2);
    temperatureData &= 0x3FFF; // remove first two bits
    if (temperatureData & 0x2000 == 1) { // negative temperature
      temperatureData -= 0x4000;
    }
    double val = double(temperatureData) / 32;
    temperatureData /= 32;
    Serial.print("Temperature: ");
    Serial.print(val);
    //Serial.write(176);  //degree sign
    Serial.println("C.");
    // Power Down '10100000'
    writeData(CTRL_REG,0xA0);
    return true;
  } else {
    return false;
  }
}

double measureTemperatureDouble(){
  // Measure temperature '10010000'
  writeData(CTRL_REG, 0x90);
  //TODO: necessary to write to second control register?
  delay(10); // wait for 10 ms
  //Check status reg for temp measurement available
  int flag = readData(STATUS_REG)& 1;
  if (flag == 1) {
    // Temperature is available
    int temperatureData = readData(TEMP_R1) << 8;
    temperatureData |= readData(TEMP_R2);
    temperatureData &= 0x3FFF; // remove first two bits
    if (temperatureData & 0x2000 == 1) { // negative temperature
      temperatureData -= 0x4000;
    }
    double val = double(temperatureData) / 32;
    double valZero = double(0.0);
    temperatureData /= 32;
    return val;
  } else {
    double valZero = double(0.0);
    return valZero;
  }
}



byte getFrequency(float freq, int n){
  long val = long((freq/(MCLK/4)) * pow(2,27));
  byte code;
    switch (n) {
      case 1:
        code = (val & 0xFF0000) >> 0x10;
        break;
      case 2:
        code = (val & 0x00FF00) >> 0x08;
        break;
      case 3:
        code = (val & 0x0000FF);
        break;
      default:
        code = 0;
    }
  return code;
}


void sendToPC(int* data1, int* data2, int* data3)
{
  byte* byteData1 = (byte*)(data1);
  byte* byteData2 = (byte*)(data2);
  byte* byteData3 = (byte*)(data3);
  byte buf[6] = {byteData1[0], byteData1[1],
                 byteData2[0], byteData2[1],
                 byteData3[0], byteData3[1]};
  Serial.write(buf, 6);
}


void sendToPC(double* data1, double* data2, double* data3, double* data4, double* data5, double* data6)
{
  byte* byteData1 = (byte*)(data1);
  byte* byteData2 = (byte*)(data2);
  byte* byteData3 = (byte*)(data3);
  byte* byteData4 = (byte*)(data4);
  byte* byteData5 = (byte*)(data5);
  byte* byteData6 = (byte*)(data6);
  byte buf[24] = {byteData1[0], byteData1[1], byteData1[2], byteData1[3],
                 byteData2[0], byteData2[1], byteData2[2], byteData2[3],
                 byteData3[0], byteData3[1], byteData3[2], byteData3[3],
                 byteData4[0], byteData4[1], byteData4[2], byteData4[3],
                 byteData5[0], byteData5[1], byteData5[2], byteData5[3],
                 byteData6[0], byteData6[1], byteData6[2], byteData6[3]};
  Serial.write(buf, 24);
}


void flashLED(){
  delay(250);
  digitalWrite(13, HIGH); // FRONT ORANGE INDICATOR LED
  delay(250);
  digitalWrite(13, LOW); // FRONT ORANGE INDICATOR LED
  delay(250);
  digitalWrite(13, HIGH); // FRONT ORANGE INDICATOR LED
  delay(250);
  digitalWrite(13, LOW); // FRONT ORANGE INDICATOR LED
  delay(250);
  digitalWrite(13, HIGH); // FRONT ORANGE INDICATOR LED
  delay(250);
  digitalWrite(13, LOW); // FRONT ORANGE INDICATOR LED
  delay(250);
  digitalWrite(13, HIGH);
  delay(250);
  digitalWrite(13, LOW);
  delay(250);
}

void onLED(){
  digitalWrite(13, HIGH); // FRONT ORANGE INDICATOR LED
  delay(1000);
  digitalWrite(13, LOW); // FRONT ORANGE INDICATOR LED
  delay(1000);
  digitalWrite(13, HIGH); // FRONT ORANGE INDICATOR LED
  delay(1000);
  digitalWrite(13, LOW); // FRONT ORANGE INDICATOR LED
  delay(1000);
  digitalWrite(13, HIGH);
  delay(1000);
  digitalWrite(13, LOW);
}

void on774(){
  ADG774('A');
  LED(true);
}


void off774(){
  ADG774('Z');
  LED(false);
}

void allLOW(){
  LED(false);
  AD8130(false);
  ADG774('Z');
  ADG1608_RC(0);
  ADG1608_GAIN(0);
  ADG1608_RFB(0);
  }


///////////////////////////////
// IC FUNCTIONS
///////////////////////////////


void LED(boolean state){
  switch(state) {
        case true:
          digitalWrite(13, HIGH); // FRONT ORANGE INDICATOR LED ON
          break;

        case false:  //Measure Temperature
          digitalWrite(13, LOW); // FRONT ORANGE INDICATOR LED OFF
          break;
      }
  }

void AD8130(boolean state){
  switch(state) {
        case true:  //Program Registers
          digitalWrite(A10, HIGH); // PD-AD8130 ENABLE CURRENT SOURCE
          break;

        case false:  //Measure Temperature
          digitalWrite(A10, LOW); // PD-AD8130 DISABLE CURRENT SOURCE
          break;
      }
  }

void ADG774(char route){
    switch(route) {
        case 'A':  //Program Registers
          digitalWrite(A8, LOW); // CAL_EN ADG774 CALIBRATION OR LEAD SELECTION
          digitalWrite(A9, LOW); // CAL_IN ADG774 CALIBRATION OR LEAD SELECTION
          break;

        case 'B':  //Measure Temperature
          digitalWrite(A8, LOW); // CAL_EN ADG774 CALIBRATION OR LEAD SELECTION
          digitalWrite(A9, HIGH); // CAL_IN ADG774 CALIBRATION OR LEAD SELECTION
          break;

        case 'Z':  //Measure Temperature
          digitalWrite(A8, HIGH); // CAL_EN ADG774 CALIBRATION OR LEAD SELECTION
          digitalWrite(A9, LOW); // CAL_IN ADG774 CALIBRATION OR LEAD SELECTION
          break;
      }
  }

void ADG1608_RC(int route){
    switch(route) {
        case 0:  //Program Registers
          digitalWrite(30, LOW); // RESIS_EN ADG1608 R/RC CALIBRATION SELECTION
          digitalWrite(32, LOW); // RESIS_A0 ADG1608 R/RC CALIBRATION SELECTION
          digitalWrite(33, LOW); // RESIS_A1 ADG1608 R/RC CALIBRATION SELECTION
          digitalWrite(34, LOW); // RESIS_A2 ADG1608 R/RC CALIBRATION SELECTION
          break;
        case 1:  //Program Registers
          digitalWrite(30, HIGH); // RESIS_EN ADG1608 R/RC CALIBRATION SELECTION
          digitalWrite(32, LOW); // RESIS_A0 ADG1608 R/RC CALIBRATION SELECTION
          digitalWrite(33, LOW); // RESIS_A1 ADG1608 R/RC CALIBRATION SELECTION
          digitalWrite(34, LOW); // RESIS_A2 ADG1608 R/RC CALIBRATION SELECTION
          break;

        case 2:  //Measure Temperature
          digitalWrite(30, HIGH); // RESIS_EN ADG1608 R/RC CALIBRATION SELECTION
          digitalWrite(32, HIGH); // RESIS_A0 ADG1608 R/RC CALIBRATION SELECTION
          digitalWrite(33, LOW); // RESIS_A1 ADG1608 R/RC CALIBRATION SELECTION
          digitalWrite(34, LOW); // RESIS_A2 ADG1608 R/RC CALIBRATION SELECTION
          break;

        case 3:  //Program Registers
          digitalWrite(30, HIGH); // RESIS_EN ADG1608 R/RC CALIBRATION SELECTION
          digitalWrite(32, LOW); // RESIS_A0 ADG1608 R/RC CALIBRATION SELECTION
          digitalWrite(33, HIGH); // RESIS_A1 ADG1608 R/RC CALIBRATION SELECTION
          digitalWrite(34, LOW); // RESIS_A2 ADG1608 R/RC CALIBRATION SELECTION
          break;

        case 4:  //Measure Temperature
          digitalWrite(30, HIGH); // RESIS_EN ADG1608 R/RC CALIBRATION SELECTION
          digitalWrite(32, HIGH); // RESIS_A0 ADG1608 R/RC CALIBRATION SELECTION
          digitalWrite(33, HIGH); // RESIS_A1 ADG1608 R/RC CALIBRATION SELECTION
          digitalWrite(34, LOW); // RESIS_A2 ADG1608 R/RC CALIBRATION SELECTION
          break;

        case 5:  //Program Registers
          digitalWrite(30, HIGH); // RESIS_EN ADG1608 R/RC CALIBRATION SELECTION
          digitalWrite(32, LOW); // RESIS_A0 ADG1608 R/RC CALIBRATION SELECTION
          digitalWrite(33, LOW); // RESIS_A1 ADG1608 R/RC CALIBRATION SELECTION
          digitalWrite(34, HIGH); // RESIS_A2 ADG1608 R/RC CALIBRATION SELECTION
          break;

        case 6:  //Measure Temperature
          digitalWrite(30, HIGH); // RESIS_EN ADG1608 R/RC CALIBRATION SELECTION
          digitalWrite(32, HIGH); // RESIS_A0 ADG1608 R/RC CALIBRATION SELECTION
          digitalWrite(33, LOW); // RESIS_A1 ADG1608 R/RC CALIBRATION SELECTION
          digitalWrite(34, HIGH); // RESIS_A2 ADG1608 R/RC CALIBRATION SELECTION
          break;

        case 7:  //Program Registers
          digitalWrite(30, HIGH); // RESIS_EN ADG1608 R/RC CALIBRATION SELECTION
          digitalWrite(32, LOW); // RESIS_A0 ADG1608 R/RC CALIBRATION SELECTION
          digitalWrite(33, HIGH); // RESIS_A1 ADG1608 R/RC CALIBRATION SELECTION
          digitalWrite(34, HIGH); // RESIS_A2 ADG1608 R/RC CALIBRATION SELECTION
          break;

        case 8:  //Measure Temperature
          digitalWrite(30, HIGH); // RESIS_EN ADG1608 R/RC CALIBRATION SELECTION
          digitalWrite(32, HIGH); // RESIS_A0 ADG1608 R/RC CALIBRATION SELECTION
          digitalWrite(33, HIGH); // RESIS_A1 ADG1608 R/RC CALIBRATION SELECTION
          digitalWrite(34, HIGH); // RESIS_A2 ADG1608 R/RC CALIBRATION SELECTION
          break;
      }
  }

void ADG1608_GAIN(int route){
    switch(route) {
        case 0:  //Program Registers
          digitalWrite(43, LOW); // RG_EN ADG1608 IN-AMP RESISTOR GAIN SELECTION
          digitalWrite(45, LOW); // RG_A0 ADG1608 IN-AMP RESISTOR GAIN SELECTION
          digitalWrite(46, LOW); // RG_A1 ADG1608 IN-AMP RESISTOR GAIN SELECTION
          digitalWrite(47, LOW); // RG_A2 ADG1608 IN-AMP RESISTOR GAIN SELECTION
          break;

        case 1:  //Program Registers
          digitalWrite(43, HIGH); // RG_EN ADG1608 IN-AMP RESISTOR GAIN SELECTION
          digitalWrite(45, LOW); // RG_A0 ADG1608 IN-AMP RESISTOR GAIN SELECTION
          digitalWrite(46, LOW); // RG_A1 ADG1608 IN-AMP RESISTOR GAIN SELECTION
          digitalWrite(47, LOW); // RG_A2 ADG1608 IN-AMP RESISTOR GAIN SELECTION
          break;

        case 2:  //Measure Temperature
          digitalWrite(43, HIGH); // RG_EN ADG1608 IN-AMP RESISTOR GAIN SELECTION
          digitalWrite(45, HIGH); // RG_A0 ADG1608 IN-AMP RESISTOR GAIN SELECTION
          digitalWrite(46, LOW); // RG_A1 ADG1608 IN-AMP RESISTOR GAIN SELECTION
          digitalWrite(47, LOW); // RG_A2 ADG1608 IN-AMP RESISTOR GAIN SELECTION
          break;

        case 3:  //Program Registers
          digitalWrite(43, HIGH); // RG_EN ADG1608 IN-AMP RESISTOR GAIN SELECTION
          digitalWrite(45, LOW); // RG_A0 ADG1608 IN-AMP RESISTOR GAIN SELECTION
          digitalWrite(46, HIGH); // RG_A1 ADG1608 IN-AMP RESISTOR GAIN SELECTION
          digitalWrite(47, LOW); // RG_A2 ADG1608 IN-AMP RESISTOR GAIN SELECTION
          break;

        case 4:  //Measure Temperature
          digitalWrite(43, HIGH); // RG_EN ADG1608 IN-AMP RESISTOR GAIN SELECTION
          digitalWrite(45, HIGH); // RG_A0 ADG1608 IN-AMP RESISTOR GAIN SELECTION
          digitalWrite(46, HIGH); // RG_A1 ADG1608 IN-AMP RESISTOR GAIN SELECTION
          digitalWrite(47, LOW); // RG_A2 ADG1608 IN-AMP RESISTOR GAIN SELECTION
          break;

        case 5:  //Program Registers
          digitalWrite(43, HIGH); // RG_EN ADG1608 IN-AMP RESISTOR GAIN SELECTION
          digitalWrite(45, LOW); // RG_A0 ADG1608 IN-AMP RESISTOR GAIN SELECTION
          digitalWrite(46, LOW); // RG_A1 ADG1608 IN-AMP RESISTOR GAIN SELECTION
          digitalWrite(47, HIGH); // RG_A2 ADG1608 IN-AMP RESISTOR GAIN SELECTION
          break;

        case 6:  //Measure Temperature
          digitalWrite(43, HIGH); // RG_EN ADG1608 IN-AMP RESISTOR GAIN SELECTION
          digitalWrite(45, HIGH); // RG_A0 ADG1608 IN-AMP RESISTOR GAIN SELECTION
          digitalWrite(46, LOW); // RG_A1 ADG1608 IN-AMP RESISTOR GAIN SELECTION
          digitalWrite(47, HIGH); // RG_A2 ADG1608 IN-AMP RESISTOR GAIN SELECTION
          break;

        case 7:  //Program Registers
          digitalWrite(43, HIGH); // RG_EN ADG1608 IN-AMP RESISTOR GAIN SELECTION
          digitalWrite(45, LOW); // RG_A0 ADG1608 IN-AMP RESISTOR GAIN SELECTION
          digitalWrite(46, HIGH); // RG_A1 ADG1608 IN-AMP RESISTOR GAIN SELECTION
          digitalWrite(47, HIGH); // RG_A2 ADG1608 IN-AMP RESISTOR GAIN SELECTION
          break;

        case 8:  //Measure Temperature
          digitalWrite(43, HIGH); // RG_EN ADG1608 IN-AMP RESISTOR GAIN SELECTION
          digitalWrite(45, HIGH); // RG_A0 ADG1608 IN-AMP RESISTOR GAIN SELECTION
          digitalWrite(46, HIGH); // RG_A1 ADG1608 IN-AMP RESISTOR GAIN SELECTION
          digitalWrite(47, HIGH); // RG_A2 ADG1608 IN-AMP RESISTOR GAIN SELECTION
          break;
      }
  }

void ADG1608_RFB(int route){
    switch(route) {
        case 0:  //Program Registers
          digitalWrite(22, LOW); // IN_AMP_EN ADG1608 RFB SELECTION
          digitalWrite(24, LOW); // IN_AMP_A0 ADG1608 RFB SELECTION
          digitalWrite(25, LOW); // IN_AMP_A1 ADG1608 RFB SELECTION
          digitalWrite(26, LOW); // IN_AMP_A2 ADG1608 RFB SELECTION
          break;

        case 1:  //Program Registers
          digitalWrite(22, HIGH); // IN_AMP_EN ADG1608 RFB SELECTION
          digitalWrite(24, LOW); // IN_AMP_A0 ADG1608 RFB SELECTION
          digitalWrite(25, LOW); // IN_AMP_A1 ADG1608 RFB SELECTION
          digitalWrite(26, LOW); // IN_AMP_A2 ADG1608 RFB SELECTION
          break;

        case 2:  //Measure Temperature
          digitalWrite(22, HIGH); // IN_AMP_EN ADG1608 RFB SELECTION
          digitalWrite(24, HIGH); // IN_AMP_A0 ADG1608 RFB SELECTION
          digitalWrite(25, LOW); // IN_AMP_A1 ADG1608 RFB SELECTION
          digitalWrite(26, LOW); // IN_AMP_A2 ADG1608 RFB SELECTION
          break;

        case 3:  //Program Registers
          digitalWrite(22, HIGH); // IN_AMP_EN ADG1608 RFB SELECTION
          digitalWrite(24, LOW); // IN_AMP_A0 ADG1608 RFB SELECTION
          digitalWrite(25, HIGH); // IN_AMP_A1 ADG1608 RFB SELECTION
          digitalWrite(26, LOW); // IN_AMP_A2 ADG1608 RFB SELECTION
          break;

        case 4:  //Measure Temperature
          digitalWrite(22, HIGH); // IN_AMP_EN ADG1608 RFB SELECTION
          digitalWrite(24, HIGH); // IN_AMP_A0 ADG1608 RFB SELECTION
          digitalWrite(25, HIGH); // IN_AMP_A1 ADG1608 RFB SELECTION
          digitalWrite(26, LOW); // IN_AMP_A2 ADG1608 RFB SELECTION
          break;

        case 5:  //Program Registers
          digitalWrite(22, HIGH); // IN_AMP_EN ADG1608 RFB SELECTION
          digitalWrite(24, LOW); // IN_AMP_A0 ADG1608 RFB SELECTION
          digitalWrite(25, LOW); // IN_AMP_A1 ADG1608 RFB SELECTION
          digitalWrite(26, HIGH); // IN_AMP_A2 ADG1608 RFB SELECTION
          break;

        case 6:  //Measure Temperature
          digitalWrite(22, HIGH); // IN_AMP_EN ADG1608 RFB SELECTION
          digitalWrite(24, HIGH); // IN_AMP_A0 ADG1608 RFB SELECTION
          digitalWrite(25, LOW); // IN_AMP_A1 ADG1608 RFB SELECTION
          digitalWrite(26, HIGH); // IN_AMP_A2 ADG1608 RFB SELECTION
          break;

        case 7:  //Program Registers
          digitalWrite(22, HIGH); // IN_AMP_EN ADG1608 RFB SELECTION
          digitalWrite(24, LOW); // IN_AMP_A0 ADG1608 RFB SELECTION
          digitalWrite(25, HIGH); // IN_AMP_A1 ADG1608 RFB SELECTION
          digitalWrite(26, HIGH); // IN_AMP_A2 ADG1608 RFB SELECTION
          break;

        case 8:  //Measure Temperature
          digitalWrite(22, HIGH); // IN_AMP_EN ADG1608 RFB SELECTION
          digitalWrite(24, HIGH); // IN_AMP_A0 ADG1608 RFB SELECTION
          digitalWrite(25, HIGH); // IN_AMP_A1 ADG1608 RFB SELECTION
          digitalWrite(26, HIGH); // IN_AMP_A2 ADG1608 RFB SELECTION
          break;
      }
  }




