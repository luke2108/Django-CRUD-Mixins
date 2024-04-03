from jeraconv import jeraconv


# This helper is used for convert West calendar to Japanese calendar.
# Used jeraconv: https://pypi.org/project/jeraconv/
def convert_west_to_jp(iso_time):
    w2j = jeraconv.W2J()
    try:
        return w2j.convert(iso_time.year, iso_time.month, iso_time.day)
    except Exception:
        return None
