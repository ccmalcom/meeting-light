import os
import time
import logging
from datetime import datetime
import requests
from requests.exceptions import RequestException, Timeout, ConnectionError
from dotenv import load_dotenv

# setup logging
app_support_path = os.path.expanduser("~/Library/Application Support/MeetingLight")
os.makedirs(app_support_path, exist_ok=True)
log_path = os.path.join(app_support_path, "meetingLight.log")

#configure logging to both file and console
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(log_path),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Load environment variables
env_path = os.path.join(app_support_path, ".env")
load_dotenv(dotenv_path=env_path)

GOVEE_API_KEY = os.getenv("GOVEE_API_KEY")
GOVEE_DEVICE_MAC = os.getenv("GOVEE_DEVICE_MAC")
GOVEE_MODEL = os.getenv("GOVEE_MODEL")


# API Configuration
GOVEE_API_URL = "https://developer-api.govee.com/v1/devices/control"
REQUEST_TIMEOUT = 10  # seconds
MAX_RETRIES = 3
RETRY_DELAY = 2  # seconds
RATE_LIMIT_DELAY = 0.5  # seconds

#Connection health tracking
last_successful_call = None
consecutive_failures = 0
MAX_CONSECUTIVE_FAILURES = 5

def _make_api_call(payload, operation_name):
    """
    Make a robust API call to Govee with retries and error handling.
    Args:
        payload (dict): The JSON payload to send in the PUT request.
        operation_name (str): A descriptive name for the operation being performed.
    Returns:
        bool: True if the operation was successful, False otherwise.
    """
    global last_successful_call, consecutive_failures
    headers = {
        "Govee-API-Key": GOVEE_API_KEY,
        "Content-Type": "application/json"
    }
    
    for attempt in range(MAX_RETRIES):
        try:
            logger.debug(f"Attempting {operation_name} (attempt {attempt + 1}/{MAX_RETRIES})")
            
            response = requests.put(
                GOVEE_API_URL,
                json=payload,
                headers=headers,
                timeout=REQUEST_TIMEOUT
            )
            
            if response.status_code == 200:
                logger.info(f"{operation_name} - SUCCESS")
                last_successful_call = datetime.now()
                consecutive_failures = 0
                
                # Rate limiting - small delay between successful calls
                time.sleep(RATE_LIMIT_DELAY)
                return True
            
            elif response.status_code == 429:  # Rate limited
                logger.warning(f"{operation_name} - Rate limited, waiting before retry...")
                time.sleep(5)  # Wait longer for rate limit
                continue
            
            else:
                logger.error(f"{operation_name} - FAILED: HTTP {response.status_code} - {response.text}")
                # Don't retry on client errors (4xx) except rate limit
                if 400 <= response.status_code < 500 and response.status_code != 429:
                    consecutive_failures += 1
                    return False
                    
        except Timeout:
            logger.error(f"{operation_name} - TIMEOUT after {REQUEST_TIMEOUT}s (attempt {attempt + 1}/{MAX_RETRIES})")
            
        except ConnectionError as e:
            logger.error(f"{operation_name} - CONNECTION ERROR: {str(e)} (attempt {attempt + 1}/{MAX_RETRIES})")
            
        except RequestException as e:
            logger.error(f"{operation_name} - REQUEST ERROR: {str(e)} (attempt {attempt + 1}/{MAX_RETRIES})")
        
        # Exponential backoff before retry
        if attempt < MAX_RETRIES - 1:
            delay = RETRY_DELAY * (2 ** attempt)
            logger.info(f"Waiting {delay}s before retry...")
            time.sleep(delay)
    
    # All retries failed
    consecutive_failures += 1
    logger.error(f"{operation_name} - FAILED after {MAX_RETRIES} attempts. Consecutive failures: {consecutive_failures}")
    
    # Alert if connection seems persistently broken
    if consecutive_failures >= MAX_CONSECUTIVE_FAILURES:
        logger.critical(f"CONNECTION HEALTH CRITICAL: {consecutive_failures} consecutive failures. Light may be offline or network issues.")
    
    return False

