# Entidades do Domínio

> Estruturas orientadas a objetos que representarão músicas, notas e demais elementos de gameplay.

## Estado Atual
- As classes encontram-se como *stubs* (arquivos vazios) aguardando implementação.
- A pasta `entities/` contém `Music.py` e o pacote `Notes/` com tipos específicos (`Note`, `Agudo`, `Grave`, `Flam`).
- A intenção é separar regras de negócio do loop gráfico, permitindo testes unitários sem pygame.

## `Music`
- Servirá como agregador de metadados da faixa: título exibido, caminhos de áudio/mapa e tempo de offset.
- Pode encapsular parsing do CSV para gerar notas ou delegar para uma fábrica dedicada.

## Pacote `Notes`
- `Note` deverá definir a interface para eventos musicais (tempo de disparo, duração, tipo de acerto esperado).
- Tipos concretos (`Agudo`, `Grave`, `Flam`) representarão variações de notas e permitirão polimorfismo durante o gameplay.
- Ideal manter cada classe responsável por calcular sua janela de acerto e feedback visual/sonoro.

## Próximos Passos Recomendados
1. Definir atributos mínimos da `Music` (nome, bpm, offset, caminho do mapa, caminho do áudio).
2. Criar um parser que converta o CSV em uma lista de `Note` com timestamps absolutos.
3. Implementar comportamento comum em `Note` (por exemplo, `is_hit(timestamp)`), delegando particularidades aos filhos.
4. Integrar as entidades à futura `GameplayScene`, que consumirá esses objetos para sincronizar notas e scoring.
