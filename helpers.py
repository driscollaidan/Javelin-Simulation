import random
import time
import spiceypy as spice

def assemble_time_string(time):

    year = int(time["year"])
    month = int(time["month"])
    day = int(time["day"])
    hour = int(time["hour"])
    minute = int(time["minute"])
    second = int(time["second"])

    components = [year, month, day, hour, minute, second]
    for i in range(len(components)):
        if components[i] < 10:
            components[i] = "0" + str(components[i])
        else:
            components[i] = str(components[i])

    return "-".join(components[:3]) + "T" + ":".join(components[3:])

def seed():
    random.seed(time.time())

def random_integer(minimum, maximum):
    return random.randint(minimum, maximum)

def random_float(minimum, maximum):
    return random.uniform(minimum, maximum)

def process_time(time): 
        month_dict = {
            "Jan": 1,
            "Feb": 2,
            "Mar": 3,
            "Apr": 4,
            "May": 5,
            "Jun": 6,
            "Jul": 7,
            "Aug": 8,
            "Sep": 9,
            "Oct": 10,
            "Nov": 11,
            "Dec": 12
        }

        year = int(time[0:4])
        month = month_dict[time[5:8]]
        day = int(time[9:11])
        hour = int(time[12:14])
        minute = int(time[15:17])
        second = int(time[18:20])

        time_dict = {
            "year": year,
            "month": month,
            "day": day,
            "hour": hour,
            "minute": minute,
            "second": second
        }

        et = spice.utc2et(assemble_time_string(time_dict))
        return et