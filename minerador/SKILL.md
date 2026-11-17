---
name: minerador
description: Minerador: pesquisa de nicho no Instagram e TikTok com dados reais (contas, outliers, transcrição, comentários, carrossel com análise visual opcional) e pauta de 20 ideias.
---

# Minerador

Escavador de ideias com base em dados reais do Instagram e do TikTok, com YouTube opcional. Mesma lógica da /pauta-canal (nicho, outliers, análise item a item, padrões, pauta), com a análise ajustada a cada plataforma: Instagram e TikTok sem capa e sem retenção; YouTube com retenção, título e capa.

**Princípio central:** a análise de cada item selecionado é sempre completa. Nada de resumir, cortar ou pular camada para gastar menos. A economia de tokens vem só do método: consultas `jq` que já devolvem linhas prontas, scripts que fazem a conta mecânica, lotes com ficha gravada em disco e referências lidas só quando a etapa chega.

## Ao carregar: banner

A primeira coisa que você escreve, antes de qualquer pergunta ou ferramenta, é este banner **exatamente como está**, dentro de um bloco de código (cabe em terminal, web, Desktop e celular):

```
█▌ M I N E R A D O R ▐█
▸ ideias com base em dados
  by OctaDigital
```

Depois do banner, siga direto para a pergunta inicial.

## Arquitetura (o que ler e quando)

- `references/endpoints.md`: todas as consultas e `jq` testados. Leia ao chegar nas etapas 1, 2 e 4.
- `references/analise.md`: modelo da ficha e rubrica de vídeo. Leia ao começar a etapa 4.
- `references/carrossel.md`: análise visual. Leia só se o usuário pediu carrossel.
- `references/youtube.md`: lente do YouTube (termos, lista do canal, retenção, título, capa). Leia só se o usuário pediu YouTube.
- `references/pauta.md`: síntese, pauta, regras de escrita e entrega. Leia ao chegar nas etapas 5 e 6.
- `scripts/` (Python 3, caminhos relativos a esta pasta): `select.py` (seleção da amostra), `gate.py` (portões de cobertura e de fichas), `slides.py` (download, folha de contato e medidas do carrossel), `capas.py` (capas do YouTube), `report.py` (PDF), `cleanup.py` (limpeza). Use-os em vez de calcular na cabeça.

## Regras de economia

1. Nunca traga payload bruto. Use `jq` e `@tsv`; evite `tikhub.*` e `scrapecreators.*` para listas, salvo onde `endpoints.md` indicar.
2. Chamadas independentes em paralelo, no mesmo bloco.
3. Estado em disco em `minerador/<nicho>-<AAAA-MM-DD>/`. No contexto fica só a tabela de seleção.
4. Analise em lotes de até 6 itens e grave a ficha logo. Com a ferramenta Agent, delegue cada lote a um subagente que grava as fichas e devolve só "ok + ids".
5. Se existir pasta do mesmo nicho com menos de 7 dias, ofereça reaproveitar `selecao.tsv` e as fichas e minerar só o que falta. Use `cache_max_age: 7d` onde existir.
6. Uma linha de progresso por etapa, sem narrar chamadas.
7. Falha: no máximo 1 nova tentativa. Erro de entrada (400, invalid_input) não cobra. Item que não puder ser analisado por completo é substituído pelo próximo da fila, nunca entregue pela metade sem aviso.
8. Estimativa antes de gastar: cerca de US$ 0,02 por item analisado, mais US$ 0,05 a 0,10 de descoberta (valores estimados). Acima de 100 itens, confira `mcp__Treg__balance`.

## Pergunta inicial (uma só mensagem)

Use AskUserQuestion quando existir e pule o que já foi informado:

- **Nicho** (e, se quiser, o ângulo ou posicionamento dele, para aplicar nas ideias)
- **Tamanho da amostra:** 15, 30 (padrão) ou 50 itens analisados. Muda o quanto se pesquisa, nunca a profundidade de cada item.
- **Redes:** Instagram + TikTok (padrão), só Instagram ou só TikTok. **YouTube é opcional** e gasta bem mais tokens (detalhe do vídeo, mapa de reprise, comentários e capas): só inclua se o usuário pedir, e avise disso ao perguntar.
- **Plataforma principal do público (opcional):** se ele sabe onde o público mais está, a pauta e o peso da amostra seguem essa rede.
- **Incluir carrossel / post de imagem, com análise visual dos slides?** Sim ou não. Reels e vídeos entram sempre.
- **Contas semente (opcional):** 2 a 5 @ de referência. No Instagram é o melhor ponto de partida.

Candidatas por rede (Instagram e TikTok): cerca de metade da amostra (15 itens: 8 contas; 30: 15; 50: 25). No YouTube, a amostra do canal é de pelo menos 15 itens. Crie a pasta com `fichas/` e `_tmp/`.

## Etapas

**1. Descoberta de contas.** Descoberta acha contas, não vídeos; a pontuação vem da etapa 2. Monte 6 a 10 termos em 3 ou 4 grupos (nicho, sinônimos, dores, formatos, jargão em PT-BR e em inglês). Consultas em `endpoints.md`. Instagram e TikTok têm o mesmo peso: parta das sementes e expanda por contas similares e hashtag no Instagram. Grave `termos_contas.tsv` (rodada, grupo, termo, conta) e rode `python3 scripts/gate.py cobertura <pasta>`. Se falhar, mais uma rodada com termos novos. Com YouTube, siga `references/youtube.md` para o mapa de termos (25 a 40) e as consultas.

**2. Posts por conta e outlier.** Uma chamada por conta candidata, em paralelo, com o `jq` de `endpoints.md`, que calcula a mediana e a razão dentro da própria consulta. Anexe as linhas a `candidatos.tsv`.

**3. Seleção.** `python3 scripts/select.py <pasta> --n <amostra> --max-por-conta 4` grava `selecao.tsv` e imprime a tabela curta (equilibra redes e formatos e inclui um contraste por rede).

**4. Análise completa de cada item.** Leia `references/analise.md` (e `carrossel.md` se pediu carrossel, `youtube.md` se pediu YouTube). Todo vídeo tem transcrição, legenda inteira e comentários (no YouTube, também detalhe, retenção, título e capa); todo carrossel tem slides lidos e análise visual. Grave `fichas/<nome>.md`. Depois rode `python3 scripts/gate.py fichas <pasta> [--carrossel]`; se falhar, complete o que falta a partir de `selecao.tsv`, sem nova descoberta.

**5. Síntese e 6. Pauta de 20 ideias.** Leia `references/pauta.md`. Grave `padroes.md` e `pauta.md`, gere o PDF com `scripts/report.py`, entregue e limpe com `scripts/cleanup.py`.

## Encerramento

Apague temporários do workbench, rode `cleanup.py`, feche abas e processos abertos por você e diga em uma linha o que foi encerrado. Não mate processos que já existiam.
