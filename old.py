#!/usr/bin/env python3
"""
Sign up for Silver Lake

Selenium webdriver for Chrome (a.k.a. the file named chromedriver) must be installed in either:
- in the same directory as chrome.exe on Windows (e.g. C:\Program Files\Google\Chrome\Application)
- in a directory that is included in the PATH on Mac OS X (e.g. /usr/local/bin)
"""

def make_reservation(person):
  """
  Makes any and every available reservation for a single person.
  
    {
      'fname': 'Foo',
      'lname': 'Barstein',
      'phone': '6462129988',
      'email': 'foo@barstein.com'
    }

  :param people: a person as a dictionary with 'fname', 'lname', 'phone', and 'email' fields.
  """
  
  import logging
  from selenium import webdriver
  from selenium.webdriver import ActionChains
  from selenium.webdriver.common.keys import Keys

  # logging
  logging.basicConfig(
    level=logging.INFO,
    # format="%(asctime)s %(levelname)s %(threadName)s %(name)s %(message)s",
    format="%(asctime)s %(message)s",
    datefmt='%Y-%m-%d %H:%M:%S',
    filename='logs/log.txt',
    filemode='a'
  )
  logger = logging.getLogger('status')

  # open the webdriver
  url = 'https://silverlakereservations.as.me'
  chrome_options = webdriver.ChromeOptions() # set some options
  chrome_options.add_argument("--headless") # run in background
  driver = webdriver.Chrome(options=chrome_options)
  driver.get(url)

  # pause for a second
  ActionChains(driver).pause(2).perform()

  # get a list of all available appointment types
  all_appointment_types = driver.find_elements_by_css_selector('#step-pick-appointment > div.pane-content > div.select.select-type > div')
  all_appointment_types = [t for t in all_appointment_types if t.is_displayed()] # limit to those that are visible
  selected_appointment_types = []  # we will select a subset of all types
  found_appointment_type = False

  # desired_appointment_type = 'Senior Swim'
  desired_appointment_type = '11:30 and 3:30'

  # loop through all types
  for atype in all_appointment_types:
    try:
      # grab this appointment type's name, if any
      title = atype.find_element_by_tag_name('label').text
      # check whether it's of the kind we want to select
      if desired_appointment_type in title:
        found_appointment_type = True
        selected_appointment_types.append(atype) # add the the list
    except:
      pass

  # verify that we can find the appointment type we're looking for
  if not found_appointment_type:
    logger.info('appointment type not found: {}'.format(desired_appointment_type))
    return
    
  # loop through the appointment types we've picked
  for atype in selected_appointment_types:
    # grab this appointment type's title, if any
    title = atype.find_element_by_tag_name('label').text
    # logger.info('appointment type: {}'.format(title))

    # click it
    atype.click()

    # pause for a second
    ActionChains(driver).pause(2).perform()

    # select all dates - each date is in its own fieldset
    available_datetimes = driver.find_elements_by_css_selector('#dates-and-times > fieldset')
    available_datetimes = [dt for dt in available_datetimes if dt.is_displayed()] # limit to those that are visible

    # check whether there are any available datetimes
    if len(available_datetimes) <= 0:
      # logger.info('no available datetimes')
      continue

    # loop through each datetime
    reservations = {} # this will store all reservation data that is successfully submitted
    num_selections = 0
    for dt in available_datetimes:

      # grab this day, date, and time
      day = dt.find_element_by_css_selector('div.day-of-week').text
      date = dt.find_element_by_css_selector('div.date-secondary').text
      time_labels = dt.find_elements_by_css_selector('div.choose-time div.form-inline label')

      # set up data storage for any reservations we make for this date
      reservations[date] = [] # will hold times we pick on this date

      # loop through all available times on this date
      time_selected = False  # we only want to pick one time per day
      for label in time_labels:
        # if we've already selected a time on this day, skip the rest on this day
        if time_selected or num_selections >= 3:
          continue

        t = label.text  # grab the text from this label... it stores the time slot
        # logger.info('option: {}, {}, {}'.format(day, date, t))

        # check whether we already have a reservation for this slot
        if reservation_exists(person, date, t):
          logger.info('skipping... reservation already exists for {}{} at {} {}'.format(person['fname'], person['lname'], date, t))
          continue

        logger.info('selecting {} on {}, {}'.format(t, day, date))
        label.click()  # click this time option
        
        # pause for a second
        ActionChains(driver).pause(2).perform()

        num_selections += 1 # track how many datetimes we've selected
        time_selected = True # prevents us from picking two times on the same day

        # the form is a bit dynamic...
        # if there are multiple available dates or times, you must click the label to get the option to add it to your 'cart'
        # otherwise if there is only one available date and time, you can simply click 'continue' to select it

        if len(available_datetimes) > 1 or len(time_labels) > 1:
          # there are multiple available options... select the first time slot on each day
          # we do this by clicking the 'Add a Time' button
          logger.info('clicking to add {} on {}, {}'.format(t, day, date))
          add_button = dt.find_element_by_css_selector('.btn-additional')
          add_button.click()

        else:
          # there is only one available time... select it and move on to the next date
          # we do this by clicking the 'Continue' button
          logger.info('clicking to continue with {} on {}, {}'.format(t, day, date))
          continue_button = dt.find_element_by_css_selector('.btn-next-step')
          continue_button.click()

        # store this in our reservations data
        reservations[date].append( {'type': title, 'time': t} ) # store this time for this date
        logger.info('storing data: {}'.format(reservations[date]))

        # pause for a second
        ActionChains(driver).pause(2).perform()

    # we've selected all the dates/times... so now complete the form

    # if there are multiple datetimes, we must first click the continue button at the top
    if num_selections > 1:
      # there are some invisible continue buttons we must ignore
      continue_buttons = driver.find_elements_by_css_selector('#selected-times-container > a.btn-next-step')
      visible_buttons = [btn for btn in continue_buttons if btn.is_displayed()]  # limit to those that are visible
      logger.info('{} total, {} visible'.format(len(continue_buttons), len(visible_buttons)))
      # click the button... there should only be one visible one
      for btn in visible_buttons:
        logger.info('clicking to continue with {} selections'.format(num_selections))
        btn.click()

    # pause for a second
    ActionChains(driver).pause(2).perform()

    # try to complete reservation form
    try:
      # enter personal details
      fname = driver.find_element_by_css_selector('#first-name')
      fname.send_keys(person['fname'])
      lname = driver.find_element_by_css_selector('#last-name')
      lname.send_keys(person['lname'])
      phone = driver.find_element_by_css_selector('#phone')
      phone.send_keys(person['phone'])
      email = driver.find_element_by_css_selector('#email')
      email.send_keys(person['email'])

      # pause for a second
      ActionChains(driver).pause(1).perform()

      # submit the reservation
      #submit button id #submit-forms-nopay
      submit = driver.find_element_by_css_selector('#custom-forms > div > div > input')
      submit.click()

      # pause for a second
      ActionChains(driver).pause(2).perform()

      logger.info('submitted the form')

      clean_date = date.replace(':', '')
      clean_date = date.replace(' ', '')
      filename = 'logs/{}-{}-{}-{}.png'.format(person['lname'], person['fname'], title, clean_date)
      filename = filename.replace(' ', '')
      filename = filename.replace(':', '')
      filename = filename.replace('(', '')
      filename = filename.replace(')', '')
      filename = filename.lower()
      # body = driver.find_element_by_tag_name('body')
      # body.save_screeenshot(filename)
      logger.info('saving screenshot to {}'.format(filename))
      driver.save_screenshot(filename)

    except:
      logger.info('failed to submit the form')

      # remove this entry from our reservation data
      del reservations[date]
      pass

    try:
      # save this reservation to our file
      logger.info('saving reservation to reservations.txt')
      f = open('reservations.txt', 'a')
      # loop through each date
      for date, spots in reservations.items():
        # loop through each reserved time on that date
        logger.info('saving lines for {}'.format(date))
        for spot in spots:
          # write the data to the line
          # logger.info('date: {}'.format(date))
          # logger.info('type: {}'.format(spot['type']))
          # logger.info('time: {}'.format(spot['time']))
          line = '{date},{time},{type},{fname},{lname}\n'.format(
            date=date,
            type=spot['type'],
            time=spot['time'],
            fname=person['fname'],
            lname=person['lname']
          )
          logger.info('saving line: {}'.format(line))
          f.write(line)
      f.close()
    except:
      logger.info('failed to save data the file')


  # finished!
  driver.close()

  # mouse over
  # ActionChains(driver).move_to_element(trigger).perform() 

  # pause for a second
  # ActionChains(driver).pause(1).perform()

def reservation_exists(person, date, time):
  """
  Checks whether a reservation already exists for the person on this date.
  :returns: True if a reservation already exists for this person on this date, False otherwise.
  """
  # open up reservations file
  f = open('reservations.txt', 'r')
  # loop through each line
  for line in f:
    line = line.strip()
    # get data from the line
    rdate, rtime, rtype, rfname, rlname = line.split(',')
    # check for a match
    if person['fname'].lower() == rfname.lower() and person['lname'].lower() == rlname.lower() and date == rdate and time == rtime:
      # we found a match
      return True

  # no match
  return False

# if running this file directly...
if __name__ == '__main__':
  import schedule
  import time

  people = [
    {
      'fname': 'Robert',
      'lname': 'Oppenheimer',
      'phone': '8482712299',
      'email': 'robertoppenheimer@mailinator.com'
    },
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

  # make_reservation(people[0])

  # schedule.every(2).day.at("11:30").do(make_reservation, person)
  schedule.every(1).minutes.do(make_reservation, people[2])

  # for person in people:
  #   # schedule every day at 11:30AM
  #   schedule.every().day.at("11:30").do(make_reservation, person)

  # flush out pending jobs
  while True:
      schedule.run_pending()
      time.sleep(15)
