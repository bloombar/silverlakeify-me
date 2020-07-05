#!/usr/bin/env python3
"""
Operate a Silver Lake Reservation Bot.
"""

import schedule
import time
from person import Person
from reservation_bot import ReservationBot

def main():
  # indicate day/time preferences.
  # - Enter preferred time for each day, if any
  # - Enter '-' to exclude a given day
  # - Comment out a day entirely to reserve any time on that day
  preferences = {
    # 'Monday': '11:30AM', # book only this time
    # 'Tuesday': '3:30PM', # book ony this time
    # 'Wednesday': '-', # do not book
    # book anytime Thursday, since a preference is not indicated here
    # 'Friday': '-', # do not book
    # 'Saturday': '-', # do not book
    # 'Sunday': '-', # do not book
  }

  # appointment_type = 'Senior Swim' # or '11:30 and 3:30 Sessions'
  # person = Person('Morris', 'Chang', '9148179962', 'chang_m@mailinator.com', preferences)

  appointment_type = '11:30 and 3:30 Sessions' # or 'Senior Swim'
  person = Person('Katya', 'Bloomberg', '9148179962', 'katya@plasticpast.com', preferences)
  # bot = ReservationBot(person, appointment_type=appointment_type, hidden=False)
  schedule.every(1).minutes.do(ReservationBot, person=person, appointment_type=appointment_type, hidden=True)

  # flush out pending jobs
  while True:
    schedule.run_pending()
    time.sleep(15)

# run the main function
if __name__ == '__main__':
  main()
