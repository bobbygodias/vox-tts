# VOX

> **O TTS aberto em brasileiro.**

VOX é uma plataforma aberta, local e desacoplada de modelos para síntese de voz em português brasileiro. O projeto nasce para pesquisa, narração e integração com aplicações sem depender de créditos de APIs proprietárias.

## Estado

**v0.1.0 — fundação do projeto.**

Nesta fase estamos definindo:

- o núcleo independente de backend;
- adaptadores iniciais para F5-TTS e XTTS v2;
- normalização textual pt-BR;
- manifests reproduzíveis de síntese;
- quatro identidades vocais sintéticas iniciais;
- separação entre código, pesos, referências vocais e artefatos.

## Perfis vocais planejados

| ID | Direção | Estado |
|---|---|---|
| `vox-br-young-01` | adulto jovem, luminoso e ágil | design |
| `vox-br-neutral-01` | adulto neutro para narração geral | design |
| `vox-br-rasp-01` | adulto rouco com pitch médio-alto | design |
| `vox-br-senior-01` | adulto sênior, aproximadamente 65 anos | design |

Os perfis serão construídos apenas com material sintético ou explicitamente autorizado. Disponibilidade pública de uma gravação não será tratada como consentimento para clonagem.

## Arquitetura pretendida

```text
Cliente / aplicação
        |
        v
VOX Core API
        |
        +--> estado e manifests (PostgreSQL/Neon)
        |
        +--> worker Python
                 |
                 +--> backend F5-TTS
                 +--> backend XTTS v2
                 +--> backends futuros
```

O Neon armazenará metadados, estados, hashes, versões e auditoria. Pesos de modelos, referências privadas e WAVs grandes não pertencem ao banco nem ao repositório.

## Licenças

O código criado especificamente para o VOX é licenciado sob Apache-2.0. Isso **não** altera as licenças dos backends, pesos ou saídas de terceiros.

- Coqui TTS mantido: código MPL-2.0.
- XTTS v2: pesos CPML, termos próprios e uso não comercial.
- F5-TTS: código MIT.
- `firstpixel/F5-TTS-pt-br`: pesos CC BY-NC 4.0.

Consulte [`docs/MODEL_LICENSES.md`](docs/MODEL_LICENSES.md) antes de baixar, executar ou distribuir qualquer modelo.

## Segurança e privacidade

- Nenhuma chave, token ou credencial no Git.
- Nenhuma referência vocal privada em commits, logs ou manifests.
- Nenhum endpoint de síntese será exposto sem autenticação, quotas, validação de arquivos e isolamento.
- Cada render aceito deverá possuir manifest com hashes e versões, sem texto integral nem caminhos privados.

## Relação com Andrew Social Bridge

VOX é um projeto separado do `andrew-social-bridge`. Uma integração futura usará uma API interna estreita; credenciais do Instagram nunca serão compartilhadas com o worker de áudio.

## Origem

Projeto concebido por Bobby Dias e Andrew Vox como infraestrutura aberta para TTS brasileiro, preservando liberdade técnica, consentimento vocal e reprodutibilidade.
