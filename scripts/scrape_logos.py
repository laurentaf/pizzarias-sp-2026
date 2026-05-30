"""
Scrape logos das pizzarias via Google Images (sem API key).
Uso: python scrape_logos.py --start 16 --end 100
"""

import argparse
import csv
import os
import re
import time
from urllib.parse import quote_plus

import requests
from bs4 import BeautifulSoup


HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}


def search_google_images(query):
    url = f"https://www.google.com/search?q={quote_plus(query)}&tbm=isch"
    resp = requests.get(url, headers=HEADERS, timeout=10)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")
    img_tags = soup.find_all("img")
    urls = []
    for img in img_tags:
        src = img.get("src") or img.get("data-src") or ""
        if src.startswith("http") and "google" not in src and "gstatic" not in src:
            urls.append(src)
    return urls[0] if urls else None


def download_image(url, filepath):
    resp = requests.get(url, headers=HEADERS, timeout=10, stream=True)
    resp.raise_for_status()
    with open(filepath, "wb") as f:
        for chunk in resp.iter_content(8192):
            f.write(chunk)


def main():
    parser = argparse.ArgumentParser(description="Scrape logos de pizzarias (sem API key)")
    parser.add_argument("--input", default="../data/enderecos.csv")
    parser.add_argument("--output", default="../logos")
    parser.add_argument("--start", type=int, default=16)
    parser.add_argument("--end", type=int, default=100)
    args = parser.parse_args()

    os.makedirs(args.output, exist_ok=True)

    with open(args.input, encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter=";")
        pizzarias = [row for row in reader if args.start <= int(row["Posição"]) <= args.end]

    print(f"Processando {len(pizzarias)} pizzarias (posicoes {args.start} a {args.end})...\n")

    found = 0
    skipped = 0

    for row in pizzarias:
        pos = row["Posição"]
        nome = row["Pizzaria"]
        query = f"{nome} pizzaria logo"

        print(f"[{pos:>3}] {nome}... ", end="", flush=True)

        try:
            img_url = search_google_images(query)
            if not img_url:
                print("SEM IMAGEM")
                skipped += 1
                time.sleep(2)
                continue

            filename = f"{pos}-{nome.replace(' ', '_').replace('/', '-')}.jpg"
            filepath = os.path.join(args.output, filename)
            download_image(img_url, filepath)
            print(f"OK -> {filename}")
            found += 1
        except Exception as e:
            print(f"ERRO: {e}")
            skipped += 1

        time.sleep(2)

    print(f"\nFinalizado: {found} logos baixados, {skipped} sem imagem")


if __name__ == "__main__":
    main()
