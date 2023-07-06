#include <Adafruit_ILI9341.h>
#include <Adafruit_BusIO_Register.h>
#include <Adafruit_I2CDevice.h>
#include <Adafruit_I2CRegister.h>
#include <Adafruit_SPIDevice.h>
#include <Servo.h>
#include <Wire.h>
#include <hd44780.h>
#include <hd44780ioClass/hd44780_I2Cexp.h>


//threshhold de tempo para resetar o vocal
unsigned long timeThreshold = 1200;
unsigned long singerMillis = 0;
int singerAngle = 50;
int singerPot = 10;
bool singerState = true;


//inicio codigo led
#include <FastLED.h>

#define NUM_LEDS 30
#define DATA_PIN 5
#define CLOCK_PIN 13

// Inicialize o objeto do display
hd44780_I2Cexp lcd;

CRGB cores[4][2] = {
  {CRGB::BlueViolet, CRGB::SeaGreen}, // Sereno
  {CRGB::Blue, CRGB::Green},       // Calmo
  {CRGB::Red, CRGB::Blue},     // Padrão
  {CRGB::Green, CRGB::Orange}  // Animado
};
int corAtual = 0;

CRGB leds[NUM_LEDS];
String modo;
unsigned long previousMillis = 0;
unsigned long interval = 1000;
bool flag =true;
int pos = 0;

void limparLeds(CRGB cor) {
  for (int i = 0; i < NUM_LEDS; i++) {
    leds[i] = cor;
  }
  FastLED.show();
}


void acendeLeds(int pos) {
  limparLeds(cores[corAtual][1]);
  //Serial.println(corAtual);
  for (int i = pos-6; i < NUM_LEDS; i += 6) {
    if (i<0) {
      continue;
    }
    leds[i] = cores[corAtual][0];
    if (i<1) {
      continue;
    }
    leds[i - 1] = cores[corAtual][0];
    if (i<2) {
      continue;
    }
    leds[i - 2] = cores[corAtual][0];
    
  }
  //leds[0] = CRGB::Black;
  FastLED.show();
}


void batida(){
  acendeLeds(pos);
  //Serial.println(pos);
  pos++;
  pos %= 6;
}

void estatico() {
  for (int i = 0; i < NUM_LEDS; i++) {

    if (flag) {
      leds[i] = cores[corAtual][0];
      flag = false;

    } else {
      leds[i] = cores[corAtual][1];
      flag = true;
    }
  }
}

void setCores(String modo) {
  limparLeds(CRGB::Black);
  if (modo == "batida"){
    batida();
  }
  else if (modo == "sereno") {
    corAtual = 0;
    interval = 1000;
    estatico();
  }
  else if (modo == "calmo") {
    interval = 800;
    corAtual = 1;
    estatico();
  }
  else if (modo == "padrao") {
    interval = 600;
    corAtual = 2;
    estatico();
  }
  else if (modo == "animado") {
    interval = 400;
    corAtual = 3;
    estatico();
  }
  FastLED.show();
} 

//fim codigo led




Servo servo1;
Servo servo2;
Servo servo3;
Servo servo4;

int pinoServo1 = 13; // servo do braço direito do batera
int pinoServo2 = 12; // servo do braço esquerdo do batera
int pinoServo3 = 11; // servo do braço do vocalista
int pinoServo4 = 8; // servo do baixo

int servo1StartAngle = 90;
int servo2StartAngle = 130;
int servo3StartAngle = 110;
int servo4StartAngle = 90;

int ledBoca = 10;

bool bassPos = true;
int bassAngle = 0;
String energia = ""; //energia da musica

//funcao controle baixo
void bass(int angle){
  //Serial.println(angle);

  if (bassPos){
    servo4.write(servo4StartAngle + angle);
   // Serial.println(servo4StartAngle + angle);
  }else{
    servo4.write(servo4StartAngle - angle);
  //  Serial.println(servo4StartAngle - angle);
  }
  bassPos=!bassPos;
}

void moveSinger(){
  Serial.println(singerState);
  
  if (singerState){
    servo3.write(90);
  }else{
    servo3.write(90+singerAngle);
  }
  singerState=!singerState;
}

