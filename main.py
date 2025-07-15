from govee import set_light_on, set_light_off, get_device_list, set_light_color, set_light_brightness



# try:
#     devices = get_device_list()
#     print("Retrieved devices:")
# except Exception as e:
#     print(f"An error occurred: {e}")

# try:
#     set_light_on()
# except Exception as e:
#     print(f"An error occurred: {e}")

# try:
#     set_light_off()
# except Exception as e:
#     print(f"An error occurred: {e}")
    

# try:
#     set_light_color(255, 0, 0)
# except Exception as e:
#     print(f"An error occurred: {e}")

try:
    set_light_brightness(100)
except Exception as e:
    print(f"An error occurred: {e}")
