# Backend F5 pt-BR

O primeiro adaptador concreto do VOX mira o runtime F5-TTS e o checkpoint
`firstpixel/F5-TTS-pt-br`. Nesta etapa ele apenas produz um plano auditável: não
instala dependências, não baixa pesos e não executa síntese.

## Por que um plano antes da execução

`vox f5-plan` verifica os arquivos locais, o formato de saída, as confirmações de
direito vocal e de uso não comercial, a presença do CLI e do FFmpeg. O JSON de
saída contém hashes e tamanhos, mas omite o texto integral e os caminhos privados
da referência vocal.

O checkpoint pt-BR está marcado como **CC BY-NC 4.0**. Portanto, este backend não
deve ser usado comercialmente sem outra licença aplicável. A licença Apache-2.0
do VOX não substitui a licença dos pesos.

## Exemplo

```bash
vox f5-plan \
  --text-file ./private/text.txt \
  --reference ./private/reference.wav \
  --reference-text-file ./private/reference.txt \
  --checkpoint ./models/model_last.safetensors \
  --vocab ./models/vocab.txt \
  --model-name F5TTS_Base \
  --output ./renders/test.wav \
  --device cuda \
  --confirm-voice-rights \
  --confirm-noncommercial-use
```

O nome da arquitetura é obrigatório e nunca é inferido do nome do checkpoint.
`F5TTS_Base` acima é apenas um exemplo: antes do primeiro render real, ele deverá
ser conferido contra a configuração exata usada no treinamento do peso baixado.

## Regras atuais da referência

- áudio em WAV, FLAC, MP3, M4A ou OGG;
- WAV com duração verificável inferior a 12 segundos;
- transcrição UTF-8 obrigatória, evitando download implícito de ASR;
- recomendação de aproximadamente um segundo de silêncio ao final;
- consentimento ou outro fundamento jurídico explícito para o uso da voz.

Arquivos que não sejam WAV ainda exigem conferência externa de duração. A etapa
de execução só será adicionada depois de validarmos runtime, checkpoint, vocabulário
e uma referência autorizada em máquina adequada.

## Fontes técnicas

- F5-TTS oficial: <https://github.com/SWivid/F5-TTS>
- checkpoint pt-BR: <https://huggingface.co/firstpixel/F5-TTS-pt-br>
- CC BY-NC 4.0: <https://creativecommons.org/licenses/by-nc/4.0/>