def check_connection_health():
    """
    Check if the connection to Govee API is healthy.
    Returns:
        tuple: (is_healthy: bool, status_message: str)
    """
    global last_successful_call, consecutive_failures
    
    if consecutive_failures >= MAX_CONSECUTIVE_FAILURES:
        return False, f"Connection unhealthy: {consecutive_failures} consecutive failures"
    
    if last_successful_call is None:
        return True, "No calls made yet"
    
    time_since_success = (datetime.now() - last_successful_call).total_seconds()
    
    if time_since_success > 600:  # 10 minutes
        return False, f"No successful call in {int(time_since_success/60)} minutes"
    
    return True, f"Healthy: Last success {int(time_since_success)}s ago"


def reset_connection_health():
    # Manually reset connection health counters. Useful after wake from sleep.
    global consecutive_failures
    consecutive_failures = 0
    logger.info("Connection health counters reset")


def set_light_color(r, g, b):
    """
    Set the light to a specific RGB color.
    
    Args:
        r: Red value (0-255)
        g: Green value (0-255)
        b: Blue value (0-255)
    
    Returns:
        bool: True if successful, False otherwise
    """
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
    return _make_api_call(payload, f"Set color to RGB({r},{g},{b})")


def set_brightness(level):
    """
    Set the brightness level.
    
    Args:
        level: Brightness (0-100)
    
    Returns:
        bool: True if successful, False otherwise
    """
    payload = {
        "model": GOVEE_MODEL,
        "device": GOVEE_DEVICE_MAC,
        "cmd": {
            "name": "brightness",
            "value": level
        }
    }
    return _make_api_call(payload, f"Set brightness to {level}")


def set_color_temperature(temperature):
    """
    Set the color temperature.
    
    Args:
        temperature: Color temperature in Kelvin (2000-9000)
    
    Returns:
        bool: True if successful, False otherwise
    """
    payload = {
        "model": GOVEE_MODEL,
        "device": GOVEE_DEVICE_MAC,
        "cmd": {
            "name": "colorTem",
            "value": temperature
        }
    }
    return _make_api_call(payload, f"Set color temperature to {temperature}K")


def set_light_on():
    """
    Turn the light on.
    
    Returns:
        bool: True if successful, False otherwise
    """
    payload = {
        "model": GOVEE_MODEL,
        "device": GOVEE_DEVICE_MAC,
        "cmd": {
            "name": "turn",
            "value": "on"
        }
    }
    return _make_api_call(payload, "Turn light ON")


def set_light_off():
    """
    Turn the light off.
    
    Returns:
        bool: True if successful, False otherwise
    """
    payload = {
        "model": GOVEE_MODEL,
        "device": GOVEE_DEVICE_MAC,
        "cmd": {
            "name": "turn",
            "value": "off"
        }
    }
    return _make_api_call(payload, "Turn light OFF")


def get_device_list():
    """
    Retrieve the list of Govee devices on the account.
    
    Returns:
        dict: Device list or empty dict on failure
    """
    headers = {
        "Govee-API-Key": GOVEE_API_KEY,
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.get(
            "https://developer-api.govee.com/v1/devices",
            headers=headers,
            timeout=REQUEST_TIMEOUT
        )
        
        if response.status_code == 200:
            logger.info("Device list retrieved successfully")
            return response.json()
        else:
            logger.error(f"Failed to retrieve device list: {response.status_code} - {response.text}")
            return {}
            
    except RequestException as e:
        logger.error(f"Failed to retrieve device list: {str(e)}")
        return {}


def set_light_brightness(level):
    """
    Set the brightness level (duplicate function name in original - keeping for compatibility).
    
    Args:
        level: Brightness (0-100)
    
    Returns:
        bool: True if successful, False otherwise
    """
    return set_brightness(level)


# Health check function that can be called periodically
def perform_health_check():
    """
    Perform a health check by attempting a simple API call.
    
    Returns:
        bool: True if light is responsive, False otherwise
    """
    logger.info("Performing connection health check...")
    
    # Try to get device list as a simple health check
    result = get_device_list()
    
    if result:
        logger.info("Health check PASSED - Connection is healthy")
        reset_connection_health()
        return True
    else:
        logger.warning("Health check FAILED - Connection may be degraded")
        return False