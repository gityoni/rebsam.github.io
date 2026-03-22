#!/usr/bin/env python3
"""
export_corpus.py — Exporte les 1972 documents du Vertex AI Search datastore
en CSV avec ID, URI, titre et catégorie auto-détectée.

Usage :
  python export_corpus.py                     # → corpus_documents.csv
  python export_corpus.py --out mon_fichier.csv

Prérequis :
  pip install google-auth requests
  gcloud auth application-default login       # ou GOOGLE_APPLICATION_CREDENTIALS
"""

import csv
import json
import re
import sys
import time
import argparse
import google.auth
import google.auth.transport.requests
import requests

# ── Config ────────────────────────────────────────────────
PROJECT_NUMBER = "217121855341"
DATASTORE_ID   = "corpus-sifrey-global_1772101356063"
PAGE_SIZE      = 100   # max autorisé par l'API

BASE_URL = (
    f"https://discoveryengine.googleapis.com/v1"
    f"/projects/{PROJECT_NUMBER}/locations/global"
    f"/collections/default_collection"
    f"/dataStores/{DATASTORE_ID}"
    f"/branches/default_branch/documents"
)

# ── Catégories déduites du chemin URI ─────────────────────
# Le bucket suit le pattern : gs://rebbesam-data-01/{CATÉGORIE} pdf/{fichier}
# On mappe les dossiers hébreux vers des labels français lisibles
CATEGORY_MAP = {
    "תלמוד בבלי":      "Talmud Bavli",
    "משניות":          "Mishna",
    "משניות קדשים":    "Mishna - Kodshim",
    "משניות טהרות":    "Mishna - Taharot",
    "רמב\"ם":          "Rambam",
    "שולחן ערוך":      "Choulhan Aroukh",
    "משנה ברורה":      "Mishna Beroura",
    "טור":             "Tur",
    "ילקוט יוסף":      "Yalkout Yossef",
    "בן איש חי":       "Ben Ich Haï",
    "תניא":            "Tanya",
    "זוהר":            "Zohar",
    "ליקוטי מוהרן":    "Likoutey Moharan",
    "ליקוטי הלכות":    "Likoutey Halachot",
    "חסידות":          "Hassidout",
    "קבלה":            "Kabbalah",
    "מוסר":            "Moussar",
    "הלכה":            "Halakha",
    "שבת":             "Chabbat",
    "כשרות":           "Kashrout",
    "נשים":            "Nashim",
    "פסח":             "Pessah",
    "תפלה":            "Tefila",
    "תנ\"ך":           "Tanach",
    "תנך":             "Tanach",
    "פרשת שבוע":       "Parashat Shavua",
    "שו\"ת":           "Responsa",
    "Chalom Bait":     "Chalom Bait",
    "Sifrey Halacha":  "Sifrey Halacha",
}

def get_access_token() -> str:
    creds, _ = google.auth.default(
        scopes=["https://www.googleapis.com/auth/cloud-platform"]
    )
    req = google.auth.transport.requests.Request()
    creds.refresh(req)
    return creds.token


def infer_category(uri: str) -> str:
    """Déduit la catégorie depuis le chemin GCS."""
    # gs://rebbesam-data-01/CATÉGORIE pdf/fichier.pdf
    # ou gs://rebbesam-data-01/CATÉGORIE/fichier.pdf
    match = re.search(r'gs://[^/]+/([^/]+?)(?:\s+pdf)?/', uri)
    if not match:
        return "Autre"
    folder = match.group(1).strip()
    # Cherche une correspondance partielle dans CATEGORY_MAP
    for heb, label in CATEGORY_MAP.items():
        if heb in folder:
            return label
    return folder  # retourne le nom du dossier brut si pas mappé


def list_all_documents(token: str) -> list[dict]:
    docs = []
    page_token = None
    page_num = 0

    while True:
        page_num += 1
        params = {"pageSize": PAGE_SIZE}
        if page_token:
            params["pageToken"] = page_token

        resp = requests.get(
            BASE_URL,
            headers={"Authorization": f"Bearer {token}"},
            params=params,
            timeout=30,
        )

        if resp.status_code == 401:
            print("[!] Token expiré — renouvellement...")
            token = get_access_token()
            continue

        if not resp.ok:
            print(f"[!] Erreur API {resp.status_code} : {resp.text[:300]}")
            break

        data = resp.json()
        batch = data.get("documents", [])
        docs.extend(batch)

        print(f"  Page {page_num:3d} — {len(batch):3d} docs récupérés "
              f"(total : {len(docs)})", end="\r")

        page_token = data.get("nextPageToken")
        if not page_token:
            break

        time.sleep(0.1)  # throttle léger

    print()
    return docs


def parse_title(doc: dict) -> str:
    """Extrait le titre depuis jsonData, structData ou le nom du fichier."""
    # structData (format object)
    struct = doc.get("structData", {})
    for field in ("title", "name", "titre", "document_title"):
        if struct.get(field):
            return str(struct[field])

    # jsonData (format JSON string)
    json_data = doc.get("jsonData", "")
    if json_data:
        try:
            obj = json.loads(json_data)
            for field in ("title", "name", "titre"):
                if obj.get(field):
                    return str(obj[field])
        except Exception:
            pass

    # Fallback : nom du fichier depuis l'URI
    uri = doc.get("content", {}).get("uri", "")
    if uri:
        filename = uri.rsplit("/", 1)[-1]
        return re.sub(r'_Partie_\d+', '', filename).replace(".pdf", "").replace(".txt", "").strip()

    return doc.get("id", "")


def export_csv(docs: list[dict], out_path: str) -> None:
    with open(out_path, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f, quoting=csv.QUOTE_ALL)
        writer.writerow(["id", "titre", "categorie", "uri"])

        for doc in docs:
            doc_id  = doc.get("id", "")
            uri     = doc.get("content", {}).get("uri", "")
            titre   = parse_title(doc)
            categorie = infer_category(uri)
            writer.writerow([doc_id, titre, categorie, uri])

    print(f"[✓] {len(docs)} documents exportés → {out_path}")


def main():
    parser = argparse.ArgumentParser(description="Exporte le corpus Vertex AI Search en CSV")
    parser.add_argument("--out", default="corpus_documents.csv", help="Fichier de sortie")
    args = parser.parse_args()

    print(f"[*] Authentification GCP...")
    try:
        token = get_access_token()
    except Exception as e:
        print(f"[!] Erreur auth : {e}")
        print("    → Exécute : gcloud auth application-default login")
        sys.exit(1)

    print(f"[*] Récupération des documents (datastore : {DATASTORE_ID})...")
    docs = list_all_documents(token)
    print(f"[*] {len(docs)} documents récupérés au total")

    if not docs:
        print("[!] Aucun document — vérifie les droits IAM ou l'ID du datastore")
        sys.exit(1)

    export_csv(docs, args.out)

    # Résumé par catégorie
    from collections import Counter
    cats = Counter(infer_category(d.get("content", {}).get("uri", "")) for d in docs)
    print("\n[*] Répartition par catégorie :")
    for cat, count in sorted(cats.items(), key=lambda x: -x[1]):
        print(f"    {count:4d}  {cat}")


if __name__ == "__main__":
    main()
