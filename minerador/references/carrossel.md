# Carrossel: analise visual (somente se o usuario pediu)

1. Pegue as URLs dos slides (`endpoints.md`, Etapa 4) e salve numa lista.
2. Rode `python3 scripts/slides.py <pasta> <id> --urls-file <lista>` .
   - Sai com codigo 3 e `REDE_BLOQUEADA` quando o ambiente nao alcanca `cdninstagram.com` (nuvem). Nesse caso rode o MESMO script no
     workbench do Composio (`COMPOSIO_REMOTE_WORKBENCH`), que baixa normalmente, e traga so o texto que ele imprime.
3. O script devolve: texto OCR de cada slide e medidas objetivas (cores dominantes, brilho, contraste, tipo visual, texto%, maior texto,
   hierarquia, posicao do texto, consistencia entre slides) e salva a folha de contato em `folhas/<id>.jpg`.

## Rota A: leitura visual real (terminal local, Desktop com rede livre)
Use Read na folha de contato (`folhas/<id>.jpg`) e no slide 1 e no ultimo em tamanho cheio (`_tmp/<id>/slide_01.jpg`).
Analise de verdade o que ve: paleta e contraste, tipografia (peso, tamanho, hierarquia entre titulo e corpo), layout e grade,
uso de imagem, rosto, print ou ilustracao, consistencia entre slides, ritmo de leitura, densidade de texto, como o slide 1 prende,
indicador de arrastar, slide final e CTA. Use as medidas do script para confirmar o que viu.

## Rota C: leitura visual na nuvem via Drive (documentada, nao testada aqui)
O `/pauta-canal` ve imagens na nuvem assim: rode `slides.py` no workbench do Composio, zipe as folhas e os slides, suba o zip no Drive (`GOOGLEDRIVE_UPLOAD_FILE`), baixe com `download_file_content` do conector do Drive (JSON com base64: `jq -r .content arquivo | base64 -d > pacote.zip`), descompacte em pasta nova e abra com Read. Se o conector do Drive e o Composio estiverem disponiveis, tente a Rota C antes da B. Se qualquer etapa falhar, tente uma vez de novo e caia na Rota B.

## Rota B: analise objetiva (nuvem, sem como ver a imagem)
Sem como trazer a imagem ate o modelo (Rota C indisponivel ou falhou), nenhum modelo da nuvem enxerga a imagem. Use so as medidas e o texto do script, e escreva na ficha
"analise visual objetiva, sem leitura subjetiva". Diga ao usuario, no fechamento, que a leitura visual completa exige rodar a skill
onde o shell alcanca o CDN (terminal local ou Desktop). Nunca descreva visual que nao veio de imagem vista ou de medicao.

## O que a secao "Analise visual" da ficha precisa ter
Paleta (hex e proporcao), contraste, tipografia e hierarquia, layout, tipo visual (plano, misto, fotografico), consistencia,
densidade de texto por slide, papel do slide 1 (promessa, curiosidade), slide final e CTA, e em Rota B a marca de que e objetiva.
