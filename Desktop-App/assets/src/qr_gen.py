import qrcode

def filter(data):
    text = ''
    for char in data:
        if char in ['<','>',':','/','|','?','*','"','\'', '\\']:
            char = ''
        text += char
    return text


def gen(data):

    # QR code settings
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=10,
        border=4,
        )
    qr.add_data(data.lower())  # encode data
    qr.make(fit=True)  # make qr

    image = qr.make_image(fill_color="black", back_color="white").convert('RGB')  # colour settings

    path = "qr_codes/" + data.lower()[:30] + ".png"
    try:
        image.save(path)
    except:
        pass
