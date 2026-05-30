"""
Scrape logos das pizzarias via Google Places API.
Uso: python scrape_logos.py --api-key SUA_CHAVE --start 16 --end 100
"""

import argparse
import csv
import os
import time
import requests


def search_place(query, api_key):
    url = "https://maps.googleapis.com/maps/api/place/textsearch/json"
    resp = requests.get(url, params={"query": query, "key": api_key})
    resp.raise_for_status()
    data = resp.json()
    if data["status"] == "OK" and data["results"]:
        return data["results"][0]
    return None


def get_photo(photo_ref, api_key, max_width=400):
    url = "https://maps.googleapis.com/maps/api/place/photo"
    resp = requests.get(url, params={
        "photoreference": photo_ref,
        "maxwidth": max_width,
        "key": api_key
    })
    resp.raise_for_status()
    return resp.content


def main():
    parser = argparse.ArgumentParser(description="Scrape logos de pizzarias via Google Maps")
    parser.add_argument("--api-key", required=True, help="Google Places API key")
    parser.add_argument("--input", default="../data/enderecos.csv", help="CSV com as pizzarias")
    parser.add_argument("--output", default="../logos", help="Pasta de saida")
    parser.add_argument("--start", type=int, default=16, help="Posicao inicial (inclusive)")
    parser.add_argument("--end", type=int, default=100, help="Posicao final (inclusive)")
    args = parser.parse_args()

    os.makedirs(args.output, exist_ok=True)

    with open(args.input, encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter=";")
        pizzarias = [row for row in reader if args.start <= int(row["Posição"]) <= args.end]

    print(f"Processando {len(pizzarias)} pizzarias (posicoes {args.start} a {args.end})...")

    found = 0
    skipped = 0

    for row in pizzarias:
        pos = row["Posição"]
        nome = row["Pizzaria"]
        endereco = row["Endereço"]
        query = f"{nome} pizzaria {endereco} São Paulo"

        print(f"[{pos}] Buscando: {nome}...", end=" ")

        place = search_place(query, args.api_key)
        if not place or "photos" not in place:
            print("SEM FOTO")
            skipped += 1
            time.sleep(1)
            continue

        photo_ref = place["photos"][0]["photo_reference"]
        filename = f"{pos}-{nome.replace(' ', '_').replace('/', '-')}.jpg"
        filepath = os.path.join(args.output, filename)

        img = get_photo(photo_ref, args.api_key)
        with open(filepath, "wb") as f:
            f.write(img)

        print(f"OK -> {filename}")
        found += 1
        time.sleep(1)

    print(f"\nFinalizado: {found} logos baixados, {skipped} sem foto")


if __name__ == "__main__":
    main()
