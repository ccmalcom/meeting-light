"""
Govee LED light control module with retry logic, state tracking, and health monitoring.

This module provides an interface to control Govee LED lights via their API,
with features including:
- Automatic retry with exponential backoff
- State tracking to avoid redundant API calls
- Connection health monitoring
- Comprehensive error handling and logging
"""

import os
import time
import logging
from typing import Dict, Tuple, Optional
from datetime import datetime
from dotenv import load_dotenv
import requests
from requests.exceptions import RequestException, Timeout, ConnectionError

# Import centralized configuration
from config import (
    APP_SUPPORT_PATH,
    ENV_FILE_PATH,
    LOG_FILE_PATH,
    LOG_FORMAT,
    GOVEE_API_URL,
    GOVEE_API_TIMEOUT,
    GOVEE_MAX_RETRIES,
    GOVEE_RETRY_DELAY,
    GOVEE_RATE_LIMIT_DELAY,
    MAX_CONSECUTIVE_FAILURES,
    HEALTH_CHECK_TIMEOUT
)

# Setup logging
os.makedirs(APP_SUPPORT_PATH, exist_ok=True)

# Note: Logging is configured in main, but we set up this module's logger
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv(dotenv_path=ENV_FILE_PATH)

GOVEE_API_KEY = os.getenv("GOVEE_API_KEY")
GOVEE_DEVICE_MAC = os.getenv("GOVEE_DEVICE_MAC")
GOVEE_MODEL = os.getenv("GOVEE_MODEL")

# Connection health tracking
last_successful_call: Optional[datetime] = None
consecutive_failures: int = 0

# Light state tracking to avoid redundant API calls
_current_state: Dict[str, Optional[any]] = {
    'power': None,              # True=on, False=off, None=unknown
    'color': None,              # (r, g, b) tuple or None
    'brightness': None,         # 0-100 or None
    'color_temperature': None,  # Kelvin value or None
}


def _update_state(key: str, value: any) -> None:
    """
    Update the tracked light state.
    
    Args:
        key: State key to update
        value: New value for the state
    """
    _current_state[key] = value
    logger.debug(f"State updated: {key} = {value}")


def _state_matches(key: str, value: any) -> bool:
    """
    Check if the desired state matches current state.
    
    Args:
        key: State key to check
        value: Value to compare against
    
    Returns:
        True if state matches, False otherwise
    """
    return _current_state[key] == value


def reset_state() -> None:
    """
    Reset all tracked state.
    
    Useful after sleep/wake cycles or when manual light changes occur.
    Forces resync on next command.
    """
    global _current_state
    _current_state = {
        'power': None,
        'color': None,
        'brightness': None,
        'color_temperature': None,
    }
    logger.info("Light state tracking reset")


def _make_api_call(payload: Dict, operation_name: str) -> bool:
    """
    Make an API call to Govee with retry logic and error handling.
    
    Args:
        payload: The JSON payload to send
        operation_name: Description of the operation for logging
    
    Returns:
        True if successful, False otherwise
    """
    global last_successful_call, consecutive_failures
    
    headers = {
        "Govee-API-Key": GOVEE_API_KEY,
        "Content-Type": "application/json"
    }
    
    for attempt in range(GOVEE_MAX_RETRIES):
        try:
            logger.debug(f"Attempting {operation_name} (attempt {attempt + 1}/{GOVEE_MAX_RETRIES})")
            
            response = requests.put(
                GOVEE_API_URL,
                json=payload,
                headers=headers,
                timeout=GOVEE_API_TIMEOUT
            )
            
            if response.status_code == 200:
                logger.info(f"{operation_name} - SUCCESS")
                last_successful_call = datetime.now()
                consecutive_failures = 0
                
                # Rate limiting - small delay between successful calls
                time.sleep(GOVEE_RATE_LIMIT_DELAY)
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
            logger.error(f"{operation_name} - TIMEOUT after {GOVEE_API_TIMEOUT}s (attempt {attempt + 1}/{GOVEE_MAX_RETRIES})")
            
        except ConnectionError as e:
            logger.error(f"{operation_name} - CONNECTION ERROR: {str(e)} (attempt {attempt + 1}/{GOVEE_MAX_RETRIES})")
            
        except RequestException as e:
            logger.error(f"{operation_name} - REQUEST ERROR: {str(e)} (attempt {attempt + 1}/{GOVEE_MAX_RETRIES})")
        
        # Exponential backoff before retry
        if attempt < GOVEE_MAX_RETRIES - 1:
            delay = GOVEE_RETRY_DELAY * (2 ** attempt)
            logger.info(f"Waiting {delay}s before retry...")
            time.sleep(delay)
    
    # All retries failed
    consecutive_failures += 1
    logger.error(f"{operation_name} - FAILED after {GOVEE_MAX_RETRIES} attempts. Consecutive failures: {consecutive_failures}")
    
    # Alert if connection seems persistently broken
    if consecutive_failures >= MAX_CONSECUTIVE_FAILURES:
        logger.critical(f"CONNECTION HEALTH CRITICAL: {consecutive_failures} consecutive failures. Light may be offline or network issues.")
    
    return False