void DrumsCycle() {
  int servoMaxRangeAngle = 60;
  if (flag){
    servo1.write(50);  // direito
    servo2.write(40);
    flag=false;
  }else{
    servo1.write(120);  // direito
    servo2.write(120);
    flag=true;
  }
}


void setup() {
  Serial.begin(115200);

  Wire.begin();
  // Inicialize o display
  lcd.begin(20, 4);
  
  //setup led
  FastLED.addLeds<WS2812B, DATA_PIN, RGB>(leds, NUM_LEDS);  // GRB ordering is typical
  FastLED.setTemperature(UncorrectedTemperature);

  servo1.attach(pinoServo1);
  servo2.attach(pinoServo2);
  servo3.attach(pinoServo3);
  servo4.attach(pinoServo4);

  servo1.write(servo1StartAngle);
  servo2.write(servo2StartAngle);
  servo3.write(servo3StartAngle);
  servo4.write(servo4StartAngle);

  pinMode(ledBoca, OUTPUT);
  analogWrite(ledBoca, 0);
  //servo1StartAngle = servo1.read();
  //servo2StartAngle = servo2.read();
  //servo3StartAngle = servo3.read();
}

void loop() {

  unsigned long currentMillis = millis();//tempo para led
  if (Serial.available() > 0) {
    String texto = Serial.readStringUntil('\n');
    
    texto.trim();
    
    //Serial.println("Texto: " + texto);
    
    previousMillis = currentMillis;
    if (texto.startsWith("batida")) {
      setCores(texto);
    } else if (texto.startsWith("voz")) {
      int singAmplitudeAngle = map(texto.substring(4, texto.length()).toInt(), 0, 100, 0, 93);
      if (singAmplitudeAngle > singerPot){
        if (singerState){
          moveSinger();
        }
        singerMillis = currentMillis;
      }
      int ledLight = map(texto.substring(4, texto.length()).toInt(), 0, 100, 0, 250);
      Sing(singAmplitudeAngle, ledLight);
    }
    else if (texto.startsWith("sereno") || texto.startsWith("calmo") || texto.startsWith("padrao") || texto.startsWith("animado")){
      setCores(texto);
    }
    else if (texto.startsWith("baixa")){
      bassAngle = 10;
    }
    else if (texto.startsWith("media")){
      bassAngle = 20;
    }
    else if (texto.startsWith("alta")){
      bassAngle = 25;
    }
    else if (texto.startsWith("altissima")){
      bassAngle = 30;
    }
    else if (texto.startsWith("baixo")){
      bass(bassAngle);
    }
    else if (texto.startsWith("batera")){
      DrumsCycle();
    }

    if(texto.startsWith("letra ")){
      String palavra = "letra ";
      lcd.clear();  // Limpar o display
      texto = texto.substring(palavra.length(), texto.length());  // Remover "letra" do texto
    
      int textSize = texto.length(); // Tamanho do texto
      int numLines = (textSize / 20) + 1; // Quantidade de linhas que o texto vai ocupar
      int line; // Linha atual
    
      for (int i = 0; i < numLines; i++) {
        // Definir a linha atual
        line = i;
    
        // Se for maior que 3, modula por 4 para voltar à primeira linha
        if (line > 3) {
          line %= 4;
        }
    
        // Setar o cursor para a linha atual
        lcd.setCursor(0,line);
        
        // Imprimir no LCD o trecho do texto que cabe na linha atual
        if (textSize > 20) {
          lcd.print(texto.substring(i * 20, (i + 1) * 20));
          textSize -= 20;
        } else {
          lcd.print(texto.substring(i * 20, i * 20 + textSize));
        }
      }
    }
  }
  if (currentMillis > singerMillis + timeThreshold){
      if (!singerState){
        moveSinger();
      }
  }
}

void Sing(int singAmplitudeAngle, int ledLight) {
  int servoAngle = servo3StartAngle - singAmplitudeAngle;
  analogWrite(ledBoca, ledLight);
  //servo3.write(servoAngle);
}