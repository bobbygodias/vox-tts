# Segurança

## Escopo inicial

VOX ainda não oferece serviço público. Não exponha workers ou endpoints de síntese diretamente à internet.

## Segredos e material privado

- Nunca faça commit de chaves, tokens, URLs privadas ou credenciais do Neon.
- Nunca faça commit de referências vocais, pesos ou áudio privado.
- Manifests públicos não contêm texto integral, caminhos locais ou identificadores pessoais.
- Logs devem usar IDs e hashes, não conteúdo de voz ou narração.

## Serviço remoto futuro

Antes de qualquer exposição externa, implementar autenticação, quotas, limites de requisição, validação de formatos, isolamento do worker, expiração de arquivos, auditoria e proteção contra replay.

## Relato de vulnerabilidades

Não publique credenciais, amostras privadas ou detalhes exploráveis em issues públicas. Use um canal privado definido pelos mantenedores quando ele estiver disponível.
