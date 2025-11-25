# Entidades do Domínio

> Estruturas orientadas a objetos que representarão músicas, notas e demais elementos de gameplay.

## Estado Atual
- As classes centrais já possuem os dados mínimos necessários para a gameplay rítmica.
- A pasta `entities/` contém `Music.py` e o pacote `Notes/` com tipos específicos (`Note`, `Agudo`, `Grave`, `Flam`, `Mao`).
- A intenção segue sendo separar regras de negócio do loop gráfico, permitindo testes unitários sem pygame.

## `Music`
- Estrutura simples com três atributos: `title`, `csv_path` e `mp3_path`.
- Criada pela `MusicSelectScene` ao varrer a pasta `musics/`, servindo como DTO para outras cenas.
- O parsing do CSV fica a cargo da `GameplayScene`, que converte as linhas em objetos `Note` específicos.

## Pacote `Notes`
- `Note` define atributos compartilhados: tempos de spawn/hit, tipo (`note_type`), posição na tela, estado de animação (`state`, `fade_elapsed`, `alpha`), resultado (`perfect/good/miss`) e informações auxiliares como `key_mistaken`.
- Tipos concretos (`Agudo`, `Grave`, `Flam`, `Mao`) fornecem o timbre/efeito sonoro por meio do método `note_sound` (o detalhamento está nos arquivos específicos).
- O gameplay atual delega à cena o cálculo das janelas de acerto, mas os objetos mantêm flags suficientes para controlar animações de fade/out e queda.

## Próximos Passos Recomendados
1. Expandir `Music` caso sejam necessários metadados adicionais (por exemplo BPM, offset ou dificuldade).
2. Avaliar mover lógica de parsing/validação do CSV para uma fábrica dedicada, mantendo `GameplayScene` enxuta.
3. Padronizar métodos utilitários em `Note` (ex.: helpers de janela de acerto) para reduzir código duplicado na cena.
4. Escrever testes unitários para validar parsing das notas e atualização de estados (fade, queda, etc.).
