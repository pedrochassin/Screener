import locale
from deep_translator import GoogleTranslator
from datetime import datetime

locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')
translator = GoogleTranslator(source='en', target='es')

def convertir_volumen(volumen_str):
    volumen_str = volumen_str.replace(".", "")
    if "M" in volumen_str:
        volumen_str = volumen_str.replace("M", "") + "0000"
    elif "B" in volumen_str:
        volumen_str = volumen_str.replace("B", "") + "0000000"
    elif "K" in volumen_str:
        volumen_str = volumen_str.replace("K", "") + "0"
    try:
        return locale.format_string("%d", int(volumen_str), grouping=True)
    except ValueError:
        return volumen_str

def traducir_texto(texto):
    return translator.translate(texto)

def obtener_fecha_actual():
    return datetime.today().date()