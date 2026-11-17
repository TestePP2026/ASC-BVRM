# Site ASC/BVRM Basquetebol

Site estático (HTML, CSS e JavaScript simples). Os jogos vêm da FPB; tudo o resto edita-se no painel de administração.

## Pôr online (grátis)
1. Criar um repositório no GitHub e enviar todos os ficheiros desta pasta.
2. Settings > Pages > "Deploy from a branch" > `main` / `(root)`.
3. Settings > Actions > General > Workflow permissions > "Read and write permissions".
4. Em `admin/config.yml`, trocar `O-TEU-UTILIZADOR/asc-bvrm-site` pelo repositório real.

## Administração
Abrir `O-SEU-SITE/admin/`, entrar no GitHub (com um token de acesso fino, permissão "Contents: read and write" só neste repositório) e editar:
- **Jogos**: corrigir ou esconder um jogo da FPB (pelo ID) ou acrescentar jogos próprios. As alterações têm prioridade sobre os dados da FPB e não se perdem nas atualizações.
- **Equipas e plantéis**: escalões, treinadores, fotografia, jogadores.
- **Dados do clube**: morada, contactos, redes sociais.
Cada gravação cria um commit e o site atualiza em cerca de um minuto.

## Atualização automática
`.github/workflows/update.yml` corre `scripts/scrape.py` 4 vezes por dia e grava `data/games.json`. Também se pode correr à mão em Actions > Atualizar jogos da FPB > Run workflow. Se a FPB mudar o formato das páginas, o passo falha e o GitHub avisa por email; o site continua com os últimos dados.

## Plantéis
`scripts/rosters.py` abre a página de cada equipa na FPB (campo "Número da equipa na FPB" no painel) com um navegador automático e grava `data/rosters.json`. No site, o plantel manual de uma equipa (se existir) substitui o da FPB. "Não mostrar o plantel no site" esconde-o por completo (útil para escalões de formação). As fotografias dos atletas não são copiadas.
