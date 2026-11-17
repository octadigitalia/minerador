# Analise de cada item (ficha completa, sem limite de tamanho)

Processe em lotes de ate 6 itens: busque transcricao e comentarios do lote em paralelo, escreva as fichas em `fichas/<nome>.md`
(nome = ultimo trecho do id, por exemplo `DfleQoDCr3B` ou `7646249622893038879`) e so entao passe ao proximo lote.
Com a ferramenta Agent, delegue cada lote a um subagente que grava as fichas e devolve so "ok + ids".
Todo item recebe todas as camadas. Nada de resumo no lugar de analise.

## Modelo da ficha de video (reel ou TikTok)

```
# <id> | <rede> | <conta>
Link, formato, duracao, data, metrica, razao sobre a mediana da conta, comentarios, shares e saves (TikTok)

## Gancho
Palavras exatas dos primeiros 3 a 5 segundos. Tipo do gancho (pergunta, promessa, choque, prova, curiosidade, lista).

## Promessa
O que e prometido e em que segundo a promessa aparece.

## Estrutura
Com marcas de tempo do transcript: abertura, virada, prova, exemplo, CTA. Ritmo e tom.

## Legenda
Legenda inteira e hashtags. O que a legenda acrescenta ou repete do video.

## Comentarios
Os de mais likes, com a contagem: o que o publico pede, elogia, contesta, perguntas e pedidos que viram ideia.

## Encaixe
Os algoritmos classificam o video pelas palavras da transcricao e da legenda. Diga qual topico, qual avatar (quem assiste) e qual dor o video deixa claro, e QUAIS palavras da transcricao ou da legenda mostram isso. Se o topico so aparece depois dos primeiros segundos ou nao aparece, diga.

## Alcance
Viral de nicho ou viral amplo? Evidencia: tema do video, quem comenta, se o tema serve so ao publico do nicho ou a qualquer pessoa. Viral amplo vira "baixa transferencia" na sintese.

## Foco da conta
Os posts recentes da conta repetem o mesmo topico e o mesmo avatar? Sim ou nao, com 2 ou 3 exemplos da lista.

## Destino do CTA
Para onde o video leva: produto proprio, servico, afiliado, comunidade, e-mail, link para outra rede, nada. Link ou empurrao para outra plataforma conta como observacao.

## Por que funcionou
Hipoteses amarradas a evidencia da propria ficha. Confianca alta, media ou baixa. Nunca invente motivo sem dado.
```

As secoes Encaixe, Alcance, Foco da conta e Destino do CTA valem para as tres redes. Elas vem de uma hipotese de um criador (nao de regra publicada pelas plataformas): trate como lente de analise e confirme na sintese com os dados coletados, nunca como fato.

Itens de contraste (razao < 1): mesma ficha, e em "Por que funcionou" diga o que difere dos outliers da mesma conta.

## Modelo da ficha de carrossel
Mesmas secoes, trocando "Estrutura" por "Slide a slide" e acrescentando "Analise visual" (veja `carrossel.md`).
