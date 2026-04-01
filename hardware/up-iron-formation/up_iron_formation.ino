/*
 * UP Iron Formation Energy Storage - Test Model Control System
 *
 * Controls and monitors a proof-of-concept energy storage model
 * based on Upper Peninsula iron formations, implementing feedback
 * loops between iron-air batteries, compressed air, gravity storage,
 * and pumped hydro.
 *
 * Hardware:
 *   - ESP32 or Arduino with WiFi
 *   - DS18B20 temperature sensor (iron bed)
 *   - Analog pressure sensor (0-50 PSI)
 *   - HX711 load cell (gravity counterweight)
 *   - Analog water level sensor
 *   - 2x servo (gravity release, valve control)
 *   - Air pump, water pump, heater (relay-driven)
 *
 * Energy Storage Systems (scale model):
 *   1. Iron-Air Battery: iron oxidation/reduction with thermal feedback
 *   2. Compressed Air (CAES): mine shaft pressure storage
 *   3. Gravity Storage: counterweight in shaft (50 lbs, 6 ft)
 *   4. Pumped Hydro: water level differential
 *
 * Feedback Loops:
 *   - Thermal: waste heat from iron oxidation assists air compression
 *   - Mechanical: gravity system creates vacuum for compression assist
 *   - Hydraulic: compressed air drives water pumps
 *   - Chemical: iron oxidation temperature optimized by solar/wind input
 *
 * Web Interface:
 *   Creates WiFi AP "UP_Iron_Battery_Test" with real-time dashboard
 *   showing all sensor readings, energy storage levels, and controls.
 *
 * Version: 1.0
 * Date: June 2025
 */

#include <Arduino.h>
#include <WiFi.h>
#include <WebServer.h>
#include <ArduinoJson.h>
#include <OneWire.h>
#include <DallasTemperature.h>
#include <HX711.h>
#include <Servo.h>

// ==================== PIN DEFINITIONS ====================

#define TEMP_SENSOR_PIN     2
#define PRESSURE_SENSOR_PIN A0
#define LOAD_CELL_DOUT_PIN  3
#define LOAD_CELL_SCK_PIN   4
#define WATER_LEVEL_PIN     A1
#define SERVO_GRAVITY_PIN   9
#define SERVO_VALVE_PIN     10
#define AIR_PUMP_PIN        5
#define WATER_PUMP_PIN      6
#define HEATER_PIN          7
#define LED_STATUS_PIN      13

// ==================== SYSTEM CONSTANTS ====================

#define TEMP_PRECISION       12
#define SAMPLING_RATE        100    // ms between sensor reads
#define FEEDBACK_LOOP_DELAY  500    // ms between feedback updates
#define LOG_INTERVAL         5000   // ms between serial log lines

#define MAX_PRESSURE         50.0   // PSI
#define MAX_TEMPERATURE      80.0   // Celsius safety limit
#define GRAVITY_MASS_KG      22.7   // 50 lbs counterweight
#define MINE_SHAFT_HEIGHT_M  1.83   // 6 ft scale model shaft

// ==================== NETWORK ====================

const char* ssid     = "UP_Iron_Battery_Test";
const char* password = "IronFormation2025";

// ==================== HARDWARE OBJECTS ====================

OneWire oneWire(TEMP_SENSOR_PIN);
DallasTemperature tempSensors(&oneWire);
HX711 loadCell;
Servo gravityServo;
Servo valveServo;
WebServer server(80);

// ==================== DATA STRUCTURES ====================

struct SystemState {
    float temperature;
    float pressure;
    float waterLevel;
    float gravityPosition;
    float ironOxidationRate;
    float energyStored[4];     // [iron-air, CAES, gravity, hydro]
    float efficiencyRating;
    float feedbackMultiplier;
    unsigned long timestamp;
};

struct EnergyFlow {
    float solarInput;
    float windInput;
    float thermalRecovery;
    float mechanicalAdvantage;
    float totalOutput;
    float roundTripEfficiency;
};

SystemState currentState;
EnergyFlow energyMetrics;

// Calibration offsets (set during startup)
float pressureCalibration  = 0.0;
float loadCellCalibration  = 0.0;
float temperatureOffset    = 0.0;

// ==================== FORWARD DECLARATIONS ====================

void calibrateSensors();
void setupWiFi();
void setupWebServer();
void resetSystemState();
void updateSensorReadings();
void calculateEnergyFlows();
void executeFeedbackLoop();
void controlActuators();
void logSystemData();

