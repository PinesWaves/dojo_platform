import base64
from io import BytesIO
import qrcode
from django.core.cache import cache
from datetime import date, timedelta


def generate_qr_file(data):
    cache_key = f"qr_code_file_{data}"
    cached_qr = cache.get(cache_key)
    if cached_qr:
        return BytesIO(base64.b64decode(cached_qr))

    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=3,
    )
    qr.add_data(data)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")
    buffered = BytesIO()
    img.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode('utf-8')

    cache.set(cache_key, img_str, timeout=3600)
    buffered.seek(0)
    return buffered


def get_qr_base64(data):
    buffer = generate_qr_file(data)
    img_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
    return f"data:image/png;base64,{img_base64}"


def get_next_closest_day(st_date: date, week_day: int) -> date:
    """Get the next closest week day from a given date.
    Args:
        st_date (date): The starting date.
        week_day (int): The target day of the week (0=Monday, 6=Sunday).
    Returns:
        date: The next closest date that falls on the specified day of the week.
    """
    days_ahead = (week_day - st_date.weekday() + 7) % 7
    days_ahead = days_ahead if days_ahead != 0 else 7
    closest_date = st_date + timedelta(days=days_ahead)
    return closest_date
