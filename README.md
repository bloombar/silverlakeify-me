# Silver Lake Reservation Bot

This program makes reservations at the Silver Lake swimming park in Croton-on-Hudson by filling in and submitting the online reservation form at https://silverlakereservations.as.me/

## Background

Due to the COVID-19 pandemic, all visitors to Silver Lake must make an online reservation no more than one week in advance. Visitors are limited to 3 visits per week. Due to the popular nature of the park and the pandemic-induced social distancing requirements, these limited reservations are filled very quickly. A bot is necessary.

## How it works

The program named `silver_lakeify_me.py` should be run in the background. On a regular interval, adjustable in the code, such as every 10 minutes or every day at 11:30AM, the program will attempt to make a reservation for the first 3 available day/time slots.

The actual reservations are handled by code in the file named `silver_lakeify_me.py`. This file uses the **selenium** automation framework to open Google Chrome to the appropriate web site, enter the reservation details into the online form, and submit the form.

## Dependencies

This program depends upon a few Python modules:

- selenium
- schedule
- [WeDriver for Chrome](https://sites.google.com/a/chromium.org/chromedriver/downloads) - download the appropriate one for your version of Google Chrome

### Installing modules

Install `selenium` and `schedule` via `pip`:

You can either install individually:

```bash
pip install schedule
pip install selenium
```

... or install using the dependency file:

```bash
pip install -r requirements.txt
```

### Installing WebDriver for Chrome

The Webdriver for Chrome (a.k.a. the file named chromedriver) must be installed separately.

- [Download the webdriver](https://sites.google.com/a/chromium.org/chromedriver/downloads) that is suitable for the version of Google Chrome you have installed
- This will give you a file named `chromedriver` or `chromedriver.exe`.

Place the `chromedriver` file into a directory that is on your system's PATH. I.e., place it...

- in the same directory as chrome.exe on Windows (e.g. C:\Program Files\Google\Chrome\Application)
- in a directory that is included in the PATH on Mac OS X (e.g. /usr/local/bin)
