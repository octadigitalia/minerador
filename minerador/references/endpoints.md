# Endpoints e consultas (Instagram e TikTok, testadas com dados reais)

YouTube tem arquivo próprio: `youtube.md`.

Chame com `mcp__Treg__call`, `endpoint_id`, `params` (body) e `query` `{"jq": "..."}`. Nunca peça payload bruto.
Em todas as consultas de lista, troque `H` pelo handle da conta (sem @). Saida: linhas TSV, uma por item.

## Etapa 1: descoberta (devolve conta, ocorrencias, maior pico)

TikTok, `anyapi.tiktok.search.videos`, body `{"query":"<termo>","sortBy":"most-liked"}` (validos: relevance, most-liked, date-posted):
`.data.videos|group_by(.author)|map([.[0].author,length,(map(.views)|max)]|@tsv)|join("\n")`

Instagram hashtag, `anyapi.instagram.hashtag.posts`, body `{"hashtag":"<tag>","datePosted":"last-month","mediaType":"reel"}`:
`.data.posts|group_by(.username)|map([.[0].username,length,(map(.likes)|max)]|@tsv)|join("\n")`

Instagram contas similares (partindo de sementes e dos melhores achados), `anyapi.instagram.similar_profiles`, body `{"handle":"<h>"}`:
`(.data.profiles // .data.users // .data)|map(.username // .handle)|join(",")`

Instagram busca de perfis (no maximo 1 vez por pesquisa, resposta pesada, sem jq): `scrapecreators.x.v1-instagram-search-profiles`, query `{"query":"<kw>"}`.

Nao ha filtro de idioma nem seguidores confiaveis. Filtre portugues pela legenda e pelo nome.
Grave cada achado em `termos_contas.tsv` (rodada, grupo, termo, conta) e rode `gate.py cobertura`.

## Etapa 2: posts por conta (linhas ja no formato de candidatos.tsv)

Colunas: rede, formato, conta, id, metrica, razao, mediana, likes, comentarios, extra (duracao em s ou nº de slides), data (aammdd), legenda.
Cada consulta traz ate 5 outliers (3x a mediana da conta; 2,5x para carrossel) mais o pior post da conta (contraste, razao < 1).
Anexe a saida a `candidatos.tsv`. Se a conta nao devolver linhas, nao tem outlier. Se tiver menos de 15 posts na pagina, siga `nextCursor`.

TikTok, `anyapi.tiktok.user.videos`, body `{"handle":"H"}`:
```
(.data.videos|map(select(.views!=null))) as $a|($a|map(.views)|sort|.[length/2|floor]//1|if .<1 then 1 else . end) as $m|((($a|map(select(.views>=3*$m))|sort_by(-.views)|.[:5])+[$a|min_by(.views)])|unique_by(.url)|map(["tiktok","video","H",.url,.views,((.views/$m*10|floor)/10),$m,.likes,.comments,"",(.createdUtc|strftime("%y%m%d")),(.caption//""|gsub("[\t\n]";" ")|.[:140])]|@tsv)|join("\n"))
```

Instagram reels, `anyapi.instagram.user.reels`, body `{"handle":"H"}`:
```
(.data.reels|map(select(.views!=null))) as $a|($a|map(.views)|sort|.[length/2|floor]//1|if .<1 then 1 else . end) as $m|((($a|map(select(.views>=3*$m))|sort_by(-.views)|.[:5])+[$a|min_by(.views)])|unique_by(.shortcode)|map(["instagram","reel","H",.shortcode,.views,((.views/$m*10|floor)/10),$m,.likes,.comments,(.durationSeconds|floor),(.createdUtc|strftime("%y%m%d")),(.caption//""|gsub("[\t\n]";" ")|.[:140])]|@tsv)|join("\n"))
```

Instagram carrosseis (so se pedido), `anyapi.instagram.user.posts`, body `{"handle":"H"}` (exige 3 carrosseis na amostra; cada pagina traz so 12 posts, entao siga `nextCursor` ate 3 paginas; foto nao tem views, entao compete por likes):
```
.data.posts as $p|($p|map(select((.media|length)>1))) as $c|if ($c|length)<3 then "" else ($c|map(.likes)|sort|.[length/2|floor]//1|if .<1 then 1 else . end) as $m|((($c|map(select(.likes>=2.5*$m))|sort_by(-.likes)|.[:5])+[$c|min_by(.likes)])|unique_by(.url)|map(["instagram","carrossel","H",.url,.likes,((.likes/$m*10|floor)/10),$m,.likes,.comments,(.media|length),(.createdUtc|strftime("%y%m%d")),(.caption//""|gsub("[\t\n]";" ")|.[:140])]|@tsv)|join("\n")) end
```

Depois: `python3 scripts/select.py <pasta> --n <amostra>`.

## Etapa 4: dados de cada item selecionado (em lotes, em paralelo)

Transcricao Instagram: `scrapecreators.x.v2-instagram-media-transcript`, query `{"url":"<url do reel>","cache_max_age":"7d"}`.
Reel acima de 120 s da 400 sem cobrança: repita com `allow_long_transcription=true` (10 creditos por minuto).
Use `jq` `.transcripts[0].text` (a resposta crua traz o texto duas vezes, com tempos por palavra, e pesa). Para estrutura com tempos: `.transcripts[0].transcript_with_timestamp|map("\(.start|floor)s "+.text)|join(" ")`. Se der 404 "post does not have a video", o item e carrossel/imagem: reclassifique e va para o fluxo de carrossel.

Transcricao TikTok: `scrapecreators.x.v1-tiktok-video-transcript`, query `{"url":"<url>","language":"pt"}`.
Use `jq` `.transcript_with_timestamp|map("\(.start|floor)s "+.text)|join(" ")` (a resposta crua traz WEBVTT + JSON, texto em dobro). Sem legenda de audio: `use_ai_as_fallback=true` (10 creditos, ate 2 min). Alternativa: `anyapi.tiktok.video_transcript_full` (POST).

Comentarios, `anyapi.instagram.post.comments` ou `anyapi.tiktok.video.comments`, body `{"url":"<url>"}`:
`(.data.comments//[])|sort_by(-.likes,-(.text|length))|.[:20]|map([.likes,.replies,.text]|@tsv)|join("\n")` (curtidas vem 0 no Instagram: o desempate por tamanho traz os comentarios com conteudo; `not_found` = sem comentarios, nao erro; palavra repetida em massa tipo "Quero" = gatilho de CTA, conte e registre)

URLs dos slides de um carrossel (vem da lista, nao do post.detail), `anyapi.instagram.user.posts`:
`.data.posts|map(select(.url|test("<shortcode>")))|.[0].media|map(.url)|join("\n")`
As URLs expiram: baixe logo apos a selecao.

## Erros conhecidos
- `tikhub.*` e `scrapecreators.*` devolvem payload gigante; so use onde indicado.
- `sortBy: likes` no TikTok e invalido (use most-liked). Hashtag tikhub deu 400: use o anyapi.
- Erro de entrada (400, invalid_input) nao cobra. No maximo 1 nova tentativa.
- Seguidores vem nulos em varias respostas: nao dependa deles.

- Descoberta sem filtro de idioma: depois de listar contas, descarte as que nao postam em PT-BR (olhe 2 legendas) antes de gastar a etapa 2.
- Pagina de posts do Instagram tem 12 itens; views nulas somem do calculo (guarda no jq).
