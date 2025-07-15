import os
import requests
from dotenv import load_dotenv

load_dotenv()

GOVEE_API_KEY = os.getenv("GOVEE_API_KEY")
GOVEE_DEVICE_MAC = os.getenv("GOVEE_DEVICE_MAC")
GOVEE_MODEL = os.getenv("GOVEE_MODEL")

def set_light_color(r, g, b):
    headers = {
        "Govee-API-Key": GOVEE_API_KEY,
        "Content-Type": "application/json"
    }
    payload = {
        "model": GOVEE_MODEL,
        "device": GOVEE_DEVICE_MAC,
        "cmd": {
            "name": "color",
            "value": {
                "r": r,
                "g": g,
                "b": b
            }
        }
    }
    response = requests.put("https://developer-api.govee.com/v1/devices/control", json=payload, headers=headers)

    if response.status_code == 200:
        print("Light color set successfully.")
    else:
        print(f"Failed to set light color: {response.status_code} - {response.text}")

def set_light_on():
    headers = {
        "Govee-API-Key": GOVEE_API_KEY,
        "Content-Type": "application/json"
    }
    payload = {
        "model": GOVEE_MODEL,
        "device": GOVEE_DEVICE_MAC,
        "cmd": {
            "name": "turn",
            "value": "on"
        }
    }
    response = requests.put("https://developer-api.govee.com/v1/devices/control", json=payload, headers=headers)

    if response.status_code == 200:
        print("Light turned on successfully.")
    else:
        print(f"Failed to turn on light: {response.status_code} - {response.text}")
        
def set_light_off():
    headers = {
        "Govee-API-Key": GOVEE_API_KEY,
        "Content-Type": "application/json"
    }
    payload = {
        "model": GOVEE_MODEL,
        "device": GOVEE_DEVICE_MAC,
        "cmd": {
            "name": "turn",
            "value": "off"
        }
    }
    response = requests.put("https://developer-api.govee.com/v1/devices/control", json=payload, headers=headers)

    if response.status_code == 200:
        print("Light turned off successfully.")
    else:
        print(f"Failed to turn off light: {response.status_code} - {response.text}")

def get_device_list():
    headers = {
        "Govee-API-Key": GOVEE_API_KEY,
        "Content-Type": "application/json"
    }
    response = requests.get("https://developer-api.govee.com/v1/devices", headers=headers)
    if response.status_code == 200:
        devices = response.json()
        return devices
    else:
        print(f"Failed to retrieve device list: {response.status_code} - {response.text}")
        return []

def set_light_brightness(level):
    headers = {
        "Govee-API-Key": GOVEE_API_KEY,
        "Content-Type": "application/json"
    }
    payload = {
        "model": GOVEE_MODEL,
        "device": GOVEE_DEVICE_MAC,
        "cmd": {
            "name": "brightness",
            "value": level
        }
    }
    response = requests.put("https://developer-api.govee.com/v1/devices/control", json=payload, headers=headers)

    if response.status_code == 200:
        print(f"Light brightness set to {level} successfully.")
    else:
        print(f"Failed to set light brightness: {response.status_code} - {response.text}")