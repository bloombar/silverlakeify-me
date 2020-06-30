# Silver Lake Reservation Bot

This program makes reservations at the Silver Lake swimming park in Croton-on-Hudson by filling in and submitting the online reservation form at https://silverlakereservations.as.me/

## Background

Due to the COVID-19 pandemic, all visitors to Silver Lake must make an online reservation no more than one week in advance. Due to the popular nature of the park and the pandemic-induced social distancing requirements, these limited reservations are filled very quickly.

## How it works

The program named `scheduler.py` should be run in the background. At 11:30AM EST every day, the program will attempt to make a reservation for all available days and times. It does so for as many people as are indicated in the list called `people` in the code.

The actual reservations are handled by code in the file named `silver_lakeify_me.py`. This file uses the **selenium** automation framework to open Google Chrome to the appropriate web site, enter the reservation details into the online form, and submit the form.
