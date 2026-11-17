# Lente YouTube (opcional, gasta bem mais tokens)

Só rode se o usuário pediu YouTube na pergunta inicial. Avise antes: a análise de YouTube lê mais coisa (detalhe do vídeo com mapa de reprise, capítulos, comentários, capas) e pesa mais que Instagram e TikTok. A ficha de YouTube tem retenção, título e capa; as outras redes não. Na síntese, só compare YouTube com as outras redes em tema, gancho, duração e CTA, nunca em retenção ou capa.

## Etapa 1: mapa de termos
Para YouTube o mapa é maior: 25 a 40 termos em pelo menos 6 grupos (nome do tema e sinônimos, jargão, ferramentas e marcas, dores, resultados desejados, formatos de vídeo, níveis, termos adjacentes, outros idiomas se o nicho for global). Termo vago entra assim mesmo; o gate de cobertura decide o que pesa. Bola de neve: dos maiores outliers e dos canais repetidos, extraia títulos e palavras-chave e gere termos novos, no máximo 2 rodadas extras.

Busca: `anyapi.youtube.search`, body `{"query":"<termo>","sortBy":"popular"}` (valores: relevance, popular) e `uploadDate` (today, this_week, this_month, this_year). Não há filtro de região nem idioma: **escreva o termo em português** para vir conteúdo em português (um termo ambíguo trouxe resultados em espanhol). Shorts: `anyapi.youtube.search_shorts`, mesmo formato. jq de descoberta (canal, id do canal, ocorrências, maior pico):
`.data.videos|group_by(.authorId)|map([.[0].channel,.[0].authorId,length,(map(.views)|max)]|@tsv)|join("\n")`
Grave os canais em `termos_contas.tsv` e rode `gate.py cobertura`.

## Etapa 2: lista do canal e outlier
`anyapi.youtube.channel_videos`, body `{"handle":"@canal"}` ou `{"channelId":"UC..."}` (30 por página; `nextCursor`). Os views da lista vêm arredondados (59000, 9400), o que basta para o outlier. A lista não traz likes, comentários nem sempre a duração; isso vem do detalhe. Troque `C` pelo nome do canal:
```
.data.videos as $a|($a|map(.views)|sort|.[length/2|floor]//1|if .<1 then 1 else . end) as $m|((($a|map(select(.views>=3*$m))|sort_by(-.views)|.[:5])+[$a|min_by(.views)])|unique_by(.id)|map(["youtube","video","C",.id,.views,((.views/$m*10|floor)/10),$m,"","",(.lengthText//""),(.createdUtc|strftime("%y%m%d")),.title]|@tsv)|join("\n"))
```
Anexe a `candidatos.tsv` e rode `select.py --max-por-conta 5`. Mínimo de 15 itens de YouTube, vindos de pelo menos 4 grupos de termos.

## Etapa 4: dados de cada vídeo selecionado
- **Detalhe** (views, likes, comentários, duração, capítulos em segundos, palavras-chave, mapa de mais reprisados, URL da capa): `scrapecreators.youtube.video.detail`, query `{"url":"https://www.youtube.com/watch?v=<id>"}`. Resposta bruta e grande: tente `jq` e, se for ignorado, rode em lotes de 3 e grave a ficha logo. Dado que não veio, escreva "não obtido", nunca infira.
- **Transcrição:** `anyapi.youtube.video_transcript_full`, query `{"url":"<url>"}`. Traz tempo por trecho e se a legenda é manual ou automática. Se falhar, tente outro provedor; sem transcrição a ficha fica incompleta e o vídeo sai da síntese.
- **Comentários:** `treg.youtube.video.comments`, `{"video_id":"<id>"}` (50 por chamada, com likes). Confira o primeiro retorno.
- **Capas:** `python3 scripts/capas.py <pasta> id:razao id:razao ...` (veja abaixo).

## Seções extras da ficha de YouTube
- **Retenção:** cruze os picos do mapa de mais reprisados com a transcrição e diga o que está sendo dito ou mostrado em cada pico e onde o interesse cai. Sem o mapa, "não obtido".
- **Título:** fórmula, número, tensão ou curiosidade, palavras de poder.
- **Capa, duas camadas:** (1) medidas do `capas.py`: texto por OCR e tamanho, brilho, contraste, saturação, cores. (2) leitura visual olhando a imagem: rosto (sim ou não), expressão e olhar, % do quadro que o rosto ocupa, enquadramento, elementos, texto sobreposto, contraste entre áreas, o que a capa promete sem o título. Descreva só o que viu. Sem imagem aberta, escreva "leitura visual não obtida" e nunca descreva por dedução.
- Estrutura usa os capítulos quando existirem; senão blocos pela transcrição, com viradas, prova e CTA.

## Como ver as capas (mesmas rotas do carrossel)
- **Rota A (terminal local):** `capas.py` baixa direto de `i.ytimg.com`. Abra as folhas `folhas/capas_NN.jpg` com Read (8 capas por folha, com id e outlier escritos em cima) e as capas decisivas em tamanho cheio.
- **Rota C (nuvem):** o shell leva 403 do proxy em `i.ytimg.com`. Rode `capas.py` no workbench do Composio (baixa normalmente), zipe as folhas e as capas, suba o zip no Drive (`GOOGLEDRIVE_UPLOAD_FILE`), traga com `download_file_content` do conector do Drive (o resultado é um JSON com base64: `jq -r .content arquivo | base64 -d > capas.zip`, `unzip` em pasta nova, `file` para conferir) e abra com Read. Essa rota está documentada no `/pauta-canal` e não foi testada nesta skill. Se uma etapa falhar, tente uma vez de novo e marque "leitura visual não obtida" só nas capas afetadas.
- As imagens abertas ficam no contexto até o fim: leia as capas perto do fim da etapa 4.
