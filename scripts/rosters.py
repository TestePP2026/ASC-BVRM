"""Lê os plantéis das equipas do clube na FPB e grava data/rosters.json.

A FPB carrega o plantel por JavaScript depois de abrir a página, por isso
usamos um navegador automático (Playwright) e esperamos que a lista apareça.
"""
import datetime as dt, json, re, sys
from pathlib import Path
from bs4 import BeautifulSoup

DATA = Path(__file__).resolve().parent.parent / "data"


def jogadores(html):
    out = []
    for p in BeautifulSoup(html, "html.parser").select(".roster__player"):
        nome = p.select_one(".roster__player__header__heading")
        if not nome:
            continue
        jn = p.select_one(".roster__player__header_jnumber")
        num = "".join(jn.find_all(string=True, recursive=False)).strip() if jn else ""
        pos = p.select_one(".roster__player__header_position")
        pos = " / ".join(x.strip().capitalize() for x in pos.get_text().split("/") if x.strip()) if pos else ""
        link = p.find("a", href=re.compile(r"/atletas/\d+"))
        out.append({
            "number": int(num) if num.isdigit() else None,
            "name": nome.get_text(strip=True),
            "position": pos,
            "fpb_id": int(re.search(r"(\d+)", link["href"])[1]) if link else None,
        })
    return out


def main():
    from playwright.sync_api import sync_playwright, TimeoutError as PWTimeout

    equipas = json.loads((DATA / "teams.json").read_text("utf-8"))["teams"]
    ficheiro = DATA / "rosters.json"
    antigo = json.loads(ficheiro.read_text("utf-8")) if ficheiro.exists() else {"teams": {}}
    novos, falhas, tentadas = dict(antigo["teams"]), [], 0
    with sync_playwright() as pw:
        browser = pw.chromium.launch()
        page = browser.new_page()
        for t in equipas:
            fid = t.get("fpb_id")
            if not fid:
                continue
            tentadas += 1
            try:
                page.goto(f"https://www.fpb.pt/equipa/equipa_{fid}/", wait_until="domcontentloaded", timeout=45000)
                page.wait_for_selector(".roster__player", timeout=30000)
                lista = jogadores(page.content())
                if lista:
                    novos[str(fid)] = lista
                    print(f"{t['name']}: {len(lista)} jogadores")
            except PWTimeout:
                falhas.append(t["name"])
                print(f"Aviso: sem plantel lido para {t['name']} (equipa {fid}); mantém-se o anterior.", file=sys.stderr)
        browser.close()
    if tentadas and len(falhas) == tentadas:
        sys.exit("Nenhum plantel lido da FPB: ficheiro mantido.")
    if novos == antigo["teams"]:
        return print("Sem alterações.")
    agora = dt.datetime.now(dt.timezone.utc).isoformat(timespec="minutes")
    ficheiro.write_text(json.dumps({"updated": agora, "teams": novos}, ensure_ascii=False, indent=1), "utf-8")


if __name__ == "__main__":
    main()
