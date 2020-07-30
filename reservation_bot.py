#!/usr/bin/env python3
"""
A bot to sign up for Silver Lake during summer 2020.

Selenium webdriver for Chrome (a.k.a. the file named chromedriver) must be installed in either:
- in the same directory as chrome.exe on Windows (e.g. C:\Program Files\Google\Chrome\Application)
- in a directory that is included in the PATH on Mac OS X (e.g. /usr/local/bin)
"""

from person import Person
import datetime
import logging
from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.common.keys import Keys

class ReservationBot():

  def __init__(self, person, max_per_week=3, hidden=True, log=True):
    """
    Instantiate the bot object with settings.
    :param person: The person object for whom to make a reservation.
    :param max_per_week: The maximum number of reservations allowed per week.  Defaults to 3.
    :param hidden: Whether to show the web browser or keep it hidden.
    """
    # start logging
    if log:
      self.start_logging('logs/log.txt')
      self.log('Starting for {} {}'.format(person.first_name, person.last_name))

    # loop through each desired appointment_type
    appointment_types = person.appointment_types # how the site groups appointments e.g. ["11:30 and 2:30", "5:30", "Senior Swim"]. 
    for appointment_type in appointment_types:

      # try to run the bot for this appouintment type
      try:

        # open the web site in google chrome
        self.start_session('https://silverlakereservations.as.me', hidden)

        # get available dates for the desired appointment type
        dates = self.get_available_dates(appointment_type)
        # print('\nall:')
        # [print(d['date'], d['day'], d['times']) for d in dates]

        # filename = 'logs/no-dates-{}.png'.format(datetime.date.today())
        # self.save_screenshot(filename)

        # filter the available dates

        dates = self.filter_by_unreserved(dates, person) # by only those that this person has not yet reserved
        # print('\nunreserved dates:')
        # [print(d['date'], d['day'], d['times']) for d in dates]

        dates = self.filter_by_time_preferences(dates, person) # by only those with times that match the person's preferences
        # print('\npreferred dates:')
        # [print(d['date'], d['day'], d['times']) for d in dates]

        dates = self.limit_per_day(dates) # for any day with multiple times, keep only the first time
        # print('\nlimit 1 per day:')
        # [print(d['date'], d['day'], d['times']) for d in dates]

        dates = self.limit_per_week(dates, person, max_per_week) # limit the number of reservations per week we book
        # print('\nlimit 3 per week:')
        # [print(d['date'], d['day'], d['times']) for d in dates]
        
        # proceed if we have dates to reserve
        if len(dates) > 0:

          # click on the date/times we want to reserve
          self.select_dates(dates)

          # fill in personal details
          self.enter_personal_details(person)

          # submit the form
          self.submit_form()

          # save reservation
          self.save_reservation(dates, person)

          # save screenshot
          clean_dates = '-'.join(['{}-{}'.format(d['date'], '-'.join([t['time'] for t in d['times']])) for d in dates])  # string of dates
          filename = 'logs/{}-{}-{}.png'.format(person.last_name, person.first_name, clean_dates)
          self.save_screenshot(filename)

      except Exception as e:
        # the desired appointment type was not found
        self.log('Error: {}'.format(repr(e)))

      # open the web site in google chrome
      if hasattr(self, 'driver'):
        self.end_session()

    # end for

  def start_session(self, url, hidden=True):
    """
    Load the web site in google chrome by using the webdriver.  
    :param url: The web site to load.
    :param hidden: Whether to show the web browser.
    """
    # open the webdriver
    chrome_options = webdriver.ChromeOptions()  # set some options
    chrome_options.add_argument('--start-maximized') # max height
    if hidden:
      # hide Chrome from user
      chrome_options.add_argument("--headless")
    self.driver = webdriver.Chrome(options=chrome_options)
    self.driver.get(url)

    # pause while page loads reservation content after initial page load
    self.pause(2)

  def end_session(self):
    """
    Close the Chrome webdriver.
    """
    self.driver.close()

  def start_logging(self, filename='log.txt', logger_name='status', level=logging.INFO):
    """
    Enable logging.
    :param filename: The filename of the log file.
    :param logger_name: A label for this logger.
    :param filename: A file in which to save the logs.
    """
    self.is_logging = True

    # logging
    logging.basicConfig(
      level=level,
      # format="%(asctime)s %(levelname)s %(threadName)s %(name)s %(message)s",
      format="%(asctime)s %(message)s",
      datefmt='%Y-%m-%d %H:%M:%S',
      filename=filename,
      filemode='a'
    )
    self.logger = logging.getLogger(logger_name)

  def log(self, msg):
    """
    Logs a message.
    :param msg: The message to log.
    """
    self.logger.info(msg)

  def log_available_dates(self, dates, message):
    """
    Logs a set of available dates in a nicely formatted compact manner.
    :param dates: The dates to log, as a list of dictionaries.
    :param message: Text to output next to the dates.
    """
    # check for no dates
    if len(dates) <= 0:
      self.log('{}: none.'.format(message))
      return

    # loop through each date
    available_dates = []
    for d in dates:
      # get a list of the available times on this date
      times = ','.join([t['time'] for t in d['times']])
      dt = '{} @ {}'.format(d['date'], times) # the date and times
      available_dates.append(dt) # add to list

    log_dates = ','.join(available_dates)
    self.log('{}: {}'.format(message, log_dates))

  def pause(self, seconds):
    """
    Pause for specified number of seconds.
    :param seconds: The number of seconds to pause.
    """
    ActionChains(self.driver).pause(2).perform()

  def select_appointment_type(self, desired_appointment_type):
    """
    Get the element on the page that represents the appointment type we want to book.
    :param desired_appointment_type: The type of interest to us.
    """
    # get a list of all available appointment types
    all_appointment_types = self.driver.find_elements_by_css_selector('#step-pick-appointment > div.pane-content > div.select.select-type > div')
    all_appointment_types = [t for t in all_appointment_types if t.is_displayed()] # limit to those that are visible

    selected_appointment_types = []  # we will select a subset of all types

    # loop through all types
    for atype in all_appointment_types:
      try:
        # grab this appointment type's name, if any
        title = atype.find_element_by_tag_name('label').text
        # check whether it's of the kind we want to select
        if desired_appointment_type in title:
          selected_appointment_types.append(atype) # add the the list
      except:
        # no label found within this appointment type element
        pass

    # make sure we found the target appointment type
    if len(selected_appointment_types) == 0:
      # no appointment type found
      self.log('No "{}" appointment type found.'.format(desired_appointment_type))
      # save screenshot
      filename = 'logs/error-none-found-{}.png'.format(datetime.date.today())
      self.save_screenshot(filename)

      # raise an exception
      raise Exception('No "{}" appointment type found.'.format(desired_appointment_type))

    # loop through the appointment types we've picked
    for atype in selected_appointment_types:
      # grab this appointment type's title, if any
      title = atype.find_element_by_tag_name('label').text
      # logger.info('appointment type: {}'.format(title))

      # click it
      atype.click()

      # pause to allow content to load
      self.pause(2)

  def get_available_dates(self, appointment_type):
    """
    Get a list of all available date/time combinations.
    :param appointment_type: The type of appointment to search dates/times for.
    """

    # first, select the appropriate type of appointment
    self.select_appointment_type(appointment_type)

    # select all dates - each date is in its own fieldset
    available_dates = self.driver.find_elements_by_css_selector('#dates-and-times > fieldset')
    available_dates = [d for d in available_dates if d.is_displayed()] # limit to those that are visible

    # self.log("Found {} available dates.".format(len(available_dates)))

    # loop through each date and append a nicely-formatted version to a list
    dates = []
    for d in available_dates:

      # grab this day, date, and the time elements
      day = d.find_element_by_css_selector('div.day-of-week').text
      date = d.find_element_by_css_selector('div.date-secondary').text
      time_elements = d.find_elements_by_css_selector('div.choose-time div.form-inline label')

      # loop through the available times
      times = []
      for el in time_elements:
        # keep the time and the element to click to book that time
        times.append({
          'time': el.text.lower(),
          'element': el
        })

      # form into a nice package
      date_data = {
        'date': date,
        'day': day,
        'times': times,
        'type': appointment_type,
        'element': d # a reference to the element on the page for this date
      }

      # append to list of dates
      dates.append(date_data)

    # if you got it, log it
    self.log_available_dates(dates, 'Available "{}" dates'.format(appointment_type))

    return dates

  def filter_by_unreserved(self, dates, person, match_times=False):
    """
    Filter out those dates/times that are already booked by this person.
    :param dates: A list of dates to filter.
    :param person: The person for whom to do the filtering.
    :param match_times: Whether to filter out any dates for which existing reservations exist, regardless of times
    :returns: The list of dates with existing reserved dates removed.
    """
    # do nothing further if no dates
    if len(dates) == 0:
      return []

    reservations = self.get_reservations(person)

    good_dates = dates.copy()  # assume they're all good for now
    
    # loop through all dates
    for reservation in reservations:
      # print('==', date['date'], date['times'], '==')
      # loop through all existing reservations
      for date in dates:
        # check whether the date and time are already in our reservations
        date_matches = reservation['date'] == date['date'] # dates match
        time_matches = reservation['time'] in [d['time'] for d in date['times']]  # existing reservation time is present in available times
        # print(reservation['date'], date['date'], date_matches, '|', reservation['time'], [d['time'] for d in date['times']], time_matches)
        if (date_matches and time_matches) or (date_matches and not match_times):
          # we have a reservation that matches
          # self.log('Reservation for {} at {} aready exists... skipping.'.format(reservation['date'], reservation['time']))
          # remove it from the good dates
          good_dates.remove(date)
          break  # quit this loop
        
    # if you got it, log it
    self.log_available_dates(good_dates, 'Filtered by unreserved dates')

    return good_dates

  def filter_by_time_preferences(self, dates, person):
    """
    On any given date, if the preferred time is available, remove other times from the list.
    :param dates: A list of dates to filter.
    :param person: The person for whom to do the filtering.
    :returns: The list of dates with existing reserved dates removed.
    """
    # do nothing further if no dates
    if len(dates) == 0:
      return []

    good_dates = dates.copy()  # assume they're all good for now
    
    # loop through all dates
    for date in dates:
      day = date['day']

      # leave dates for which the user has not expressed preferences
      if day not in person.preferences.keys():
        continue # skip to next day

      # get the person's time preference for this day, as lowercase
      preferred_time = person.preferences[day].lower()
      
      # remove dates for which the preferred time is not available
      if preferred_time not in date['times']:
        # the preferred time is not available
        # self.log('Reservation for {} not available at preferred time {}... skipping.'.format(date['date'], preferred_time))
        good_dates.remove(date) # remove it from the list
        continue

      # find the position of this date in the list of good dates
      pos = good_dates.index(date)

      # replace list of times with only preferred time
      date['times'] = [preferred_time]

      # update the good dates list with this change
      good_dates[pos] = date

    # if you got it, log it
    self.log_available_dates(good_dates, 'Filtered by preferred times')

    return good_dates

  def limit_per_day(self, dates):
    """
    For any dates with more than one available time slot, keep only the first available time slot.
    :param dates: A list of dates.
    :returns: The updated list of dates
    """
    # do nothing further if no dates
    if len(dates) == 0:
      return []

    good_dates = dates.copy()

    # loop through all dates
    for d in good_dates:
      # check how many times are available this day
      if len(d['times']) > 1:
        # there are multiple times available on this date... got with first
        # self.log('Reservation for {} available at multiple times... skipping all but first time.'.format(d['date']))
        d['times'] = d['times'][0:1] # remove all but the first available time
        # self.log("Limiting to only 1 reservation on {}.".format(d['date']))

    # if you've got it, log it
    self.log_available_dates(good_dates, 'Limited to one time per day')

    # return the updated list
    return good_dates

  def limit_per_week(self, dates, person, max_per_week):
    """
    Limit the number of reservations we book per week.
    :param dates: A list of dates.
    :param person: The person for whom to limit reservations.
    :param max_per_week: The maximum number of reservations per week we desire.
    :returns: The updated list of dates
    """
    # do nothing further if no dates
    if len(dates) == 0:
      return []

    counts = {} # will hold counts of number of reservations each week

    # loop through all existing reservations
    reservations = self.get_reservations(person)    
    for r in reservations:
      # get the start date of the week within which this reservation falls
      week = self.get_start_of_week(r['date'])
      counts[str(week)] = counts.get(str(week), 0) + 1 # increment by one      

    # remove excess from modified dates list
    good_dates = dates.copy()
    for date in dates:
      # get the week within which this date falls
      week = self.get_start_of_week(date['date'])
      # get the number we already have reserved for this weeek
      count = counts.get(str(week), 0)
      # if we are over the limit, remove this date
      if max_per_week - count <= 0:
        # we have reached the weekly limit... no more
        # self.log('Weekly limit reached for {} {}... skipping {}.'.format(person.first_name, person.last_name, date['date']))
        good_dates.remove(date) # remove it from consideration
      else:
        counts[str(week)] = counts.get(str(week), 0) + 1 # increment by one

    # if you've got it, log it
    self.log_available_dates(good_dates, 'Limited to {} per week'.format(max_per_week))

    # return the updated list
    return good_dates


  def get_start_of_week(self, date, week_start_day=4):
    """
    Determine the date of the start of the week within which this date falls.
    :param date: A poorly-formatted date, without the year, such as 'July 10'
    :param week_start_day: The day that is considered the start of the week, as ant where 0=Monday, 1=Tuesday, etc.
    :returns: The date of the start of the week within this date falls.
    """
    # use the current year, since the year is missing from the date
    year = str(datetime.date.today().year)

    # convert date to date object
    date = '{} {}'.format(date, year) # tack on year to reservation date
    dt = datetime.datetime.strptime(date, '%B %d %Y')
    # week_start = dt - datetime.timedelta(days=dt.weekday()) # if the week starts on Monday
    # if the week starts on a different day, as is the case for this reservation system
    if dt.weekday() >= week_start_day:
      # for Friday (4), Saturday (5), or Sunday (6)...
      offset = dt.weekday() - week_start_day # e.g., for Sunday: 6 - 4 = 2; for Saturday: 5 - 4 = 1, etc.
    else:
      # for days earlier than Friday (i.e., < 4)...
      offset = dt.weekday() + (7 - week_start_day) # e.g., for Thursday 3 + 3 = 6; for Wednesday 2 + 3 = 5
    # offset by as many days as necessary to get to Friday
    week_start = dt - datetime.timedelta(days=offset)
    return week_start

  def get_reservations(self, person):
    """
    Get the reservations on file for a specific person.
    :param person: The person for whom to check the reservations.
    :returns: A list of reservations, where each item is a dictionary with reservation 'type', 'date', and 'time' fields.
    """
    # open up reservations file
    f = open('reservations.txt', 'r')

    reservations = []

    # loop through each line
    for line in f:
      line = line.strip()
      # get data from the line
      rdate, rtime, rtype, rfname, rlname = line.split(',')
      # check for a match
      if person.first_name.lower() == rfname.lower() and person.last_name.lower() == rlname.lower():
        # it's a match!
        reservation = {
          'type': rtype,
          'date': rdate,
          'time': rtime
        }
        # add to list
        reservations.append(reservation)

    f.close() # close file
    return reservations
    
  def reservation_exists(self, person, date, time):
    """
    Checks whether a reservation already exists for the person on this date.
    :param person: A Person object
    :param date: A date to check
    :param time: A time to check
    :returns: True if a reservation already exists for this person on this date, False otherwise.
    """

    # get a list of reservations
    reservations = self.get_reservations(person)

    # look for matches
    matches = [r for r in reservations if r['date'] == date and r['time'] == time]

    # return True if there's a match, False otherwise
    return len(matches) > 0 

  def select_dates(self, dates):
    """
    Add the selected dates to the website's 'cart'.
    :param dates: The dates to add.
    """
    more_than_one_option = False  # assume we do not have multiple date/time combos
    
    # loop through all dates
    for date in dates:
      # loop through all times for this date (we most likely only have one time, since we've filtered the times)
      for time in date['times']:
        # click the relevant element
        # print('clicking')
        el = time['element']  # each time is a dictionary with the time and a reference to the element on the page
        el.click()

        # let the dynamic content load
        # self.pause(1)

        # our next step depends on whether there is more than one date/time option we want to select
        more_than_one_option = len(dates) > 1 or len(date['times']) > 1
        if more_than_one_option:
          # there are multiple available options... select the first time slot on each day
          # we do this by clicking the 'Add a Time' button
          # logger.info('clicking to add {} on {}, {}'.format(t, day, date))
          # print('adding more')
          add_button = date['element'].find_element_by_css_selector('.btn-additional')
          add_button.click()
        else:
          # there is only one available time... select it and move on to the next date
          # we do this by clicking the 'Continue' button
          # logger.info('clicking to continue with {} on {}, {}'.format(t, day, date))
          # print('continuing')
          continue_button = date['element'].find_element_by_css_selector('.btn-next-step')
          continue_button.click()


    # if there are multiple otions, we must now click the continue button
    if more_than_one_option:
      # there are some invisible continue buttons we must ignore
      continue_buttons = self.driver.find_elements_by_css_selector('#selected-times-container > a.btn-next-step')
      visible_buttons = [btn for btn in continue_buttons if btn.is_displayed()]  # limit to those that are visible
      self.log('{} total, {} visible'.format(len(continue_buttons), len(visible_buttons)))
      # click the button... there should only be one visible one
      for btn in visible_buttons:
        if hasattr(btn, 'text'):
          self.log('Clicking {} button.'.format(btn.text))
        else:
          self.log('Clicking anonymous button.')
        btn.click()

    # pause to allow dynamic content to load
    self.pause(2)

  def enter_personal_details(self, person):
    """
    Enter the person's details into the form.
    :param person: The person for whom to enter details.
    """
    # try to complete reservation form
    try:
      # enter personal details
      fname = self.driver.find_element_by_css_selector('#first-name')
      fname.send_keys(person.first_name)
      lname = self.driver.find_element_by_css_selector('#last-name')
      lname.send_keys(person.last_name)
      phone = self.driver.find_element_by_css_selector('#phone')
      phone.send_keys(person.phone)
      email = self.driver.find_element_by_css_selector('#email')
      email.send_keys(person.email)

    except Exception as e:
      # save screenshot
      filename = 'logs/error-form-personal-details-{}.png'.format(datetime.date.today())
      self.save_screenshot(filename)

      # error occurred
      raise Exception('Error filling in personal details: {}'.format(e))

    # pause to allow dynamic content to load
    self.pause(1)

  def submit_form(self):
    """
    Submit the form on the web site to complete the reservation.
    """
    #submit button id #submit-forms-nopay
    try:
      submit = self.driver.find_element_by_css_selector('#custom-forms > div > div > input')
      submit.click()
      self.log('Submitted the form.')

      # pause to allow content to load
      self.pause(2)
    except Exception as e:
      # handle failure
      # save screenshot
      filename = 'logs/error-form-submit-{}.png'.format(datetime.date.today())
      self.save_screenshot(filename)

      # this is fatal.  Make sure program does not continue...
      raise Exception('Error submitting form: {}'.format(e))

  def save_screenshot(self, filename):
    """
    Capture a screenshot of the confirmation screen, for our records.
    :param filename: The name of the file to save.
    """
    filename = filename.lower()
    filename = filename.replace(' ', '')
    filename = filename.replace(':', '')
    filename = filename.replace('(', '-')
    filename = filename.replace(')', '-')
    try:
      # save screenshot of entire page
      # container = self.driver.find_element_by_css_selector('.content') # seems to be not found in some cases
      container = self.driver.find_element_by_tag_name('body')
      total_height = container.size["height"] + 100 # max out the height
      self.driver.set_window_size(1000, total_height) #the trick
      self.driver.save_screenshot(filename)
      self.log('Saved screenshot to {}'.format(filename))
    except Exception as e:
      self.log('Error saving screenshot to {}: {}'.format(filename, e))
      # not a catastrophic failure

  def save_reservation(self, dates, person):
    """
    Save the reservation to file.
    :param dates: The dates of our reservations.
    :param person: The person for whom to make the reservation.
    """
    try:
      # save these reservations to our file
      self.log('Saving reservation to reservations.txt')
      f = open('reservations.txt', 'a')
      # loop through each date
      for date in dates:
        # loop through each reserved time on that date
        for time in date['times']:
          # write the data to the line
          line = '{date},{time},{type},{fname},{lname}\n'.format(
            date=date['date'],
            type=date['type'],
            time=time['time'],
            fname=person.first_name,
            lname=person.last_name
          )
          f.write(line)
          self.log('Saved line: {}'.format(line))
      f.close()
    except Exception as e:
      self.log('Error saving reservation the file: {}'.format(e))

# try it out
if __name__ == '__main__':
  preferences = {
    'Monday': '10:00AM',
    'Tuesday': '-', # do not book
    'Wednesday': '-', # do not book
    'Thursday': '-', # do not book
    #'Friday': '-', # anytime Fridays
    'Saturday': '-', # do not book
    'Sunday': '-', # do not book
  }
  person = Person('Alice', 'Moore', '914-271-8239', 'alice.moore@safetymail.info', preferences)
  bot = ReservationBot(person, appointment_type='Senior Swim', hidden=False)
