# homeSwiftPackets
Locally running UDP service that helps control various smart home accessories.\
Designed to be paired with [ESPHome](https://github.com/ESPHome/ESPHome)'s [udp.write](https://esphome.io/components/udp/#udpwrite-action). Replaces my original [tasmota-tuya-mqtt-bridge](https://github.com/QuanTrieuPCYT/tasmota-tuya-mqtt-bridge) application.

## Types of devices controlled
This application controls various devices in my smart home. Those include:

- Xiaomi devices via [Miot Spec](https://home.miot-spec.com) (Desk Lamp).
- [ESPHome](https://esphome.io) devices (Lighting).
- Special entities exposed via [Home Assistant](https://www.home-assistant.io) (AC and Fan).
- ~~Tuya devices via their Local API, usable with [tinytuya](https://github.com/jasonacox/tinytuya).~~ (I tuya-converted all of my controllable Tuya devices so this is no longer needed).