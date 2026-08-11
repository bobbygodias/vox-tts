# Licenças de runtimes e modelos

Este inventário registra o entendimento do VOX em 11 de agosto de 2026. Ele não
é aconselhamento jurídico e deve ser revisto antes de distribuição ou uso
comercial. A licença Apache-2.0 do código VOX não relicencia runtimes, pesos,
datasets, gravações de referência nem saídas de terceiros.

| Componente | Camada | Licença declarada | Consequência para o VOX |
|---|---|---|---|
| VOX | código próprio | Apache-2.0 | código aberto do projeto |
| F5-TTS | runtime/código | MIT | integração permitida conforme os avisos da licença |
| `firstpixel/F5-TTS-pt-br` | pesos | CC BY-NC 4.0 | atribuição e uso não comercial; sem autorização comercial presumida |
| Coqui TTS mantido | runtime/código | MPL-2.0 | obrigações da MPL aplicam-se aos arquivos cobertos |
| XTTS v2 | pesos/modelo | Coqui Public Model License | termos próprios, aceite explícito e uso não comercial |
| Mozilla Common Voice | dataset | CC0, conforme a versão | corpus coletivo; não é catálogo de identidades clonáveis |

## Regras do projeto

- Downloads de pesos nunca são automáticos durante diagnóstico ou planejamento.
- Aceites ou confirmações de licença nunca são feitos pelo software em nome do usuário.
- Um peso marcado como não comercial não entra em produção comercial sem outra licença válida.
- Voz pública não significa voz licenciada para clonagem; a origem e o consentimento são controles separados.
- Um manifest registra identificadores, versões e hashes, sem texto integral nem caminhos de referências privadas.

## Fontes primárias

- F5-TTS: <https://github.com/SWivid/F5-TTS>
- F5-TTS pt-BR: <https://huggingface.co/firstpixel/F5-TTS-pt-br>
- CC BY-NC 4.0: <https://creativecommons.org/licenses/by-nc/4.0/>
- Coqui TTS: <https://github.com/idiap/coqui-ai-TTS>
- Coqui Public Model License: <https://tts-hub.github.io/cpml/>
- Mozilla Common Voice: <https://github.com/common-voice/common-voice>
