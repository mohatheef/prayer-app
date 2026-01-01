from hijri_converter import Gregorian

def gregorian_to_hijri(d):
    h = Gregorian(d.year, d.month, d.day).to_hijri()
    return f"{h.day:02d}-{h.month:02d}-{h.year}"
