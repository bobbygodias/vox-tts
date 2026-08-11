# Licenças de modelos e runtimes

Este documento registra o estado conhecido em 11 de agosto de 2026. Verifique novamente as fontes primárias antes de baixar, executar ou distribuir modelos.

| Componente | Tipo | Licença conhecida | Consequência para o VOX |
|---|---|---|---|
| VOX | código próprio | Apache-2.0 | código aberto do projeto |
| `idiap/coqui-ai-TTS` | runtime | MPL-2.0 | pode ser integrado respeitando avisos e código coberto |
| XTTS v2 | pesos e saídas | CPML | exige aceitação; uso não comercial |
| F5-TTS | runtime | MIT | código permissivo |
| `firstpixel/F5-TTS-pt-br` | pesos | CC BY-NC 4.0 | atribuição e uso não comercial |
| Mozilla Common Voice | dataset | CC0, conforme a versão | corpus coletivo; não é catálogo de identidades clonáveis |

## Fontes primárias

- Coqui TTS mantido: https://github.com/idiap/coqui-ai-TTS
- Registro XTTS v2: https://github.com/idiap/coqui-ai-TTS/blob/dev/TTS/.models.json
- CPML: https://tts-hub.github.io/cpml/
- F5-TTS: https://github.com/SWivid/F5-TTS
- F5-TTS pt-BR: https://huggingface.co/firstpixel/F5-TTS-pt-br
- Common Voice: https://github.com/common-voice/common-voice

## Regras do projeto

1. A licença Apache-2.0 do VOX não relicencia pesos, datasets ou saídas de terceiros.
2. Pesos não serão incorporados ao repositório.
3. Termos CPML não serão aceitos automaticamente.
4. Cada backend terá sua licença registrada no manifest de síntese.
5. Material publicamente acessível não será tratado como autorização para criar uma identidade vocal.
6. Perfis vocais exigem origem sintética compatível ou autorização explícita e documentada.

Este registro técnico não substitui aconselhamento jurídico.
