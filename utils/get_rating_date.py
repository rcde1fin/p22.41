# import datetime
from datetime import datetime
# import timezone from pytz module
from pytz import timezone


def getratingdate():
    # define format of datetime
    date_format = "%Y-%m-%d"

    # get current time in UTC timezone
    now_utc = datetime.now(timezone('UTC'))

    # convert now_utc to Asia/Manila time zone
    now_asia_mnl = now_utc.astimezone(timezone('Asia/Manila'))

    # assign now_asia_mnl to mnl_date variable
    mnl_date = now_asia_mnl.strftime(date_format)
    # print("mnl_date", mnl_date)  # DEBUG INFO

    rating_date = mnl_date + ' 00:00:00'

    return rating_date
