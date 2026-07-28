#!/usr/bin/env python3
"""
Script que consulta o clima atual de uma cidade usando a API pública
Open-Meteo (https://open-meteo.com) - gratuita e sem necessidade de API key.
"""

import sys
import requests

GEOCODING_URL = "https://geocoding-api.open-meteo.com/v1/search"
FORECAST_URL = "https://api.open-meteo.com/v1/forecast"

# Mapeamento dos códigos de clima (WMO) para descrições em português
WEATHER_CODES = {
    0: "Céu limpo ☀️",
    1: "Poucas nuvens 🌤️",
    2: "Parcialmente nublado ⛅",
    3: "Nublado ☁️",
    45: "Neblina 🌫️",
    48: "Neblina com geada 🌫️",
    51: "Garoa leve 🌦️",
    53: "Garoa moderada 🌦️",
    55: "Garoa forte 🌧️",
    61: "Chuva leve 🌧️",
    63: "Chuva moderada 🌧️",
    65: "Chuva forte 🌧️",
    71: "Neve leve 🌨️",
    73: "Neve moderada 🌨️",
    75: "Neve forte 🌨️",
    80: "Pancadas de chuva leves 🌦️",
    81: "Pancadas de chuva moderadas 🌧️",
    82: "Pancadas de chuva violentas ⛈️",
    95: "Tempestade ⛈️",
    96: "Tempestade com granizo leve ⛈️",
    99: "Tempestade com granizo forte ⛈️",
}


def buscar_coordenadas(cidade: str):
    """Converte o nome de uma cidade em latitude/longitude."""
    params = {"name": cidade, "count": 1, "language": "pt", "format": "json"}
    resposta = requests.get(GEOCODING_URL, params=params, timeout=10)
    resposta.raise_for_status()
    dados = resposta.json()

    if not dados.get("results"):
        return None

    local = dados["results"][0]
    return {
        "nome": local["name"],
        "pais": local.get("country", ""),
        "lat": local["latitude"],
        "lon": local["longitude"],
    }


def buscar_clima(lat: float, lon: float):
    """Busca o clima atual para as coordenadas informadas."""
    params = {
        "latitude": lat,
        "longitude": lon,
        "current_weather": True,
        "timezone": "auto",
    }
    resposta = requests.get(FORECAST_URL, params=params, timeout=10)
    resposta.raise_for_status()
    return resposta.json()["current_weather"]


def exibir_clima(local: dict, clima: dict):
    """Imprime o resultado formatado no terminal."""
    descricao = WEATHER_CODES.get(clima["weathercode"], "Condição desconhecida")
    largura = 40

    print("=" * largura)
    print(f"  Clima em {local['nome']}, {local['pais']}".center(largura))
    print("=" * largura)
    print(f" Condição........: {descricao}")
    print(f" Temperatura......: {clima['temperature']} °C")
    print(f" Vento............: {clima['windspeed']} km/h")
    print(f" Direção do vento.: {clima['winddirection']}°")
    print(f" Horário local....: {clima['time']}")
    print("=" * largura)

#funcao pricipal
def main():
    if len(sys.argv) > 1:
        cidade = " ".join(sys.argv[1:])
    else:
        cidade = input("Digite o nome da cidade: ").strip()

    if not cidade:
        print("Nenhuma cidade informada.")
        sys.exit(1)

    try:
        local = buscar_coordenadas(cidade)
        if local is None:
            print(f"Cidade '{cidade}' não encontrada.")
            sys.exit(1)

        clima = buscar_clima(local["lat"], local["lon"])
        exibir_clima(local, clima)

    except requests.exceptions.RequestException as erro:
        print(f"Erro ao consultar a API: {erro}")
        sys.exit(1)


if __name__ == "__main__":
    main()
