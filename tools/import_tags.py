#!/usr/bin/env python3
"""
import_tags.py — Tague les 1972 documents Vertex AI Search avec source_level (1–4)
en lisant le CSV généré par export_corpus.py.

Usage :
  python tools/import_tags.py                          # lit corpus_documents.csv
  python tools/import_tags.py --csv mon_fichier.csv    # CSV custom
  python tools/import_tags.py --dry-run                # simulation sans écriture

Prérequis :
  pip install google-auth requests
  gcloud auth application-default login

Niveaux de source :
  1 — Primaires  : Talmud Bavli, Mishna, Rambam, Tur, Tanach
  2 — Codificateurs majeurs : Choulhan Aroukh, Mishna Beroura, Responsa
  3 — Acharonim  : Ben Ich Haï, Yalkout Yossef, Halakha générale
  4 — Thématiques / Hassidout / Modernes
"""

import csv
import sys
import time
import argparse
from collections import Counter, defaultdict

import google.auth
import google.auth.transport.requests
import requests

# ── Config ────────────────────────────────────────────────
PROJECT_NUMBER = "217121855341"
DATASTORE_ID   = "corpus-sifrey-global_1772101356063"

BASE_URL = (
    f"https://discoveryengine.googleapis.com/v1"
    f"/projects/{PROJECT_NUMBER}/locations/global"
    f"/collections/default_collection"
    f"/dataStores/{DATASTORE_ID}"
    f"/branches/default_branch/documents"
)

# ── Hiérarchie des sources ─────────────────────────────────
# Niveau 1 : sources primaires — Talmud, Rambam, Tur, Tanach, Mishna
# Niveau 2 : codificateurs majeurs — Choulhan Aroukh, Mishna Beroura, Responsa
# Niveau 3 : Acharonim classiques — Ben Ich Haï, Yalkout Yossef
# Niveau 4 : thématiques, Hassidout, Moussar, modernes

SOURCE_LEVELS: dict[str, int] = {
    # ── NIVEAU 1 — Sources primaires ──────────────────────
    "Talmud Bavli":        1,
    "Mishna":              1,
    "Mishna - Kodshim":    1,
    "Mishna - Taharot":    1,
    "Rambam":              1,
    "Tur":                 1,
    "Tanach":              1,

    # ── NIVEAU 2 — Codificateurs majeurs ──────────────────
    "Choulhan Aroukh":     2,
    "Mishna Beroura":      2,
    "Responsa":            2,          # שו"ת

    # ── NIVEAU 3 — Acharonim classiques ───────────────────
    "Ben Ich Haï":         3,
    "Yalkout Yossef":      3,
    "Halakha":             3,
    "Sifrey Halacha":      3,
    "Parashat Shavua":     3,

    # ── NIVEAU 4 — Thématiques / Hassidout / Modernes ─────
    "Tanya":               4,
    "Zohar":               4,
    "Likoutey Moharan":    4,
    "Likoutey Halachot":   4,
    "Hassidout":           4,
    "Kabbalah":            4,
    "Moussar":             4,
    "Chabbat":             4,
    "Kashrout":            4,
    "Nashim":              4,
    "Pessah":              4,
    "Tefila":              4,
    "Chalom Bait":         4,
}

LEVEL_LABELS = {
    1: "Primaire (Talmud / Rambam / Tur)",
    2: "Codificateur (ShA / MB / Responsa)",
    3: "Acharonim classiques",
    4: "Thématique / Hassidout",
}


def get_access_token() -> str:
    creds, _ = google.auth.default(
        scopes=["https://www.googleapis.com/auth/cloud-platform"]
    )
    req = google.auth.transport.requests.Request()
    creds.refresh(req)
    return creds.token


def patch_document(doc_id: str, source_level: int, category: str,
                   token: str, dry_run: bool) -> bool:
    """Patche un document Vertex avec source_level + source_category."""
    if dry_run:
        return True

    url = f"{BASE_URL}/{doc_id}?updateMask=structData"
    payload = {
        "structData": {
            "source_level":    str(source_level),
            "source_category": category,
        }
    }
    resp = requests.patch(
        url,
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        },
        json=payload,
        timeout=30,
    )
    return resp.ok


