# https://www.ietf.org/rfc/rfc5545.txt

from datetime import datetime, timezone

DATE_FORMAT = '%Y%m%dT%H%M%SZ'

class Event:
    def __init__(
        self, 
        uid: str, 
        name: str, 
        start_date: datetime, 
        end_date: datetime
    ):
        self.uid = uid
        self.name = name
        self.start_date = start_date
        self.end_date = end_date
        self.create_date = datetime.utcnow()

    @classmethod
    def from_ical(cls, ical: str):
        event = cls('', '', datetime.now(), datetime.now())
        uid, name, start_date, end_date = 'UID:', 'SUMMARY:', 'DTSTART:', 'DTEND:'

        for i in ical.split('\n'):
            if i.startswith(uid):
                event.uid = i[len(uid):]
            elif i.startswith(name):
                event.name = i[len(name):]
            elif i.startswith(start_date):
                event.start_date = datetime.strptime(i[len(start_date):], DATE_FORMAT)
            elif i.startswith(end_date):
                event.end_date = datetime.strptime(i[len(end_date):], DATE_FORMAT)

        return event

    def generate_ical(self):
        lines = [
            "BEGIN:VEVENT",
            "UID:" + self.uid,
            "SUMMARY:" + self.name,
            "DTSTAMP:" + self.create_date.strftime(DATE_FORMAT),
            "DTSTART:" + self.start_date.strftime(DATE_FORMAT),
            "DTEND:" + self.end_date.strftime(DATE_FORMAT),
            "END:VEVENT",
        ]
        return '\n'.join(lines)


class Calendar:
    def __init__(self):
        self.events = {}

    @classmethod
    def from_ical(cls, ical):
        calendar = cls()

        next_event = ical.find('BEGIN:VEVENT')
        while next_event != -1:
            end_event = ical.find('END:VEVENT', next_event)
            event = Event.from_ical(ical[next_event:end_event])
            calendar.add_event(event)
            next_event = ical.find('BEGIN:VEVENT', next_event + 1)
        
        return calendar


    def add_event(self, event: Event):
        self.events[event.start_date] = event

    def generate_ical(self):
        lines = [
            "BEGIN:VCALENDAR",
            "VERSION:2.0",
            "PRODID:spadiff",
            "CALSCALE:GREGORIAN",
            "METHOD:PUBLISH",
        ]
        for event in self.events.values():
            lines.append(event.generate_ical())
        lines.append("END:VCALENDAR")
        return '\n'.join(lines)
