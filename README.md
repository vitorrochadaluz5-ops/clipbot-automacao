### ClipBot Automação

Projeto base para controle local de automação com login do painel e perfis separador por cliente.

## Requisitos

- Python 3.11+
- Git
- Navegador Chrome/Chromium

## Instalação

```bash
python -m venv .venv
. .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python -m playwright install chromium
```

## Rodar

```bash
python app.py
```

Acesse:

- http://localhost:8000/login
- Crie um usuário
- Faça login
- Cadastre um cliente
- Conecte o perfil de navegador
- Depois você pode adaptar a rotina de upload e publicar no TikTok

## Importante

- Não grave cookies do TikTok no repositório
- Mantenha a pasta `profiles/` fora de ambientes compartilhados
- O sistema de login do painel é separado da conta do cliente no TikTok

## Estrutura

- `app.py` — app web principal
- `database.py` — banco SQLite e tabelas
- `browser_manager.py` — perfil do navegador por cliente
- `templates/` — telas de login e dashboard
- `static/` — CSS