void calculateIronAirStorage();
void calculateCAESStorage();
void calculateGravityStorage();
void calculateHydroStorage();

void handleRoot();
void handleData();
void handleStatus();
void handleControl();
void handleCalibration();

// ==================== INITIALIZATION ====================

void setup() {
    Serial.begin(115200);
    Serial.println(F("UP Iron Formation Energy Storage - Test Model"));
    Serial.println(F("Initializing systems..."));

    // Output pins
    pinMode(AIR_PUMP_PIN, OUTPUT);
    pinMode(WATER_PUMP_PIN, OUTPUT);
    pinMode(HEATER_PIN, OUTPUT);
    pinMode(LED_STATUS_PIN, OUTPUT);

    // Sensors
    tempSensors.begin();
    tempSensors.setResolution(TEMP_PRECISION);
    loadCell.begin(LOAD_CELL_DOUT_PIN, LOAD_CELL_SCK_PIN);

    // Servos
    gravityServo.attach(SERVO_GRAVITY_PIN);
    valveServo.attach(SERVO_VALVE_PIN);

    // Calibrate at ambient conditions
    calibrateSensors();

    // Network
    setupWiFi();
    setupWebServer();

    // Initial state
    resetSystemState();

    Serial.println(F("System initialized successfully"));
    digitalWrite(LED_STATUS_PIN, HIGH);
}

// ==================== MAIN LOOP ====================

void loop() {
    updateSensorReadings();
    calculateEnergyFlows();
    executeFeedbackLoop();
    controlActuators();
    server.handleClient();
    logSystemData();
    delay(SAMPLING_RATE);
}

// ==================== SENSOR FUNCTIONS ====================

void updateSensorReadings() {
    // Temperature (DS18B20)
    tempSensors.requestTemperatures();
    currentState.temperature = tempSensors.getTempCByIndex(0) + temperatureOffset;

    // Pressure (analog 0-50 PSI)
    int pressureRaw = analogRead(PRESSURE_SENSOR_PIN);
    currentState.pressure = (pressureRaw / 1023.0) * MAX_PRESSURE + pressureCalibration;

    // Water level (analog, 0-100%)
    int waterRaw = analogRead(WATER_LEVEL_PIN);
    currentState.waterLevel = (waterRaw / 1023.0) * 100.0;

    // Gravity position (load cell -> height)
    if (loadCell.is_ready()) {
        float weight = loadCell.get_units(5);
        float weightDiff = GRAVITY_MASS_KG - weight;
        float heightFrac = weightDiff / GRAVITY_MASS_KG;
        currentState.gravityPosition = heightFrac * MINE_SHAFT_HEIGHT_M;
    }

    currentState.timestamp = millis();
}

// ==================== ENERGY CALCULATIONS ====================

void calculateEnergyFlows() {
    // Simulated renewable inputs (replace with actual sensors in field)
    energyMetrics.solarInput = 5.0 + (sin(millis() / 10000.0) * 2.0);
    energyMetrics.windInput  = 8.0 + (cos(millis() / 15000.0) * 3.0);

    // Thermal recovery from iron oxidation
    float ironTemp = currentState.temperature;
    if (ironTemp > 25.0) {
        energyMetrics.thermalRecovery = (ironTemp - 25.0) * 0.1;
        currentState.ironOxidationRate = energyMetrics.thermalRecovery * 2.0;
    } else {
        energyMetrics.thermalRecovery = 0.0;
        currentState.ironOxidationRate = 0.0;
    }

    // Gravity potential: E = mgh
    float gravityPotential = GRAVITY_MASS_KG * 9.81 * currentState.gravityPosition;
    energyMetrics.mechanicalAdvantage = gravityPotential * 0.85;

    // Per-subsystem storage
    calculateIronAirStorage();
    calculateCAESStorage();
    calculateGravityStorage();
    calculateHydroStorage();

    // Feedback multiplier: coupling bonus from waste-heat + mechanical assist
    currentState.feedbackMultiplier = 1.0
        + (energyMetrics.thermalRecovery * 0.05)
        + (energyMetrics.mechanicalAdvantage * 0.03);

    // Total output with feedback coupling
    float totalInput = energyMetrics.solarInput + energyMetrics.windInput;
    energyMetrics.totalOutput = totalInput * currentState.feedbackMultiplier;
    energyMetrics.roundTripEfficiency = (energyMetrics.totalOutput / totalInput) * 100.0;
}

