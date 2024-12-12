from reactive import Reactive, Watch, Computed
from pynput import keyboard
from datetime import datetime, timedelta
import pytz
import time
import threading

class TimeState:
    def __init__(self):
        self.time_zones = ["US/Pacific", "US/Eastern", "Europe/London", "Asia/Shanghai"]
        self.utc_shifts = [-7, -4, 1, 8]
        self.current_zone = Reactive({"value": 0})
        self.utc_time = Reactive({"value": datetime.now(pytz.UTC)})
        
        self.current_zone_name = Computed(lambda: self.time_zones[self.current_zone.value])
        self.current_time = Computed(lambda: 
            self.utc_time.value + timedelta(hours=self.utc_shifts[self.current_zone.value]))
        self.all_times = Computed(lambda: [
            self.utc_time.value + timedelta(hours=shift) 
            for shift in self.utc_shifts
        ])
        self.display_format = Reactive({"value": "12h"})
        self.show_details = Reactive({"value": False})
        self.formatted_time = Computed(lambda: self._format_time())
        self.timezone_details = Computed(lambda: self._get_timezone_details())
    
    def _format_time(self):
        current_time = self.current_time.value
        if self.display_format.value == "12h":
            return current_time.strftime("%I:%M %p")
        return current_time.strftime("%H:%M")
    
    def _get_timezone_details(self):
        current_time = self.current_time.value
        return {
            "date": current_time.strftime("%Y-%m-%d"),
            "week_day": current_time.strftime("%A"),
            "utc_offset": f"UTC{self.utc_shifts[self.current_zone.value]:+d}"
        }
    
    def toggle_format(self):
        self.display_format.value = "24h" if self.display_format.value == "12h" else "12h"
        
    def toggle_details(self):
        self.show_details.value = not self.show_details.value

    def move_left(self):
        self.current_zone.value = (self.current_zone.value - 1) % len(self.time_zones)

    def move_right(self):
        self.current_zone.value = (self.current_zone.value + 1) % len(self.time_zones)

class ClockUI:
    def __init__(self, state: TimeState):
        self.state = state
        
    def render(self):
        self._clear_screen()
        self._render_tabs()
        self._render_time()
        self._render_commands()
    
    def _render_tabs(self):
        for i, zone in enumerate(self.state.time_zones):
            if i == self.state.current_zone.value:
                self._print_highlight(zone)
            else:
                print(zone, end="  ")
        print()
    
    def _render_time(self):
        print(self.state.formatted_time.value)
        
        if self.state.show_details.value:
            details = self.state.timezone_details.value
            print(f"\n{details['date']} {details['week_day']}")
            print(f"Timezone offset: {details['utc_offset']}")

    def _render_commands(self):
        print("\n--- Commands ---")
        print("← →  : Switch timezone")
        print("Space: Toggle 12h/24h format")
        print("Enter: Toggle details")

    def _clear_screen(self):
        print("\033[2J\033[H", end="")

    def _print_highlight(self, text):
        print(f"\033[4;34m{text}\033[0m", end="  ")

def main():
    state = TimeState()
    ui = ClockUI(state)
    
    def on_press(key):
        try:
            if key == keyboard.Key.left:
                state.move_left()
            elif key == keyboard.Key.right:
                state.move_right()
            elif key == keyboard.Key.space:
                state.toggle_format()
            elif key == keyboard.Key.enter:
                state.toggle_details()
        except AttributeError:
            pass

    def update_time():
        while True:
            state.utc_time.value = datetime.now(pytz.UTC)
            time.sleep(60)

    Watch(ui.render)
    keyboard.Listener(on_press=on_press).start()
    threading.Thread(target=update_time, daemon=True).start()

    while True:
        pass

if __name__ == "__main__":
    main()