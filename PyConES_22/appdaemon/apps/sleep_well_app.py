import hassapi as hass
import datetime

def its_summer():
  return 6 <= datetime.datetime.now().month <= 9

class SleepWell(hass.Hass):
  def initialize(self):
    bed_time = self.parse_time(self.args["bed_time"])
    wake_up_time = self.parse_time(self.args["wake_up_time"])
    self.run_daily(self.on_going_to_bed_cb, bed_time)
    self.run_daily(self.on_waking_up_cb, wake_up_time)

  def on_going_to_bed_cb(self, kwargs):
    if its_summer():
      self.turn_on(self.args["switch"])

  def on_waking_up_cb(self, kwargs):
    if its_summer():
      self.turn_off(self.args["switch"])

