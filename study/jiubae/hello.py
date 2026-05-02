import logging
from reachy_mini import ReachyMini

# The simulator may not implement media release/acquire endpoints.
# Keep control commands working and silence non-critical media warnings.
logging.getLogger().setLevel(logging.ERROR)
logging.getLogger("reachy_mini").setLevel(logging.ERROR)

mini = ReachyMini(media_backend="no_media", log_level="ERROR")
try:
    print("Connected to Reachy Mini!")
    print(f"현재 상태: {mini.client.get_status()}")
    print("Wiggling antennas...")
    mini.goto_target(antennas=[0.5, -0.5], duration=0.5)
    mini.goto_target(antennas=[-0.5, 0.5], duration=0.5)
    mini.goto_target(antennas=[0, 0], duration=0.5)

    
    print("Done!")
finally:
    mini.client.disconnect()