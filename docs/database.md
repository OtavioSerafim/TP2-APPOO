# Banco de Dados

> Estrutura SQLite usada para registrar jogadores e resultados de partidas.

## Visão Geral
- Arquivo principal: `Database/app.db`.
- Migrações versionadas em `Database/migrations/` (atualmente `1_initial.sql`).
- Script `Database/init_db.py` remove o banco anterior e executa todas as migrações em ordem, respeitando prefixos numéricos.

## Estrutura das Tabelas
| Tabela   | Objetivo                   | Campos principais |
|----------|----------------------------|-------------------|
| `player` | Catálogo de jogadores.     | `id` (PK), `name` (único, texto obrigatório).
| `plays`  | Histórico de partidas.     | `id`, `played_at`, `music_name`, `score`, `player_id` (FK), `errors`, `perfect_hits`, `good_hits`, `bad_hits`.

### Regras Importantes
- `plays.player_id` referencia `player.id` com `ON DELETE CASCADE`, garantindo remoção automática de partidas quando o jogador for apagado.
- `played_at` é armazenado em string ISO (`YYYY-MM-DD HH:MM:SS`).
- Contadores de acerto/erro possuem valor padrão `0` e devem receber inteiros não negativos.

## Rotina `init_db.py`
1. Define caminhos base (`DB_PATH`, `MIGRATIONS_DIR`).
2. Remove `app.db` se existir.
3. Abre conexão SQLite e executa cada migração ordenada pelo prefixo numérico.
4. Exibe mensagem com o caminho do banco criado.

## Como Executar
```bash
python Database/init_db.py
```
- Use `python -m sqlite3 Database/app.db ".tables"` (opcional) para inspecionar as tabelas.
- Durante desenvolvimento, considere apontar `Models(db_path=":memory:")` para bancos temporários em testes automatizados.
