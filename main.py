import socket
import functions
from functions import conf

udp_ip = conf("Server", "Address")  # Assuming the Home Assistant server is on the same machine
udp_port = int(conf("Server", "Port"))

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((udp_ip, udp_port))

print(f"----------\nListening for UDP packets on port {udp_port}...\n----------")

try:
    while True:
        data, addr = sock.recvfrom(1024)
        payload = data.decode("utf-8").strip()
        if payload == "rgb":
            output = functions.esphome_toggle(conf("Devices", "ip_rgb"), conf("Devices", "key_rgb"), conf("Devices", "devname_rgb"))
        elif payload == "desk":
            output = functions.miot_toggle(conf("Devices", "ip_desk"), conf("Devices", "miio_token_desk"))
        elif payload == "decorate":
            output = functions.esphome_toggle(conf("Devices", "ip_decorate"), conf("Devices", "key_decorate"), conf("Devices", "devname_decorate"))
        elif payload == "alllights":
            output = functions.hass_toggle(conf("Devices", "hassid_lights"))
        elif payload == "climate":
            output = functions.hass_climate_toggle(conf("Devices", "hassid_climate"))
        elif payload == "fan":
            output = functions.hass_fan_toggle(conf("Devices", "hassid_fan"))
        else:
            output = "You requested an invalid device."

        print(f"Received request '{payload}' from {addr[0]}")
        print(f"Output:\n{output}\n")

except KeyboardInterrupt:
    print("\nShutting down UDP listener...")
finally:
    sock.close()