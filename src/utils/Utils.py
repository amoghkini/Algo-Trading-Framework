import math
import logging


class Utils:

  @staticmethod
  def roundToNSEPrice(price):
    x = round(price, 2) * 20
    y = math.ceil(x)
    return y / 20
