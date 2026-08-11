# Arquitetura do VOX

## Princípios

1. O núcleo não conhece detalhes de F5-TTS, XTTS ou qualquer provedor.
2. Texto, referências vocais e áudio permanecem privados por padrão.
3. Nenhum modelo é baixado ou aceito silenciosamente.
4. Estado transacional e artefatos binários são armazenados separadamente.
5. Toda síntese aceita possui um manifest reproduzível e livre de conteúdo privado.

## Componentes

### VOX Core

Define contratos para texto, idioma, perfil vocal, backend, artefato e manifest. Não importa PyTorch nem carrega pesos.

### Worker Python

Executa jobs de síntese em processo isolado. Carrega um backend por vez, preserva partes concluídas após falha e monta WAV sem recodificação com perdas.

### Adaptadores de backend

- `f5_ptbr`: experimento principal de prosódia brasileira.
- `xtts_v2`: compatibilidade multilíngue e comparação de identidade.
- futuros adaptadores devem declarar licença, hardware, idioma e requisitos de consentimento.

### StateStore

Interface substituível para perfis, jobs, versões, hashes, licenças e auditoria. A implementação inicial poderá usar filesystem; a persistência compartilhada usará PostgreSQL/Neon.

### ArtifactStore

Guarda WAVs, partes intermediárias e manifests fora do PostgreSQL. Começa em filesystem privado e poderá ganhar adaptador compatível com armazenamento de objetos.

## Fluxo

```text
cliente -> VOX Core -> StateStore -> fila -> worker -> backend
                                      |          |
                                      +----------+-> ArtifactStore
```

## Fronteiras de segurança

- Referências vocais não entram no Git, Neon, telemetria ou mensagens de erro.
- Um serviço remoto deverá exigir autenticação, quotas, limites de tamanho, validação de mídia e isolamento.
- Integrações futuras usarão APIs estreitas e credenciais segregadas.