def check_connection_health() -> Tuple[bool, str]:
    """
    Check if the connection to Govee API is healthy.
    
    Returns:
        Tuple of (is_healthy: bool, status_message: str)
    """
    global last_successful_call, consecutive_failures
    
    if consecutive_failures >= MAX_CONSECUTIVE_FAILURES:
        return False, f"Connection unhealthy: {consecutive_failures} consecutive failures"
    
    if last_successful_call is None:
        return True, "No calls made yet"
    
    time_since_success = (datetime.now() - last_successful_call).total_seconds()
    
    if time_since_success > HEALTH_CHECK_TIMEOUT:
        return False, f"No successful call in {int(time_since_success/60)} minutes"
    
    return True, f"Healthy: Last success {int(time_since_success)}s ago"


def reset_connection_health() -> None:
    """
    Manually reset connection health counters.
    
    Useful after wake from sleep or recovering from network issues.
    """
    global consecutive_failures
    consecutive_failures = 0
    logger.info("Connection health counters reset")


def set_light_color(r: int, g: int, b: int) -> bool:
    """
    Set the light to a specific RGB color.
    
    Args:
        r: Red value (0-255)
        g: Green value (0-255)
        b: Blue value (0-255)
    
    Returns:
        True if successful, False otherwise
    """
    # Check if color already matches
    desired_color = (r, g, b)
    if _state_matches('color', desired_color):
        logger.debug(f"Color already set to RGB({r},{g},{b}), skipping API call")
        return True
    
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
    
    success = _make_api_call(payload, f"Set color to RGB({r},{g},{b})")
    if success:
        _update_state('color', desired_color)
        # When setting color, temperature is cleared
        _update_state('color_temperature', None)
    return success


def set_light_brightness(level: int) -> bool:
    """
    Set the brightness level.
    
    Args:
        level: Brightness (0-100)
    
    Returns:
        True if successful, False otherwise
    """
    # Check if brightness already matches
    if _state_matches('brightness', level):
        logger.debug(f"Brightness already set to {level}, skipping API call")
        return True
    
    payload = {
        "model": GOVEE_MODEL,
        "device": GOVEE_DEVICE_MAC,
        "cmd": {
            "name": "brightness",
            "value": level
        }
    }
    
    success = _make_api_call(payload, f"Set brightness to {level}")
    if success:
        _update_state('brightness', level)
    return success


def set_color_temperature(temperature: int) -> bool:
    """
    Set the color temperature.
    
    Args:
        temperature: Color temperature in Kelvin (2000-9000)
    
    Returns:
        True if successful, False otherwise
    """
    # Check if temperature already matches
    if _state_matches('color_temperature', temperature):
        logger.debug(f"Color temperature already set to {temperature}K, skipping API call")
        return True
    
    payload = {
        "model": GOVEE_MODEL,
        "device": GOVEE_DEVICE_MAC,
        "cmd": {
            "name": "colorTem",
            "value": temperature
        }
    }
    
    success = _make_api_call(payload, f"Set color temperature to {temperature}K")
    if success:
        _update_state('color_temperature', temperature)
        # When setting temperature, color is cleared
        _update_state('color', None)
    return success


def set_light_on() -> bool:
    """
    Turn the light on.
    
    Returns:
        True if successful, False otherwise
    """
    # Check if light is already on
    if _state_matches('power', True):
        logger.debug("Light already on, skipping API call")
        return True
    
    payload = {
        "model": GOVEE_MODEL,
        "device": GOVEE_DEVICE_MAC,
        "cmd": {
            "name": "turn",
            "value": "on"
        }
    }
    
    success = _make_api_call(payload, "Turn light ON")
    if success:
        _update_state('power', True)
    return success


def set_light_off() -> bool:
    """
    Turn the light off.
    
    Returns:
        True if successful, False otherwise
    """
    # Check if light is already off
    if _state_matches('power', False):
        logger.debug("Light already off, skipping API call")
        return True
    
    payload = {
        "model": GOVEE_MODEL,
        "device": GOVEE_DEVICE_MAC,
        "cmd": {
            "name": "turn",
            "value": "off"
        }
    }
    
    success = _make_api_call(payload, "Turn light OFF")
    if success:
        _update_state('power', False)
    return success


def get_device_list() -> Dict:
    """
    Retrieve the list of Govee devices on the account.
    
    Returns:
        Device list dictionary or empty dict on failure
    """
    headers = {
        "Govee-API-Key": GOVEE_API_KEY,
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.get(
            "https://developer-api.govee.com/v1/devices",
            headers=headers,
            timeout=GOVEE_API_TIMEOUT
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


def perform_health_check() -> bool:
    """
    Perform a health check by attempting a simple API call.
    
    Returns:
        True if light is responsive, False otherwise
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