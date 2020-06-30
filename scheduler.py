import schedule
import time
from silver_lakeify_me import make_reservation

people = [
  {
    'fname': 'Amos',
    'lname': 'Bloomberg',
    'phone': '6468533493',
    'email': 'resident@plasticpast.com'
  },
  {
    'fname': 'Katya',
    'lname': 'Bloomberg',
    'phone': '8148179062',
    'email': 'katya@plasticpast.com'
  },
]

# schedule every day at 11:30AM
schedule.every().day.at("11:30").do(make_reservation, people)

# flush out pending jobs
while True:
    schedule.run_pending()
    time.sleep(30)
