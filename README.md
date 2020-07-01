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

Install `selenium` and `schedule` via `pip`:

```bash
pip install -r requirements.txt
```

The Webdriver for Chrome (a.k.a. the file named chromedriver) must be installed in either:

- in the same directory as chrome.exe on Windows (e.g. C:\Program Files\Google\Chrome\Application)
- in a directory that is included in the PATH on Mac OS X (e.g. /usr/local/bin)
