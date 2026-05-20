import socket
import functions
from functions import conf

udp_ip = conf("Server", "Address")
udp_port = int(conf("Server", "Port"))

enable_whitelist_str = conf("Server", "EnableWhitelist")
enable_whitelist = str(enable_whitelist_str).lower() in ['true', '1', 't', 'y', 'yes']

raw_whitelist = conf("Server", "Whitelist")
allowed_ips = [ip.strip() for ip in str(raw_whitelist).split(",")] if raw_whitelist else []

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((udp_ip, udp_port))

print(f"----------\nListening for UDP packets on port {udp_port}...\n----------")
if enable_whitelist: print("IP Whitelisting is enabled!")

try:
    while True:
        data, addr = sock.recvfrom(1024)
        sender_ip = addr[0]

        if enable_whitelist and sender_ip not in allowed_ips:
            print(f"Blocked unauthorized request from IP: {sender_ip}")
            continue

        payload = data.decode("utf-8").strip()

        if payload == "led":
            output = functions.esphome_toggle(conf("Devices", "ip_led"), conf("Devices", "key_led"), conf("Devices", "devname_led"))
        elif payload == "rgb":
            output = functions.esphome_toggle(conf("Devices", "ip_rgb"), conf("Devices", "key_rgb"), conf("Devices", "devname_rgb"))
        elif payload == "desk":
            output = functions.esphome_toggle(conf("Devices", "ip_desk"), conf("Devices", "key_desk"), conf("Devices", "devname_desk"))
        elif payload == "decorate":
            output = functions.esphome_toggle(conf("Devices", "ip_decorate"), conf("Devices", "key_decorate"), conf("Devices", "devname_decorate"))
        elif payload == "bulbs":
            output = functions.hass_toggle(conf("Devices", "hassid_bulbs"))
        elif payload == "alllights":
            output = functions.hass_toggle(conf("Devices", "hassid_lights"))
        elif payload == "climate":
            output = functions.hass_climate_toggle(conf("Devices", "hassid_climate"))
        elif payload == "fan":
            output = functions.hass_fan_toggle(conf("Devices", "hassid_fan"))
        elif payload == "wol":
            output = functions.wol(conf("Devices", "wol_mac"), conf("Devices", "wol_broadcast"), int(conf("Devices", "wol_port")) if conf("Devices", "wol_port") else None)
        else:
            output = "You requested an invalid device."

        print(f"Received request '{payload}' from {sender_ip}")
        print(f"Output:\n{output}\n")

except KeyboardInterrupt:
    print("\nShutting down UDP listener...")
finally:
    sock.close()