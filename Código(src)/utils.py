import locale
from deep_translator import GoogleTranslator
from datetime import datetime

locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')
translator = GoogleTranslator(source='en', target='es')

def convertir_volumen(volumen_str):
    print(f"[DEBUG] Convirtiendo volumen: '{volumen_str}'")
    if not volumen_str or volumen_str == "-":
        print(f"[DEBUG] Valor vacío o '-' detectado, devolviendo None")
        return None
    volumen_str = volumen_str.replace(".", "")
    if "M" in volumen_str:
        volumen_str = volumen_str.replace("M", "") + "0000"
        print(f"[DEBUG] Detectado 'M', nuevo valor: '{volumen_str}'")
    elif "B" in volumen_str:
        volumen_str = volumen_str.replace("B", "") + "0000000"
        print(f"[DEBUG] Detectado 'B', nuevo valor: '{volumen_str}'")
    elif "K" in volumen_str:
        volumen_str = volumen_str.replace("K", "") + "0"
        print(f"[DEBUG] Detectado 'K', nuevo valor: '{volumen_str}'")
    try:
        resultado = locale.format_string("%d", int(volumen_str), grouping=True)
        print(f"[DEBUG] Convertido a: '{resultado}'")
        return resultado
    except ValueError:
        print(f"[DEBUG] ValueError, devolviendo None (original: '{volumen_str}')")
        return None

def traducir_texto(texto):
    return translator.translate(texto)

def obtener_fecha_actual():
    return datetime.today().date()