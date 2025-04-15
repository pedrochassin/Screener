import sys
import traceback
from datetime import datetime, timedelta
from collections import defaultdict

print(f"Python version: {sys.version}")
try:
    from schwab.auth import easy_client
    from schwab.client import Client
    import asyncio
    import os
except ImportError as e:
    print(f"Error al importar módulos: {e}")
    print("Traceback completo:")
    traceback.print_exc()
    print("Posible problema con la versión de httpx. Intenta: pip install httpx==0.23.0")
    sys.exit(1)

# Configura tus credenciales
API_KEY = 'TU_CLAVE_API'  # Reemplaza con tu clave API
APP_SECRET = 'TU_SECRETO_API'  # Reemplaza con tu secreto API
CALLBACK_URI = 'https://127.0.0.1'  # Ajusta según el portal
TOKEN_PATH = 'token.json'  # Archivo para almacenar el token

async def main():
    try:
        # Autenticación
        client = easy_client(
            API_KEY,
            APP_SECRET,
            CALLBACK_URI,
            TOKEN_PATH
        )

        # Define el ticker
        ticker = 'AAPL'

        # Intento 1: Usar get_price_history con frecuencia más fina
        print("Intentando con get_price_history...")
        price_history = client.get_price_history(
            symbol=ticker,
            period_type=Client.PriceHistory.PeriodType.DAY,
            period=Client.PriceHistory.Period.ONE_DAY,
            frequency_type=Client.PriceHistory.FrequencyType.MINUTE,
            frequency=Client.PriceHistory.Frequency.EVERY_MINUTE  # Cambiado a cada minuto
        )

        # Procesa la respuesta
        if price_history.status_code == 200:
            candles = price_history.json().get('candles', [])
            print(f"Datos recibidos (candles): {len(candles)} intervalos")
            if candles:
                # Suma el volumen de todos los intervalos de hoy
                today = datetime.now().strftime('%Y-%m-%d')
                total_volume = 0
                for candle in candles:
                    candle_date = datetime.fromtimestamp(candle['datetime'] / 1000).strftime('%Y-%m-%d')
                    if candle_date == today:
                        total_volume += candle['volume']
                
                if total_volume > 0:
                    print(f"Volumen total de {ticker} el {today} hasta ahora (get_price_history): {total_volume} acciones")
                else:
                    print(f"No se encontraron datos de volumen para {ticker} el {today} en get_price_history")
            else:
                print(f"No se encontraron datos para {ticker} en get_price_history")
        else:
            print(f"Error en get_price_history: {price_history.status_code}")
            print(f"Detalles del error: {price_history.text}")

        # Intento 2: Usar get_quotes para volumen en tiempo real
        print("\nIntentando con get_quotes...")
        quote_response = client.get_quotes(symbols=[ticker])

        if quote_response.status_code == 200:
            quote_data = quote_response.json()
            if ticker in quote_data:
                quote = quote_data[ticker]
                cumulative_volume = quote.get('quote', {}).get('totalVolume', 0)
                if cumulative_volume > 0:
                    today = datetime.now().strftime('%Y-%m-%d')
                    print(f"Volumen total de {ticker} el {today} hasta ahora (get_quotes): {cumulative_volume} acciones")
                else:
                    print(f"No se encontró volumen en get_quotes para {ticker}")
            else:
                print(f"No se encontraron datos para {ticker} en get_quotes")
        else:
            print(f"Error en get_quotes: {quote_response.status_code}")
            print(f"Detalles del error: {quote_response.text}")
            
    except Exception as e:
        print(f"Error al obtener datos: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        print(f"Error al ejecutar el script: {e}")
        traceback.print_exc()