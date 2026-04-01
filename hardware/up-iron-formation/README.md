# UP Iron Formation Energy Storage - Test Model

Arduino/ESP32 firmware for a proof-of-concept energy storage system
based on Upper Peninsula iron formations.  Controls and monitors four
coupled energy storage subsystems through a single microcontroller
with a built-in web dashboard.

## What It Does

A scale model (6 ft mine shaft, 50 lb counterweight) demonstrating
how abandoned iron mines can become multi-modal energy storage:

| Subsystem | How it stores energy | Scale model |
|-----------|---------------------|-------------|
| **Iron-Air Battery** | Iron oxidation/reduction (exothermic) | Iron bed with temperature sensor |
| **Compressed Air (CAES)** | Air pressurized in sealed mine chambers | Air pump + pressure sensor |
| **Gravity Storage** | Weight raised/lowered in mine shaft | 50 lb counterweight + load cell |
| **Pumped Hydro** | Water pumped to higher elevation | Water pump + level sensor |

## Feedback Loops

The key insight: these four systems **couple** to each other.

```
Iron oxidation heat --> assists air compression (thermal)
Gravity descent     --> creates vacuum for compression (mechanical)
Compressed air      --> drives water pump (pneumatic-hydraulic)
Solar/wind surplus  --> heats iron bed to optimal range (chemical)
```

The firmware implements these as real-time feedback loops.  The
`feedbackMultiplier` metric shows the coupling bonus -- typically
1.05-1.15x, meaning 5-15% more output than the sum of parts.

## Hardware

- **Controller:** ESP32 or Arduino Mega with WiFi
- **Sensors:** DS18B20 (temp), analog pressure (0-50 PSI), HX711 load cell, analog water level
- **Actuators:** 2x servo (gravity release, valve), air pump, water pump, heater (all relay-driven)
- **Status:** LED blink rate indicates coupling efficiency

## Wiring

```
ESP32/Arduino Pin    Component
─────────────────    ─────────
D2                   DS18B20 temperature (OneWire)
A0                   Pressure sensor (0-50 PSI)
D3                   HX711 DOUT (load cell)
D4                   HX711 SCK
A1                   Water level sensor
D5                   Air pump relay
D6                   Water pump relay
D7                   Heater relay
D9                   Servo - gravity release
D10                  Servo - valve control
D13                  Status LED
```

## Web Dashboard

The firmware creates a WiFi access point (`UP_Iron_Battery_Test`)
and serves a real-time dashboard at `192.168.4.1` showing:

- All sensor readings (temp, pressure, water level, gravity position)
- Energy stored in each subsystem (MWh equivalent at scale)
- Feedback multiplier and round-trip efficiency
- Start/stop/reset/calibrate/optimize controls

## Upload

Using Arduino IDE or PlatformIO:

```bash
# Arduino IDE: install these libraries via Library Manager
#   - ArduinoJson
#   - OneWire
#   - DallasTemperature
#   - HX711

# PlatformIO
pio run --target upload
```

## Serial Log Format

CSV over serial at 115200 baud, every 5 seconds:

```
LOG: timestamp,temperature,pressure,waterLevel,gravityPosition,feedbackMultiplier,efficiency
LOG: 15000,35.2,12.4,45.0,1.22,1.087,108.7
```

## How It Connects

This hardware test rig validates the physics modeled in the Python
simulation modules:

- `resilience/recovery/bio_step_system.py` -- models the same
  iron oxidation + water + energy coupling in software
- `resilience/recovery/geometric_alumina.py` -- models iron/metal
  processing pathways
- `resilience/recovery/sovereign_operations.py` -- models the power
  balancing and monitoring logic

Build the Python simulation first to predict behavior, then validate
with this physical test rig.

## Geology Required

The full-scale system requires:
- Abandoned iron mine shafts (UP Michigan, Minnesota Iron Range, etc.)
- Banded Iron Formation (BIF) geology for the iron-air chemistry
- Sufficient depth for gravity storage (deeper = more energy)
- Sealed chambers for compressed air storage
- Water source for pumped hydro component

The scale model proves the coupling principles work before
committing to a full mine installation.
