import datetime
from user_agents import parse
from math import ceil
import math
from flask import request, url_for, current_app


def paginate(query, page=None, per_page=None):
    """This function performs pagination on query dataset

    Args:
        query: this db query
        page: the current page number (optional)
        per_page: the number of item per page (optional)
    
    rturn: dictionary
    """
      
    total = query.count()
    pages = int(ceil(total / float(per_page)))
    start = (page - 1) * per_page
    end = start + per_page
    # items = [item.serialize() for item in query.slice(start, end)]
    limited_query = query.offset(start).limit(per_page)
    items = [item.serialize() for item in limited_query]
    
    prev_url = None
    next_url = None
    if page > 1:
        prev_url = url_for(request.endpoint, page=page - 1)
    if page < pages:
        next_url = url_for(request.endpoint, page=page + 1)

    return {
        "items": items,
        "pagination": {
            "total": total,
            "pages": pages,
            "page": page,
            "per_page": per_page,
            "prev_url": prev_url,
            "next_url": next_url,
        },
    }


def calculate_percentage(expected_donation: float, total_donation: float) -> float:
    """function to calcualte the current donation percentage of the total goal

    Args:
        expected_donation->float: The amount expected.
        total_donation->float: The amount donated so far.

    Returns: percentage_donation (percenatge | float)


    """
    donation_in_percentage = (total_donation / expected_donation) * 100
    return donation_in_percentage


def calculate_percentage_changes(totals):
    """this function calculates the percentage changes in daily, weekly and monthly donation.

    Args: Totals (daily, weekly or monthly)

    rturn: changes in percentage
    """
    percentage_changes = {}
    sorted_keys = sorted(totals.keys())

    if len(sorted_keys) == 0:
        percentage_changes["No Data"] = 0
    elif len(sorted_keys) == 1:
        percentage_changes[sorted_keys[0]] = 0
    
    for i in range(1, len(sorted_keys)):
        current_key = sorted_keys[i]
        previous_key = sorted_keys[i - 1]
        current_total = totals[current_key]
        previous_total = totals[previous_key]
        if previous_total != 0:
            change = ((current_total - previous_total) / previous_total) * 100
        else:
            change = float('inf') 
        percentage_changes[current_key] = change
    return percentage_changes

def calculate_average(totals, counts):
        averages = {}
        for key in totals.keys():
            averages[key] = totals[key] / counts[key] if counts[key] != 0 else 0
        return averages

def generate_transaction_reference(merchant_id=None):
    """This function helps generate transaction reference for each flutterwave tranaction
    Args:
     merchant_id(optional)
    """

    current_time = datetime.datetime.now()
    timestamp = int(current_time.timestamp() * 1990)
    common_identify: str = "akon"
    if merchant_id:
        return merchant_id + "-" + common_identify + "-" + str(timestamp)
    else:
        return "MC-" + "-" + common_identify + str(timestamp)


def calculate_time_interval(date):
    """use to calculate campaign deadline.
        It takes the date selected by the user and calculate
        the days and hour remaining until the deadline..
    """
    time_remaining = ""

    # convert date to datetime
    date_object = datetime.datetime.strptime(date, "%Y-%m-%d")

    duration = str(date_object - datetime.datetime.now()).rsplit(sep=',')

    day = duration[0].strip()

    # TODO: List out of range issues for day less than two
    hour = duration[1].strip().rsplit(sep=":")[0]

    if int(hour) > 1:

        time_remaining = f'{day} {hour} hours'
    else:
        time_remaining = f'{day} {hour} hour'

    return time_remaining

def process_date_type(db_date):
    db_date = datetime.datetime.strptime(db_date, "%Y-%m-%d-%H:%M:%S")
    time = db_date.strftime("%H:%M:%S").split(':')[0]
    date = db_date.strftime("%Y-%m-%d")
    month = db_date.strftime("%d %B")
    formated_month = db_date.strftime("%B %d")
    actual_time = date if int(time) > 23 else f'{db_date.strftime("%H:%M")} (today)'
    return time, date, month, formated_month, actual_time


def round_up_one_decimal_place(number):
    return math.ceil(number * 10) / 10.0

def get_arrow_attributes(is_positive):
    if is_positive:
        return "up text-success", "ni-arrow-long-up"
    else:
        return "down text-danger", "ni-arrow-long-down"

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']



def get_ip():
    if request.headers.get('X-Forwarded-For'):
        return request.headers.get('X-Forwarded-For').split(',')[0]
    return request.remote_addr

def get_device_info():
    user_agent = request.headers.get('User-Agent')
    user_agent_parsed = parse(user_agent)
    return {
        'browser': user_agent_parsed.browser.family,
        'browser_version': user_agent_parsed.browser.version_string,
        'os': user_agent_parsed.os.family,
        'os_version': user_agent_parsed.os.version_string,
        'device': user_agent_parsed.device.family,
        'is_mobile': user_agent_parsed.is_mobile,
        'is_tablet': user_agent_parsed.is_tablet,
        'is_pc': user_agent_parsed.is_pc
    }
