from datetime import date, datetime, timedelta


def generate_slots(start, duration, count):
    start = datetime.strptime(start, "%H:%M")
    return list((start + timedelta(minutes=(duration*x))).strftime("%H:%M")
                for x in range(count))
