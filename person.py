"""
A representation of a person who wants a reservation at Silver Lake!
"""

class Person:

  def __init__(self, fname, lname, phone, email, appointment_types=['11:30 and 2:30', '5:30'], preferences={}):
    """
    Initialize a person with required properties for a reservation.
    :param fname: First name
    :param lname: Last name
    :param email: Email address
    :param phone: Phone number
    :param appointment_types: Names of appointment types to try to reserve in a list, e.g. ['11:30 and 2:30', '5:30', 'Senior Swim']
    :param preferences: The days/times to try to reserve, as a dictionary, e.g. { 'Monday': '11:30AM', 'Wednesday': '-' } for Mondays at that specific time, no times Wednesdays, and any times on any other days not mentioned.
    """
    self.first_name = fname
    self.last_name = lname
    self.phone = phone
    self.email = email

    # appointment type preferences
    self.appointment_types = appointment_types

    # date preferences
    self.preferences = preferences
