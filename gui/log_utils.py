from datetime import datetime
import my_logger

logger = my_logger.myLogger("log_utils.py", "client")


def get_log_str(command, prePost):
    """
    Pre: Takes in command that is either sent to or from the server.  Parses that command and constructs
        a string for reporting in any particular status box.  Must pass in as prePost whether the command
         is pre-server exectution or post server exection.
    Post: Returns a string that is used to report in a status box through the GUI, e.g. the log box in the
          log tab.  If string is not made then it returns None.
    """
    command = command.split(" ")
    if prePost == 'pre':  # command is split with by white space
        key = command[0]

        if key == 'expose':
            return "Exposing for time %.2f sec" % itime
        if key == 'real':
            itime = float(command[3])
            return "Starting real time expsoures with %.2f sec" % itime
        if key == 'series':
            itime = float(command[3])
            number = int(command[2])
            return "Exposing for %d images with time %.2f sec" % (number, itime)
        if key == 'setTEC':
            temp = float(command[1])
            return "Setting temperature to %.1f C" % temp
        if key == 'warmup':
            return "Turning off cooler"
        if key == 'abort':
            return "Aborting current exposure..."
        if key == 'filter':
            key2 = command[1]
            if key2 == 'home':
                return "Starting homing sequence..."
            if key2 == 'move':
                filter = command[2]
                return "Moving to filter %s" % filter
            if key2 == 'getFilter':
                return "Getting filter position..."
            if key2 == 'connect':
                return "Please home filter..."

    if prePost == 'post':  # command has a key then is followed by relavent information delimited with commas
        key = command[0]
        logger.debug("key from post: " + str(key))
        stats = command[1].split(",")
        logger.debug("Stats in log:" + str(stats))
        if key == 'status':
            if int(stats[0]) == 20002:  # 20002 is "success" to Evora
                return "Camera already initialized connecting..."
            elif int(stats[0]) == 20075:
                return "Camera uninitialized this will take a few..."
            else:
                return "Camera drivers reporting incorrectly please run reinstall..."
        if key == 'expose':
            # at the end of stats is the image name
            name = stats[-1]
            itime = float(stats[2])
            results = int(stats[0])
            if results == 1:  # 1 for successful exposure
                return "\"%s\" completed with time %.2f sec" % (name, itime)
            else:
                return "\"%s\" failed to expose..." % name
        if key == 'real':
            results = stats[0]
            return "Real time exposure successfully done..."
        if key == 'series':
            results = stats[0]
            return "Done take series images..."
        if key == 'seriesSent':
            name = stats[-1]
            itime = float(stats[1])
            return "\"%s\" completed with time %.2f sec" % (name, itime)
        if key == 'connect':
            if int(stats[0]) == 20002:  # 20002 is "success" Evora
                return "Initialization completed..."
            else:
                return "Initialization failed..."
        if key == 'connectLost':
            return "Disconnected from camera normally..."
        if key == 'connectFailed':
            return "Disconnected from camera suddenly..."
        if key == 'getTEC':
            pass
        if key == 'setTEC':
            temp = float(stats[0])
            return "Successfully set cooler to %.1f C" % temp
        if key == 'warmup':
            return "Successfully warming up..."
        if key == 'temp':
            results = stats[0]  # 1 for success 0 for failure
            if results == 1:
                return "Successfully shutdown cooler..."
            else:
                return "Failure in setting cooler down..."
        if key == 'startup':
            if int(stats[0]) == 20002:
                return "Camera initialization successful..."
            else:
                return "Camera initialization went wrong check the server..."
        if key == 'shutdown':
            results = stats[0]
            return "Successfully shutdown camera..."
        if key == 'abort':
            results = stats[0]
            return "Successfully aborted exposure..."
        if key == 'filter':
            key2 = command[1]
            stats = command[2].split(",")
            if key2 == 'home':
                if int(stats[0]) == 1:
                    return "Successfully homed..."
                else:
                    return "Failed to home, try again..."
            if key2 == 'move':
                if bool(stats[0]):
                    return "Successfully moved filter..."
                else:
                    return "Failed to move filter..."
            if key2 == 'findPos':
                return "Adjusting fitler this can take awhile..."
            if key2 == 'getFilter':
                key3 = command[2]
                stats = command[3].split(",")
                if key3 == 'report':
                    filter = stats[0]
                    return "At filter %s" % filter
                if key3 == 'finding':
                    filter = stats[0]
                    pos = int(stats[1])
                    return "Filter settleing in on position %d, or filter %s..." % (pos, filter)
                else:
                    filter = stats[0]
                    pos = int(stats[1])
                    return "At position %d, setting filter to %s..." % (pos, filter)
            if key2 == 'connectLost':
                return "Connection to filter lost normally..."
            if key2 == 'connectFailed':
                return "Connection to filter failed suddenly..."
    return None


def time_stamp():
    """
    Pre: No arguments are needed to invoke this method.
    Post: Returns a string with the current date and time.
    """
    time = datetime.today()
    # stamp = "[%s/%s/%s, " % (time.month, time.day, time.year)
    hour = ""
    minute = ""
    second = ""
    if time.hour < 10:
        hour += "0" + str(time.hour)
    else:
        hour += str(time.hour)

    if time.minute < 10:
        minute += "0" + str(time.minute)
    else:
        minute += str(time.minute)

    if time.second < 10:
        second += "0" + str(time.second)
    else:
        second += str(time.second)

    stamp = "[%s:%s:%s]" % (hour, minute, second)
    return stamp


def print_stamp():
    """
    Pre: User needs nothing to pass in.
    Post: Returns a string catalogging the date and time in the format of [month day year, 24hour:minute:seconds]
    """
    day = datetime.today()
    string = day.strftime("[%b %m, %y, %H:%M:%S]")
    return string + " "


class Logger(object):
    """
    This class when assigned to sys.stdout or sys.stderr it will write to a file that is opened everytime a new GUI session is started.
    It also writes to the terminal window.
    """
    def __init__(self, stream):
        self.terminal = stream

    def write(self, message):
        self.terminal.flush()
        self.terminal.write(message)
        # disabled becuase logfile definition is commented out
        # logFile.write(message)

    def stamp(self):
        d = datetime.today()
        string = d.strftime("[%b %m, %y, %H:%M:%S]")
        return string
