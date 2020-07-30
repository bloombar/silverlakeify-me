#!/usr/bin/env python3
"""
Operate a Silver Lake Reservation Bot.
"""

import schedule
import time
import random
from person import Person
from reservation_bot import ReservationBot

def try_reservation(people):
  # shuffle the list of people
  random.shuffle(people)
  for person in people:
    bot = ReservationBot(person)

def main():
  # indicate day/time preferences.
  # - Enter preferred time for each day, if any
  # - Enter '-' to exclude a given day
  # - Comment out a day entirely to reserve any time on that day
  
  # person = Person('Morris', 'Chang', '2129987754', 'morris.chang@mailinator.com', ['11:30 and 2:30', '5:30', 'Senior Swim'], {
  # bot = ReservationBot(person, appointment_type=appointment_type, hidden=False)
  # schedule.every(1).minutes.do(ReservationBot, person=person)

  # people for whom to make reservations
  people = [
    Person('Katya', 'Bloomberg', '9148179962', 'katya@plasticpast.com', ['11:30 and 2:30', '5:30'], {
      # all days/times are good  
    }),
    Person('Johil', 'Ross', '3012547340', 'johilross@gmail.com', ['11:30 and 2:30', '5:30'], {
      "Tuesday": '-', # no Tuesdays
      "Thursday": '-' # no Thursdays
    })
  ]

  schedule.every(1).minutes.do(try_reservation, people=people)

  # flush out pending jobs
  while True:
    schedule.run_pending()
    time.sleep(15)

# run the main function
if __name__ == '__main__':
  main()
