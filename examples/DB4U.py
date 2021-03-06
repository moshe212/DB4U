"""
PyXLL Examples: Real time data

As well as returning static values from functions, PyXLL functions
can return special 'RTD' instances that can notify Excel of
updates to their value.

This could be used for any real time data feed, such as live
prices or the status of a service.
"""
from pyxll import RTD, xl_func, xl_app
from datetime import datetime
import threading
import logging
import time
import sys

import pyodbc
import random

conn = pyodbc.connect('Driver={SQL Server};'
                      'Server=DESKTOP-VJQLB95;'
                      'Database=Yad2;'
                      'Trusted_Connection=yes;')

cursor = conn.cursor()

_log = logging.getLogger(__name__)


def sql_connect():
    try:

        SQLCommand = ('select top 5 City from mainposts')
        resulte = cursor.execute(SQLCommand)
        conn.commit()
        return resulte

    except pyodbc.Error as e:
        print(e)
        print('Can not get data from sql')


class CurrentTimeRTD(RTD):
    """
    CurrentTimeRTD periodically updates its value with the current
    date and time. Whenever the value is updated Excel is notified
    and when Excel refreshes the new value will be displayed.
    """

    # def __init__(self):
    #     initial_value = datetime.now().strftime(format)
    #     super(CurrentTimeRTD, self).__init__(value=initial_value)
    #     self.__format = format
    #     self.__running = True
    #     self.__thread = threading.Thread(target=self.__thread_func)
    #     self.__thread.start()

    def connect(self):
        # Called when Excel connects to this RTD instance, which occurs
        # shortly after an Excel function has returned an RTD object.
        self.__running = True
        self.__thread = threading.Thread(target=self.__thread_func)
        self.__thread.start()
        _log.info("CurrentTimeRTD Connected")

    def disconnect(self):
        # Called when Excel no longer needs the RTD instance. This is
        # usually because there are no longer any cells that need it
        # or because Excel is shutting down.
        self.__running = False
        _log.info("CurrentTimeRTD Disconnected")

    def __thread_func(self):
        while self.__running:

            try:
                # Setting 'value' on an RTD instance triggers an update in Excel
                SQLCommand = (
                    'select top 5 City from mainposts ORDER BY NEWID()')
                cursor.execute(SQLCommand)
                self.value = []
                for i in cursor:
                    print(i)
                    self.value.append(i)
                # self.value = [random.random() for x in range(10)]

                _log.info(self.value)
            except:
                _log.error("Error setting RTD value", exc_info=True)

                # Report the error back to Excel
                exc_type, exc_value, exc_trace = sys.exc_info()
                self.set_error(exc_type, exc_value, exc_trace)

            time.sleep(5)


@xl_func(": rtd")
def rtd_current_data():
    """Return the current time as 'real time data' that
    updates automatically.

    The 'recalc_on_open' option is used so that any
    cells using this function start ticking as soon
    as the workbook is opened.

    :param format: datetime format string
    """
    # try:
    #     # Setting 'value' on an RTD instance triggers an update in Excel
    #     data = sql_connect()

    #     _log.info(data)
    # except:
    #     _log.error("Error setting RTD value", exc_info=True)

    return CurrentTimeRTD()


# @xl_func("int interval: var")
# def rtd_set_throttle_interval(interval):
#     """Set Excel's RTD throttle interval (in milliseconds).

#     When real time data objects notify Excel that they have changed
#     the displayed value in Excel doesn't actually update until
#     Excel refreshes. How often Excel refreshes due to RTD updates
#     defaults to every 2 seconds, and so to see data refresh more
#     frequently this function may be used.
#     """
#     xl = xl_app()
#     xl.RTD.ThrottleInterval = interval
#     return "OK"
