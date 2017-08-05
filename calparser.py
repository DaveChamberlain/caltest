# this is on a branch

import arrow
# from urllib3 import urlopen
import urllib.request
#from ics import Calendar
from icalendar import Calendar, Event
import datetime

weekdays = ['MO', 'TU', 'WE', 'TH', 'FR', 'SA', 'SU']

def day_phrase(days):
    if days == 0:
        return "tomorrow"
    elif days == 1:
        return "the day after tomorrow"
    else:
        return "in {:d} days".format(days)

def hour_phrase(time):
    hour = time.hour
    min = time.minute
    ampm = "a.m."

    if hour > 12:
        hour -= 12
        ampm = "p.m."

    return "at {:d}:{:02d} {}".format(hour, min, ampm)


def get_date(dt):
    if isinstance(dt, list):
        dt = dt[0]

    try:
        event_date = dt.date()
    except Exception:
        event_date = dt

    return event_date


def check_weekly_recur_date(today, tomorrow, recur, interval):
    if interval is None:
        interval = 1

    for freq in recur:
        dow = weekdays.index(freq)

        if dow == today.weekday():
            print (interval)
            return today
        elif dow == tomorrow.weekday():
            print (interval)
            return tomorrow

    return None


def check_monthly_recur_date(today, tomorrow, recur):
    for freq in recur:
        if len(freq) == 2:
            freq = '0' + freq
        num = int(freq[0:len(freq)-2])
        day = freq[len(freq)-2:]
        day_of_week = weekdays.index(day)

        # find the first day of this month
        temp_day = today.replace(day=1)

        # move to the next day of week we need
        while num > 0:
            if temp_day.weekday() == day_of_week:
                num -= 1
            if num > 0:
                temp_day = temp_day + datetime.timedelta(days=1)

        if temp_day == today:
            return today
        elif temp_day == tomorrow:
            return tomorrow

    return None

def get_today_events(events):
    utc = arrow.utcnow()
    today = utc.to('US/Eastern').date()
    tomorrow = today + datetime.timedelta(days=1)

    for event in events.walk():
        if event.name == "VEVENT":
            dtstart = event.get('dtstart')
            if dtstart:

                event_date = get_date(dtstart.dt)

                if event_date in (today, tomorrow):
                    print(event.get('summary'))

                elif event_date < today:
                    rrule = event.get('RRULE')
                    if rrule:
                        # It is a repeating rule.  If there is no end date, or the end date is in the future
                        rule_end = get_date(rrule.get('UNTIL'))
                        freq = rrule.get('FREQ')
                        recur = rrule.get('COUNT')

                        if recur and not rule_end:
                            recur = recur[0]
                            if freq[0] == 'MONTHLY':
                                rule_end = event_date + datetime.timedelta(months=recur)
                            elif freq[0] == 'WEEKLY':
                                rule_end = event_date + datetime.timedelta(days=(recur * 7))
                            elif freq[0] == 'DAILY':
                                rule_end = event_date + datetime.timedelta(days=recur)

                        if rule_end is None or rule_end > tomorrow:
                            # it is an event that could happen, so figure out if it

                            if freq[0] == 'MONTHLY':
                                recur_date = check_monthly_recur_date(today, tomorrow, rrule.get('BYDAY'))
                            elif freq[0] == 'WEEKLY':
                                recur_date = check_weekly_recur_date(today, tomorrow, rrule.get('BYDAY'),
                                                                     rrule.get('INTERVAL'))

                            if recur_date:
                                print(event.get('summary'), "happens: ", recur_date)
                            else:
                                pass
                                # print("Repeating event: ", event.get('summary'), event_date, "-", rule_end,
                                #       rrule.get('FREQ'), rrule.get('BYDAY'), rrule.get('COUNT'), rrule.get('INTERVAL'),
                                #       rrule)


def get_string(url, name):
    # c = Calendar(urlopen(url).read().decode('iso-8859-1'))
    # c = Calendar(urllib.request.urlopen(url).read().decode('iso-8859-1'))
    c = Calendar.from_ical(open('calendar.ics').read())
    # c = Calendar.from_ical(open('basic.ics').read())

    get_today_events(c)
    # for component in c.walk():
    #     if component.name == "VEVENT":
    #         print (component.get('summary'), component.get('dtstart'), component.get('dtend'), component.get('dtstamp'))

    utc = arrow.utcnow()
    local = utc.to('US/Eastern')

    # for e in c.events:
    #     if local.date() <= e.begin.date():
    #         diff = e.begin.datetime - local.datetime
    #         total_seconds = diff.days * 24 * 60 * 60 + diff.seconds
    #         if local.date() == e.begin.date() and total_seconds <= 0:
    #             continue
    #         elif local.date() == e.begin.date() and total_seconds > 0:
    #             return "<s>{} has {}</s><s>Today at {}.</s>".format(name, e.name, hour_phrase(e.begin.time()))
    #         else:
    #             return "<s>{} has nothing today but {}</s><s>{} at {}</s>".format(name, e.name, day_phrase(diff.days), hour_phrase(e.begin.time()))
    #         break


dave_outlook_url = 'https://outlook.office365.com/owa/calendar/9fdc674437014c51ad95fc333f86191c@phishme.com/fd9fe1a7084b4e21a388ae20350dce402738212644810146109/calendar.ics'
#dave_google_url = 'https://calendar.google.com/calendar/ical/beardrd%40gmail.com/private-0c5e6657f636fb0942680bc6ab796a4b/basic.ics'
#janet_google_url = 'https://calendar.google.com/calendar/ical/aukemt%40gmail.com/private-d982a26fb9f516bf53352ef80a4951f6/basic.ics'

#jg = get_string(janet_google_url, "Janet")
#dg = get_string(dave_google_url, "Dave")
pm = get_string(dave_outlook_url, "Fish Me")

print ("s:m:<speak>{}</speak>".format(pm))