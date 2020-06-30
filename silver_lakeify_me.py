"""
Sign up for Silver Lake

Selenium webdriver for Chrome (a.k.a. the file named chromedriver) must be installed in either:
- in the same directory as chrome.exe on Windows (e.g. C:\Program Files\Google\Chrome\Application)
- in a directory that is included in the PATH on Mac OS X (e.g. /usr/local/bin)
"""

def make_reservation(people):
  """
  Expects a list of people as an argument, such as:

  people = [
    {
      'fname': 'Foo',
      'lname': 'Barstein',
      'phone': '6462129988',
      'email': 'foo@barstein.com'
    },
    {
      'fname': 'Bar',
      'lname': 'Fooberger',
      'phone': '2126468899',
      'email': 'bar@fooberger.com'
    },
  ]

  :param people: list of people, where each person is a dictionary with 'fname', 'lname', 'phone', and 'email' fields.
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
    filename='logs/reservations.txt',
    filemode='a'
  )
  logger = logging.getLogger('status')

  # loop through all the people we want to make reservations for
  for person in people:

    logger.info('starting for {} {}'.format(person['fname'], person['lname']))

    # open the driver
    url = 'https://silverlakereservations.as.me'
    driver = webdriver.Chrome()
    driver.get(url)

    # select appointment type
    appointment = driver.find_element_by_css_selector('#step-pick-appointment > div.pane-content > div.select.select-type > div:nth-child(4)')
    appointment.click()

    # pause for a second
    ActionChains(driver).pause(1).perform()

    # select tomorrow 11:30AM
    # datetime = driver.find_element_by_css_selector('#dates-and-times > fieldset > div > div > div > ul > li:nth-child(1) > a')
    # datetime.click()

    # select all available options
    num_datetimes = 0
    datetime_options = driver.find_elements_by_css_selector('#dates-and-times > fieldset > div > div > div > ul > li > a')

    logger.info('found {} available datetimes'.format( len(datetime_options) ))

    for option in datetime_options:
      # try to click em all! (some are not attached to page)
      try:
        option.click()
        num_datetimes += 1
      except:
        continue

    reservation_submitted = False # assume the worst, but hope for the best

    # only continue if we were successfully able to click at least one datetime option
    if num_datetimes > 0:
      # pause for a second
      ActionChains(driver).pause(1).perform()

      # try to complete reservation
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
        submit = driver.find_element_by_css_selector('#custom-forms > div > div > input')
        submit.click()

        reservation_submitted = True

      except:
        pass

    if reservation_submitted:
      # log it
      logger.info('submitted {} reservations for {} {}'.format(num_datetimes, person['fname'], person['lname']))
    else:
      # log it
      logger.info('no reservation available for {} {}'.format(person['fname'], person['lname']))

    # finished!
    driver.close()


# mouse over
# ActionChains(driver).move_to_element(trigger).perform() 

# pause for a second
# ActionChains(driver).pause(1).perform()


# if running this file directly...
if __name__ == '__main__':
  people = [
    {
      'fname': 'Foo',
      'lname': 'Barstein',
      'phone': '6462129988',
      'email': 'foo@barstein.com'
    },
  ]
  make_reservation(people)

