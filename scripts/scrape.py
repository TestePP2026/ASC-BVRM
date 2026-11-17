"""Lê calendário e resultados do clube no site da FPB e atualiza data/games.json."""
import datetime as dt, json, re, sys
from pathlib import Path
import requests
from bs4 import BeautifulSoup

CLUBE = 43
OUT = Path(__file__).resolve().parent.parent / "data" / "games.json"
MESES = {m: i + 1 for i, m in enumerate("JAN FEV MAR ABR MAI JUN JUL AGO SET OUT NOV DEZ".split())}
HEAD = {"User-Agent": "Mozilla/5.0 (compatible; site-ASC-BVRM/1.0)"}


def nome(txt):
    """A FPB repete o nome da equipa (logótipo, texto, título): fica só uma vez."""
    w = re.sub(r"^Logo\s+", "", txt.strip()).split()
    n = len(w)
    for k in (3, 2):
        if n % k == 0 and w[: n // k] * k == w:
            return " ".join(w[: n // k])
    return " ".join(w)


def parse(html):
    data, jogos = None, []
    for el in BeautifulSoup(html, "html.parser").find_all(["h3", "a"]):
        if el.name == "h3":
            m = re.match(r"(\d{1,2})\s+([A-Za-z]{3})\w*\s+(\d{4})", el.get_text(" ", strip=True))
            if m and m[2].upper() in MESES:
                data = dt.date(int(m[3]), MESES[m[2].upper()], int(m[1])).isoformat()
            continue
        href, strong = el.get("href", ""), el.find("strong")
        if "ficha-de-jogo" not in href or not strong or not data:
            continue
        local = strong.get_text(" ", strip=True)
        antes, _, depois = el.get_text(" ", strip=True).partition(local)
        hora = re.search(r"(\d{1,2})H(\d{2})", antes)
        placar = re.search(r"(\d+)\s*-\s*(\d+)", antes)
        sep = hora or placar
        if not sep:
            continue
        venue, _, city = local.rpartition(",")
        jogos.append({
            "id": int(re.search(r"internalID=(\d+)", href)[1]),
            "date": data,
            "time": f"{int(hora[1]):02d}:{hora[2]}" if hora else "",
            "home": nome(antes[: sep.start()]),
            "away": nome(antes[sep.end():]),
            "venue": venue.strip() or city.strip(),
            "city": city.strip() if venue else "",
            "comp": depois.strip(),
            "hs": int(placar[1]) if placar and not hora else None,
            "as": int(placar[2]) if placar and not hora else None,
        })
    return jogos


def main():
    novos = {}
    for pagina in ("calendario", "resultados"):
        try:
            r = requests.get(f"https://www.fpb.pt/{pagina}/clube_{CLUBE}", headers=HEAD, timeout=30)
            r.raise_for_status()
            novos.update({j["id"]: j for j in parse(r.text)})
        except Exception as e:
            print(f"Aviso ({pagina}): {e}", file=sys.stderr)
    if not novos:
        sys.exit("Nenhum jogo lido da FPB: ficheiro mantido.")
    antigo = json.loads(OUT.read_text("utf-8")) if OUT.exists() else {"games": []}
    todos = {j["id"]: j for j in antigo.get("games", [])}
    todos.update(novos)
    lista = sorted(todos.values(), key=lambda j: (j["date"], j["time"]))
    if lista == antigo.get("games"):
        return print("Sem alterações.")
    agora = dt.datetime.now(dt.timezone.utc).isoformat(timespec="minutes")
    OUT.write_text(json.dumps({"updated": agora, "games": lista}, ensure_ascii=False, indent=1), "utf-8")
    print(f"{len(lista)} jogos gravados.")


if __name__ == "__main__":
    main()