def load_csv(csv_path: str) -> list[dict]:
    rows = []
    with open(csv_path, newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(row)
    return rows


def main():
    parser = argparse.ArgumentParser(
        description="Tague les documents Vertex AI Search avec source_level"
    )
    parser.add_argument("--csv",     default="corpus_documents.csv",
                        help="CSV généré par export_corpus.py")
    parser.add_argument("--dry-run", action="store_true",
                        help="Simulation : affiche les actions sans écrire")
    parser.add_argument("--level",   type=int, choices=[1, 2, 3, 4],
                        help="Ne traiter que ce niveau (debug)")
    args = parser.parse_args()

    # ── Chargement CSV ────────────────────────────────────
    try:
        rows = load_csv(args.csv)
    except FileNotFoundError:
        print(f"[!] Fichier introuvable : {args.csv}")
        print("    → Lance d'abord : python tools/export_corpus.py")
        sys.exit(1)

    print(f"[*] {len(rows)} documents chargés depuis {args.csv}")

    # Prévisualisation des niveaux
    preview = defaultdict(list)
    unknowns = []
    for row in rows:
        cat = row.get("categorie", "Autre")
        lvl = SOURCE_LEVELS.get(cat)
        if lvl:
            preview[lvl].append(cat)
        else:
            unknowns.append(cat)

    print("\n[*] Répartition par niveau :")
    for lvl in sorted(preview):
        cats = Counter(preview[lvl])
        total = sum(cats.values())
        print(f"  Niveau {lvl} — {LEVEL_LABELS[lvl]}")
        for cat, count in sorted(cats.items(), key=lambda x: -x[1]):
            print(f"      {count:4d}  {cat}")
        print(f"      ──── total : {total}")

    if unknowns:
        unk_counter = Counter(unknowns)
        print(f"\n[?] {len(unknowns)} documents sans niveau assigné :")
        for cat, count in sorted(unk_counter.items(), key=lambda x: -x[1]):
            print(f"      {count:4d}  {cat!r}  → niveau 4 par défaut")

    if args.dry_run:
        print("\n[DRY-RUN] Aucune écriture. Ajoute --help pour les options.")
        return

    # ── Authentification ──────────────────────────────────
    print("\n[*] Authentification GCP...")
    try:
        token = get_access_token()
    except Exception as e:
        print(f"[!] Erreur auth : {e}")
        print("    → Exécute : gcloud auth application-default login")
        sys.exit(1)

    # ── Patch des documents ───────────────────────────────
    ok = err = skip = 0
    token_refresh_every = 200   # renouvelle le token toutes les 200 requêtes
    total = len(rows)

    print(f"\n[*] Mise à jour de {total} documents...")
    for i, row in enumerate(rows, 1):
        doc_id   = row.get("id", "").strip()
        category = row.get("categorie", "Autre").strip()
        level    = SOURCE_LEVELS.get(category, 4)  # défaut : 4

        if args.level and level != args.level:
            skip += 1
            continue

        if not doc_id:
            skip += 1
            continue

        # Renouvellement token périodique
        if i % token_refresh_every == 0:
            try:
                token = get_access_token()
            except Exception:
                pass

        success = patch_document(doc_id, level, category, token, args.dry_run)

        if success:
            ok += 1
        else:
            err += 1

        # Barre de progression
        pct = i / total * 100
        bar = "█" * int(pct / 5) + "░" * (20 - int(pct / 5))
        print(f"  [{bar}] {pct:5.1f}%  ✓{ok}  ✗{err}  skip:{skip}", end="\r")

        time.sleep(0.05)   # ~20 req/s — bien en dessous des quotas Vertex

    print(f"\n\n[✓] Terminé — ✓ {ok} mis à jour  ✗ {err} erreurs  {skip} ignorés")
    if err:
        print("[!] Relance le script pour réessayer les erreurs (idempotent)")


if __name__ == "__main__":
    main()
