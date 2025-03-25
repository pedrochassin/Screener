import schedule
import time
import datetime
from archivo.main import buscar_tickers

def es_dia_habil():
    """Verifica si hoy es un día hábil (lunes a viernes)."""
    return datetime.datetime.today().weekday() < 5

def programar_busquedas():
    """Programa las búsquedas automáticas en días hábiles."""
    schedule.every().day.at("07:30").do(lambda: buscar_tickers() if es_dia_habil() else None)
    schedule.every().day.at("09:00").do(lambda: buscar_tickers() if es_dia_habil() else None)
    schedule.every().day.at("16:00").do(lambda: buscar_tickers() if es_dia_habil() else None)

if __name__ == "__main__":
    programar_busquedas()
    print("Scheduler iniciado. Esperando horarios programados...")
    while True:
        schedule.run_pending()
        time.sleep(60)  # Verifica cada minuto