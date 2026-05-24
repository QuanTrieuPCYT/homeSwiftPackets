import asyncio
import json
import socket

import yaml

import aioesphomeapi
import requests

from miio import FanMiot

with open('config.yaml', 'r') as file:
    config = yaml.safe_load(file)


def conf(bs1: str, bs2: str):
    return str(config.get(bs1, {}).get(bs2, ""))


headers = {'Authorization': 'Bearer ' + conf("HomeAssistant", "Token")}


# ESPHome methods
def esphome_toggle(ip: str, key: str, device_name: str) -> dict[str, str]:
    async def _toggle_task():
        client = aioesphomeapi.APIClient(
            address=ip,
            port=6053,
            password="",
            noise_psk=key
        )

        await client.connect(login=True)

        try:
            entities_services = await client.list_entities_services()
            entities = entities_services[0] if isinstance(entities_services, tuple) else entities_services

            target_light = None
            for entity in entities:
                if isinstance(entity, aioesphomeapi.LightInfo) and (
                        entity.name == device_name or entity.object_id == device_name
                ):
                    target_light = entity
                    break

            if not target_light:
                return {"error": f"Light '{device_name}' not found on {ip}"}

            current_state = None
            state_event = asyncio.Event()

            def state_callback(state):
                nonlocal current_state
                if state.key == target_light.key:
                    current_state = state
                    state_event.set()

            unsubscribe = client.subscribe_states(state_callback)

            try:
                await asyncio.wait_for(state_event.wait(), timeout=3.0)
            except asyncio.TimeoutError:
                return {"error": "Timeout waiting for current device state"}
            finally:
                if callable(unsubscribe):
                    unsubscribe()

            new_state = not current_state.state
            client.light_command(key=target_light.key, state=new_state)

            return {
                "device": target_light.name,
                "state": "on" if new_state else "off"
            }

        finally:
            await client.disconnect()

    return asyncio.run(_toggle_task())


# MIoT methods
def miot_fan_toggle(ip: str, token: str):
    try:
        fan = FanMiot(ip=ip, token=token, model="dmaker.fan.p9") # fallbacks to Xiaomi Smart Tower Fan is fine
        if fan.status().is_on:
            return fan.off()
        else:
            return fan.on()
    except Exception as e:
        return e


# Custom Wake on LAN method
def wol(mac_address: str, broadcast_ip: str, port: int = 9) -> dict[str, str]:
    clean_mac = mac_address.replace(':', '').replace('-', '').replace('.', '')
    if len(clean_mac) != 12: return {"error": f"Invalid MAC address format: {mac_address}"}

    try:
        magic_packet = bytes.fromhex('FF' * 6 + clean_mac * 16)

        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
            sock.sendto(magic_packet, (broadcast_ip, port))

        return {
            "action": "wol",
            "status": "success",
            "mac_address": mac_address,
            "broadcast_ip": broadcast_ip,
            "port": str(port)
        }
    except Exception as e:
        return {"error": str(e)}


# Home Assistant methods
def hass_toggle(entity: str):
    url = f'{conf("HomeAssistant", "BaseURL").rstrip("/")}/api/services/homeassistant/toggle'
    data = {'entity_id': entity }
    requests.post(url, headers=headers, json=data)
    urlstate = f'{conf("HomeAssistant", "BaseURL").rstrip("/")}/api/states/{entity}'
    responsestate = requests.get(urlstate, headers=headers)
    return responsestate.text


def hass_climate_toggle(entity: str):
    payload = json.dumps({"entity_id": f"{entity}", })
    response = requests.get(f'{conf("HomeAssistant", "BaseURL").rstrip("/")}/api/states/{entity}', headers=headers)
    if response.json()["state"] == "off": requests.post(conf("HomeAssistant", "BaseURL").rstrip("/") + "/api/services/climate/turn_on", headers=headers, data=payload)
    else: requests.post(conf("HomeAssistant", "BaseURL").rstrip("/") + "/api/services/climate/turn_off", headers=headers, data=payload)
    return requests.get(f'{conf("HomeAssistant", "BaseURL").rstrip("/")}/api/states/{entity}', headers=headers).text