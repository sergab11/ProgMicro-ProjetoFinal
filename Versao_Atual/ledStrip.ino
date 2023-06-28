#include <FastLED.h>

#define NUM_LEDS 30
#define DATA_PIN 5
#define CLOCK_PIN 13

CRGB cores[4][2] = {
  {CRGB::Blue, CRGB::Green},    // Sereno
  {CRGB::BlueViolet, CRGB::SeaGreen},   // Calmo
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
  Serial.println(corAtual);
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
}
void estatico(){
  for (int i = 0; i < NUM_LEDS; i++) {
      
      if(flag){
        leds[i] = cores[corAtual][0];
        flag=false;
        
      } else {
        leds[i] = cores[corAtual][1];
        flag = true;
      }
    }
}
void batida(){
  acendeLeds(pos);
  Serial.println(pos);
  pos++;
  pos %= 6;
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
} 


void setup() {
  Serial.begin(9800);
  FastLED.addLeds<WS2812B, DATA_PIN, RGB>(leds, NUM_LEDS);  // GRB ordering is typical
  FastLED.setTemperature(UncorrectedTemperature);
}

void loop() {
  unsigned long currentMillis = millis();
  if (Serial.available()) {
    modo = Serial.readStringUntil('\n');
    setCores(modo);
    FastLED.show();
    previousMillis = currentMillis;
  }
  // if(currentMillis - previousMillis >= interval) {
  //   previousMillis = currentMillis;
  //   if(FastLED.getBrightness()) {
  //     FastLED.setBrightness(0);
  //   } else {
  //     FastLED.setBrightness(255);
  //   }
  //   FastLED.show();
  // }
}
