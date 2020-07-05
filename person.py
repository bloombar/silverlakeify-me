"""
A representation of a person who wants a reservation at Silver Lake!
"""

class Person:

  def __init__(self, fname, lname, phone, email, preferences={}):
    """
    Initialize a person with required properties for a reservation.
    :param fname: First name
    :param lname: Last name
    :param email: Email address
    :param phone: Phone number
    """
    self.first_name = fname
    self.last_name = lname
    self.phone = phone
    self.email = email

    # date preferences
    self.preferences = preferences
