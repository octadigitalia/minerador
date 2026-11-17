# Sintese e pauta

## Etapa 5: padroes (`padroes.md`)
Leia as fichas. Um padrao exige pelo menos 3 itens, de pelo menos 2 contas e 2 grupos de termos, com os ids de origem.
Evidencia menor entra como "hipotese". Cubra: tipos de gancho recorrentes, duracao que mais performa por rede, estrutura dominante,
formato vencedor, padroes visuais dos carrosseis, CTA, diferencas entre Instagram e TikTok, e lacunas (o que o publico pede e ninguem entregou).
Afirmacao sem item de origem nao entra.

Acrescente, com os dados da pesquisa, o que as fichas mostram sobre: encaixe de topico (os outliers deixam topico e avatar claros logo no inicio?), alcance (outliers de nicho versus virais amplos e como cada grupo se comporta), foco das contas que performam (mesmo topico repetido ou topicos variados), e destino do CTA (qual caminho de monetizacao os outliers usam). Se os dados nao confirmarem uma dessas hipoteses, diga que nao confirmaram.

## Etapa 6: pauta de 20 ideias (`pauta.md`)
Cada ideia nasce **nativa de uma rede** (sem empurrar o publico de uma rede para outra; o unico caminho de saida aceito e para e-mail ou comunidade propria) e traz avatar e dor. Cada ideia: titulo; rede e formato sugeridos; angulo novo; gancho de abertura (a frase exata dos primeiros segundos, ou o slide 1
com texto e direcao visual); estrutura em beats (ou slide a slide no carrossel); padroes aproveitados (ids); em que difere dos
concorrentes; risco. Ideias originais, relevantes hoje, que despertem a curiosidade do mesmo publico. Aplique o angulo do usuario
em todas. Agrupe as 20 ideias por dor do avatar, para formar linhas editoriais de serie (consistencia de topico) e nao ideias soltas. Se o usuario informou a plataforma principal do publico, priorize ideias nativas dela. Se a evidencia nao sustentar 20 boas, entregue menos e diga.

## Regras de escrita (texto que vai soar como o Matheus)
Sem travessao. Sem a construcao "nao e sobre X, e sobre Y". Portugues correto, com acentos. Tom opinativo e com personalidade.
Nunca invente resultado, numero ou experiencia.

## Entrega
`python3 scripts/report.py <pasta> --titulo "<nicho>"` gera `pesquisa.pdf` (padroes, tabela dos itens, folhas de contato).
No chat: cobertura em uma linha (contas, itens, fichas, custo real estimado), os 3 padroes mais fortes e as 5 melhores ideias em lista curta.
Envie `pauta.md` e o PDF com SendUserFile. Depois rode `python3 scripts/cleanup.py <pasta>`.
