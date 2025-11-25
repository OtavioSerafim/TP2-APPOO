# Modelos de Persistência

> Visão geral das classes responsáveis por acessar e manipular o banco SQLite.

## Visão Geral
- A pasta `models/` reaproveita o padrão do TP1: uma base abstrata (`ModelBase`), uma implementação genérica (`Model`) e modelos concretos.
- `Models` atua como *contexto compartilhado*, abrindo uma conexão única e expondo instâncias prontos para uso.
- O banco padrão é `Database/app.db`, mas `Models` aceita um caminho customizado para facilitar testes.

## Classes Principais
| Classe        | Tabela(s) | Responsabilidades |
|---------------|-----------|-------------------|
| `ModelBase`   | genérica  | Define interface CRUD obrigatória e fornece cursor reutilizável. |
| `Model`       | genérica  | Implementa CRUD padrão em SQL e hooks `prepare_create_data`/`prepare_update_data`. |
| `Player`      | `player`  | CRUD de jogadores, valida nome único e oferece `get_by_name`. |
| `Play`        | `plays`   | Registra partidas, valida data, score e contadores de acerto/erro; inclui consultas auxiliares. |
| `Models`      | múltiplas | Mantém conexão `sqlite3` e fornece acesso tipado (`models.player`, `models.play`). |

## Fluxos Comuns
### Registrar Jogador
1. Chame `models.player.create({"name": "Jogador"})`.
2. O hook `prepare_create_data` garante string não vazia e remove espaços extras.

### Registrar Partida
1. Monte o payload com `played_at`, `music_name`, `score`, `player_id` e contadores opcionais.
2. `models.play.create(payload)` converte datas para ISO (`YYYY-MM-DD HH:MM:SS`) e valida inteiros não negativos.
3. Use `models.play.latest(limit=10)` ou `models.play.for_player(player_id)` para recuperar resultados.

## Tratamento de Dados
- `_normalize_datetime` aceita `datetime` ou string; qualquer outro tipo gera `ValueError`.
- `_ensure_int` impede valores booleanos e valida limites mínimos.
- Atualizações parciais (`update`) só escrevem campos presentes no payload.

## Convenções
- Sempre que criar um novo modelo concreto, registre-o no dicionário interno de `Models` para disponibilizar via propriedades.
- Utilize `Models.close()` quando terminar a sessão para liberar a conexão SQLite.
- Tests podem instanciar `Models` apontando para um banco temporário (`:memory:` ou arquivo em diretório temporário).