void calculateIronAirStorage() {
    float baseCapacity = 10.0;  // MWh equivalent at scale
    float tempFactor = constrain(
        map(currentState.temperature * 100, 2000, 6000, 80, 120) / 100.0,
        0.8, 1.2
    );
    currentState.energyStored[0] = baseCapacity * tempFactor
        * (currentState.ironOxidationRate / 10.0);
}

void calculateCAESStorage() {
    float maxCapacity = 8.0;
    currentState.energyStored[1] = maxCapacity * (currentState.pressure / MAX_PRESSURE);
}

void calculateGravityStorage() {
    float maxCapacity = 6.0;
    currentState.energyStored[2] = maxCapacity
        * (currentState.gravityPosition / MINE_SHAFT_HEIGHT_M);
}

void calculateHydroStorage() {
    float maxCapacity = 5.0;
    currentState.energyStored[3] = maxCapacity * (currentState.waterLevel / 100.0);
}

// ==================== FEEDBACK LOOP CONTROL ====================

void executeFeedbackLoop() {
    static unsigned long lastFeedback = 0;
    if (millis() - lastFeedback < FEEDBACK_LOOP_DELAY) return;
    lastFeedback = millis();

    // Thermal -> Pneumatic: waste heat assists air compression
    if (currentState.temperature > 30.0 && currentState.pressure < MAX_PRESSURE * 0.8) {
        digitalWrite(AIR_PUMP_PIN, HIGH);
        delay(100);
        digitalWrite(AIR_PUMP_PIN, LOW);
    }

    // Gravity -> Vacuum: falling weight creates low-pressure assist
    if (currentState.gravityPosition > MINE_SHAFT_HEIGHT_M * 0.5) {
        gravityServo.write(
            map(currentState.gravityPosition * 100, 0,
                (int)(MINE_SHAFT_HEIGHT_M * 100), 0, 180)
        );
    }

    // Pneumatic -> Hydraulic: compressed air drives water pump
    if (currentState.pressure > MAX_PRESSURE * 0.6 && currentState.waterLevel < 80.0) {
        digitalWrite(WATER_PUMP_PIN, HIGH);
        delay(200);
        digitalWrite(WATER_PUMP_PIN, LOW);
    }

    // Temperature control: optimize iron oxidation window (35-55 C)
    if (currentState.temperature < 35.0 && energyMetrics.solarInput > 6.0) {
        digitalWrite(HEATER_PIN, HIGH);
    } else if (currentState.temperature > 55.0) {
        digitalWrite(HEATER_PIN, LOW);
    }
}

// ==================== ACTUATOR CONTROL ====================

void controlActuators() {
    // Valve position proportional to water level
    valveServo.write(map(currentState.waterLevel, 0, 100, 0, 180));

    // Status LED: blink rate indicates coupling efficiency
    if (currentState.feedbackMultiplier > 1.10) {
        digitalWrite(LED_STATUS_PIN, (millis() % 200) < 100);   // fast
    } else if (currentState.feedbackMultiplier > 1.05) {
        digitalWrite(LED_STATUS_PIN, (millis() % 1000) < 500);  // slow
    } else {
        digitalWrite(LED_STATUS_PIN, HIGH);                      // solid
    }
}

// ==================== CALIBRATION ====================

void calibrateSensors() {
    Serial.println(F("Calibrating sensors..."));

    // Pressure: zero at atmospheric
    long pressureSum = 0;
    for (int i = 0; i < 100; i++) {
        pressureSum += analogRead(PRESSURE_SENSOR_PIN);
        delay(10);
    }
    pressureCalibration = -(pressureSum / 100.0 / 1023.0 * MAX_PRESSURE);

    // Load cell: tare at no-load
    if (loadCell.is_ready()) {
        loadCell.set_scale();
        loadCell.tare();
    }

    // Temperature: offset to known ambient
    tempSensors.requestTemperatures();
    float ambient = tempSensors.getTempCByIndex(0);
    temperatureOffset = 22.0 - ambient;  // assume 22 C room temp

    Serial.println(F("Calibration complete"));
}

// ==================== WIFI & WEB SERVER ====================

void setupWiFi() {
    WiFi.softAP(ssid, password);
    Serial.print(F("AP IP: "));
    Serial.println(WiFi.softAPIP());
}

