import base64
from io import BytesIO
import qrcode
from django.core.cache import cache


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
