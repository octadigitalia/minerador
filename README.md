# Minerador

Skill para o Claude que pesquisa o seu nicho no Instagram, TikTok e YouTube com dados reais e entrega uma pauta de 20 ideias baseada no que já funciona.

Ela acha os vídeos que performaram muito acima da média das contas (os outliers), transcreve, lê os comentários, analisa um por um, tira os padrões e monta a pauta. Sem achismo.

By [OctaDigital](https://octadigital.com.br).

## O que ela faz

- Mapeia contas e termos do seu nicho
- Seleciona os outliers da amostra
- Transcreve e analisa cada vídeo, com os comentários
- Carrossel com análise visual (opcional)
- YouTube com retenção, título e capa (opcional, gasta mais tokens)
- Entrega a pauta de 20 ideias

## Como instalar

1. Baixe este repositório (botão **Code > Download ZIP**) ou clone:

   ```
   git clone https://github.com/octadigitalia/minerador
   ```

2. Copie a pasta `minerador/` para a pasta de skills do seu Claude (por exemplo `~/.claude/skills/` no Claude Code), ou envie a pasta compactada em **Configurações > Capacidades > Skills** no Claude.

3. Abra o Claude e rode `/minerador`.

## Estrutura

```
minerador/
  SKILL.md          instruções da skill
  references/       endpoints, análise, carrossel, YouTube e pauta
  scripts/          seleção da amostra, portões de checagem, slides, capas e relatório
```

## Uso gratuito por enquanto

A skill está liberada de graça por tempo indeterminado. Se ela te ajudar, segue [@minerando.ia](https://instagram.com/minerando.ia) no Instagram.
