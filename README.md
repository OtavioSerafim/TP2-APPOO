# TP2-APPOO — Engrenada Hero

Protótipo de jogo rítmico desenvolvido como continuação prática da disciplina **Análise, Projeto e Programação Orientados a Objetos (APPOO)**. A aplicação evolui o foco do TP1 para um domínio de entretenimento, experimentando arquitetura orientada a objetos sobre **pygame**. O código já implementa fluxo de menus, autenticação leve de jogadores, ranking de músicas e gameplay com registro de pontuação.

## 🧭 Contexto acadêmico
O objetivo é validar conceitos de orientação a objetos em um cenário interativo: estados de jogo, transições de cena, componentes reutilizáveis e integração com persistência simples via SQLite. A stack (Python + pygame) mantém a filosofia da disciplina de trabalhar com bibliotecas acessíveis, privilegiando clareza arquitetural em vez de engine pesada.

## 🎯 Foco em arquitetura orientada a objetos
- **Controlador principal (`GameApp`)** encapsula inicialização do pygame, loop principal e troca de cenas.
- **Cenas especializadas** (`MenuScene`, `MusicSelectScene`, `AddMusicScene`) herdam de `BaseScene`, compartilhando lógica de plano de fundo, dimensionamento e hooks de atualização.
- **UI desacoplada**: botões e campos de entrada vivem em `utils/`, permitindo reaproveitar temas e interações.
- **Persistência modelada**: camada `models/` replica o padrão de CRUD genérico do TP1 para armazenar jogadores, históricos de partidas e métricas básicas.

## 🚀 Visão geral da aplicação
- Menu inicial com botões para jogar, importar músicas, alternar tela cheia e sair, além de um painel no canto inferior esquerdo para criar/login de jogadores persistidos em SQLite.
- Cena de seleção que lista músicas válidas em `musics/`, toca prévia em áudio, exibe leaderboard com top 10 daquela faixa e mostra o melhor resultado do jogador ativo.
- Cena de importação que lê arquivos ZIP (CSV + MP3), sanitiza nomes e registra a nova música no diretório do jogo.
- Gameplay rítmico que sincroniza notas do CSV, calcula hits/perfects, aplica feedback visual e salva a partida com score e breakdown de acertos.

## 🧱 Arquitetura em camadas
- `game_controller.py`: ponto de entrada, configura janela, relógio e roteamento entre cenas.
- `scenes/`: camadas de apresentação do game, com uma base abstrata para reuso de comportamento.
- `utils/`: componentes visuais reutilizáveis (`Button`, `InputField`) e constantes de cores/resolução.
- `entities/`: objetos de domínio que representam músicas (`Music`) e notas (`Note` + variações) consumidos pela gameplay.
- `models/`: camada SQLite genérica para jogadores (`Player`) e histórico de sessões (`Play`), reutilizando `Model`/`ModelBase`.
- `Database/`: script de inicialização e migrações SQL versionadas (criação de tabelas `player` e `plays`).
- `assets/`: plano de fundo, imagens e sons auxiliares.

## 🎵 Fluxo de músicas
1. A pasta `musics/` agrupa uma subpasta por música.
2. Cada música deve conter exatamente um `.csv` (mapa de notas) e um `.mp3` (trilha de áudio).
3. A cena **Adicionar Música** aceita um ZIP com esses arquivos, cria a estrutura padronizada (`map.csv` + `audio.mp3`) e já deixa a faixa disponível na seleção.
4. A cena de gameplay consome esses dados para sincronizar notas, spawnar objetos `Note` concretos e avaliar acertos.

## 🗄️ Banco de dados e migrações
- Banco SQLite em `Database/app.db`.
- Migrações numéricas em `Database/migrations/*.sql`, garantindo criação de `player` e `plays` com colunas para score e estatísticas.
- O script `Database/init_db.py` recria o arquivo e aplica as migrações em ordem segura (inclusive prefixos > 9).

## ⚙️ Configurando o ambiente

### Pré-requisitos
- Python 3.11 ou superior
- `pip`
- (Opcional) `python3-tk` para habilitar o seletor de arquivos nativo na cena de importação

### Passo a passo
1. **Clonar o repositório**
	```bash
	git clone https://github.com/OtavioSerafim/TP2-APPOO.git
	cd TP2-APPOO
	```
2. **Criar e ativar um ambiente virtual** (Linux/macOS)
	```bash
	python -m venv .venv
	source .venv/bin/activate
	```
3. **Instalar dependências**
	```bash
	pip install --upgrade pip
	pip install -r requirements.txt
	```
4. **Inicializar o banco (opcional)**
	```bash
	python Database/init_db.py
	```
	Execute apenas se quiser começar com um banco limpo durante os testes.
5. **Rodar o jogo**
	```bash
	python game_controller.py
	```
	A janela abrirá com o menu principal. Use o botão *Tela Cheia* para alternar modos.

## 🌐 Controles atuais
- `Setas para cima/baixo`: navega na lista de músicas.
- `Enter`: confirma a música selecionada e inicia o gameplay.
- `Esc`: retorna ao menu a partir de qualquer cena (durante o gameplay encerra a música atual e volta para a seleção).
- `Z`, `A` e `Espaço`: executam notas individuais (grave, agudo, mão).
- `A + Espaço` simultâneos: executam a nota `Flam`.
- Mouse interage com botões, campo de jogador e demais elementos de UI.

## 📦 Dependências principais
- [pygame](https://www.pygame.org/news) para renderização, áudio e loop de jogo.
- [tkinter](https://docs.python.org/3/library/tkinter.html) (opcional) para o diálogo nativo de seleção de ZIP.
- [sqlite3](https://docs.python.org/3/library/sqlite3.html) da biblioteca padrão, usado nos modelos de persistência.

## 🚧 Próximos passos
- Expandir feedback audiovisual (efeitos sonoros/visuais diferenciados por resultado, partículas, HUD mais rico).
- Implementar opções de dificuldade e métricas extras (combo, precisão percentual, streak).
- Permitir replays ou histórico detalhado por jogador dentro do próprio jogo.
- Automatizar testes para parsing das notas e registro de partidas.

---

Projeto acadêmico desenvolvido pelos alunos Otávio Serafim de Souza Matos e Germano Marques Cipriano Fagundes na disciplina APPOO.