void setupWebServer() {
    server.on("/",              HTTP_GET,  handleRoot);
    server.on("/api/status",    HTTP_GET,  handleStatus);
    server.on("/api/data",      HTTP_GET,  handleData);
    server.on("/api/control",   HTTP_POST, handleControl);
    server.on("/api/calibrate", HTTP_POST, handleCalibration);
    server.begin();
    Serial.println(F("Web server started"));
}

void handleRoot() {
    String html = F(
        "<!DOCTYPE html><html><head>"
        "<title>UP Iron Formation Energy Storage</title>"
        "<meta charset='UTF-8'>"
        "<meta name='viewport' content='width=device-width,initial-scale=1'>"
        "<style>"
        "body{font-family:sans-serif;margin:20px;background:#1a1a2e;color:#fff}"
        ".hdr{text-align:center;margin-bottom:30px}"
        ".grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:20px}"
        ".card{background:rgba(255,255,255,.1);padding:20px;border-radius:10px}"
        ".row{display:flex;justify-content:space-between;margin:8px 0}"
        ".val{font-weight:bold;color:#ff6b6b}"
        ".btn{background:#4ecdc4;color:#000;border:none;padding:10px 20px;"
        "border-radius:5px;cursor:pointer;margin:5px}"
        ".btn:hover{background:#ff6b6b}"
        "#st{font-size:20px;text-align:center;margin:15px 0}"
        ".hi{color:#4ecdc4}.md{color:#ffd93d}.lo{color:#ff6b6b}"
        "</style></head><body>"
        "<div class='hdr'>"
        "<h1>UP Iron Formation Energy Storage</h1>"
        "<div id='st'>Initializing...</div></div>"
        "<div class='grid'>"
        "<div class='card'><h3>Sensors</h3>"
        "<div class='row'>Temperature <span class='val' id='t'>--</span></div>"
        "<div class='row'>Pressure <span class='val' id='p'>--</span></div>"
        "<div class='row'>Water Level <span class='val' id='w'>--</span></div>"
        "<div class='row'>Gravity Pos <span class='val' id='g'>--</span></div></div>"
        "<div class='card'><h3>Energy Storage</h3>"
        "<div class='row'>Iron-Air <span class='val' id='e0'>--</span></div>"
        "<div class='row'>CAES <span class='val' id='e1'>--</span></div>"
        "<div class='row'>Gravity <span class='val' id='e2'>--</span></div>"
        "<div class='row'>Hydro <span class='val' id='e3'>--</span></div></div>"
        "<div class='card'><h3>Performance</h3>"
        "<div class='row'>Feedback <span class='val' id='fb'>--</span></div>"
        "<div class='row'>Efficiency <span class='val' id='ef'>--</span></div>"
        "<div class='row'>Thermal Rec <span class='val' id='tr'>--</span></div>"
        "<div class='row'>Total Out <span class='val' id='to'>--</span></div></div>"
        "<div class='card'><h3>Control</h3>"
        "<button class='btn' onclick='cmd(\"start\")'>Start</button>"
        "<button class='btn' onclick='cmd(\"stop\")'>Stop</button>"
        "<button class='btn' onclick='cmd(\"reset\")'>Reset</button>"
        "<button class='btn' onclick='cmd(\"calibrate\")'>Calibrate</button>"
        "<button class='btn' onclick='cmd(\"optimize\")'>Optimize</button>"
        "</div></div>"
        "<script>"
        "function upd(){fetch('/api/data').then(r=>r.json()).then(d=>{"
        "document.getElementById('t').textContent=d.temperature.toFixed(1)+'C';"
        "document.getElementById('p').textContent=d.pressure.toFixed(1)+' PSI';"
        "document.getElementById('w').textContent=d.waterLevel.toFixed(1)+'%';"
        "document.getElementById('g').textContent=d.gravityPosition.toFixed(2)+' m';"
        "for(var i=0;i<4;i++)document.getElementById('e'+i).textContent=d.energyStored[i].toFixed(1)+' MWh';"
        "document.getElementById('fb').textContent=d.feedbackMultiplier.toFixed(2)+'x';"
        "document.getElementById('ef').textContent=d.roundTripEfficiency.toFixed(1)+'%';"
        "document.getElementById('tr').textContent=d.thermalRecovery.toFixed(1)+' MW';"
        "document.getElementById('to').textContent=d.totalOutput.toFixed(1)+' MW';"
        "var s=document.getElementById('st'),e=d.roundTripEfficiency;"
        "if(e>105){s.textContent='FEEDBACK LOOPS ACTIVE';s.className='hi'}"
        "else if(e>85){s.textContent='OPERATING NORMALLY';s.className='md'}"
        "else{s.textContent='NEEDS OPTIMIZATION';s.className='lo'}"
        "}).catch(e=>console.error(e))}"
        "function cmd(c){fetch('/api/control',{method:'POST',"
        "headers:{'Content-Type':'application/json'},"
        "body:JSON.stringify({command:c})}).then(()=>upd())}"
        "setInterval(upd,2000);upd();"
        "</script></body></html>"
    );
    server.send(200, "text/html", html);
}

