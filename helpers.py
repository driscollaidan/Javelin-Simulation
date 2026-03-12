import random
import time

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