void handleData() {
    StaticJsonDocument<1024> doc;
    doc["temperature"]       = currentState.temperature;
    doc["pressure"]          = currentState.pressure;
    doc["waterLevel"]        = currentState.waterLevel;
    doc["gravityPosition"]   = currentState.gravityPosition;
    doc["feedbackMultiplier"] = currentState.feedbackMultiplier;
    doc["roundTripEfficiency"] = energyMetrics.roundTripEfficiency;
    doc["thermalRecovery"]   = energyMetrics.thermalRecovery;
    doc["totalOutput"]       = energyMetrics.totalOutput;
    doc["timestamp"]         = currentState.timestamp;

    JsonArray arr = doc.createNestedArray("energyStored");
    for (int i = 0; i < 4; i++) arr.add(currentState.energyStored[i]);

    String resp;
    serializeJson(doc, resp);
    server.send(200, "application/json", resp);
}

void handleStatus() {
    StaticJsonDocument<256> doc;
    doc["status"]  = "operational";
    doc["uptime"]  = millis();
    doc["version"] = "1.0";
    String resp;
    serializeJson(doc, resp);
    server.send(200, "application/json", resp);
}

void handleControl() {
    if (!server.hasArg("plain")) {
        server.send(400, "application/json", "{\"error\":\"no command\"}");
        return;
    }

    StaticJsonDocument<256> doc;
    deserializeJson(doc, server.arg("plain"));
    String command = doc["command"];

    if (command == "start") {
        Serial.println(F("Starting test sequence"));
    } else if (command == "stop") {
        digitalWrite(AIR_PUMP_PIN, LOW);
        digitalWrite(WATER_PUMP_PIN, LOW);
        digitalWrite(HEATER_PIN, LOW);
        Serial.println(F("All systems stopped"));
    } else if (command == "reset") {
        resetSystemState();
    } else if (command == "calibrate") {
        calibrateSensors();
    } else if (command == "optimize") {
        executeFeedbackLoop();
    }

    server.send(200, "application/json", "{\"status\":\"ok\"}");
}

void handleCalibration() {
    calibrateSensors();
    server.send(200, "application/json", "{\"status\":\"calibrated\"}");
}

// ==================== DATA LOGGING ====================

void logSystemData() {
    static unsigned long lastLog = 0;
    if (millis() - lastLog < LOG_INTERVAL) return;
    lastLog = millis();

    // CSV format: timestamp,temp,pressure,water,gravity,feedback,efficiency
    Serial.print(F("LOG: "));
    Serial.print(currentState.timestamp);
    Serial.print(','); Serial.print(currentState.temperature, 1);
    Serial.print(','); Serial.print(currentState.pressure, 1);
    Serial.print(','); Serial.print(currentState.waterLevel, 1);
    Serial.print(','); Serial.print(currentState.gravityPosition, 2);
    Serial.print(','); Serial.print(currentState.feedbackMultiplier, 3);
    Serial.print(','); Serial.println(energyMetrics.roundTripEfficiency, 1);
}

// ==================== UTILITY ====================

void resetSystemState() {
    currentState.temperature       = 22.0;
    currentState.pressure          = 0.0;
    currentState.waterLevel        = 0.0;
    currentState.gravityPosition   = 0.0;
    currentState.ironOxidationRate = 0.0;
    currentState.efficiencyRating  = 85.0;
    currentState.feedbackMultiplier = 1.0;

    for (int i = 0; i < 4; i++) currentState.energyStored[i] = 0.0;

    energyMetrics.solarInput          = 0.0;
    energyMetrics.windInput           = 0.0;
    energyMetrics.thermalRecovery     = 0.0;
    energyMetrics.mechanicalAdvantage = 0.0;
    energyMetrics.totalOutput         = 0.0;
    energyMetrics.roundTripEfficiency = 85.0;

    Serial.println(F("System state reset"));
}
