# Aquisição verificável do modelo F5 pt-BR

O VOX não inclui pesos no Git e não baixa modelos durante testes, diagnóstico ou
planejamento. O arquivo `manifests/models/f5-ptbr.json` fixa os artefatos externos
necessários para a primeira prova de conceito.

## Escopo real do download

O repositório `firstpixel/F5-TTS-pt-br` contém aproximadamente 12,1 GB porque
mantém três checkpoints. O VOX seleciona somente:

| Artefato | Origem | Tamanho |
|---|---|---:|
| `model_last.safetensors` | `firstpixel/F5-TTS-pt-br` | 1.348.431.976 bytes |
| `vocab.txt` | `SWivid/F5-TTS/F5TTS_Base` | 13.800 bytes |

O manifesto fixa revisões e SHA-256 para impedir troca silenciosa de conteúdo.
O checkpoint `.safetensors` foi preferido aos arquivos `.pt`, que dependem de
desserialização Pickle e ocupam cerca de 5,39 GB cada.

## Verificação local

Depois que um operador autorizado obtiver os dois arquivos e os colocar em um
diretório privado, fora do repositório:

```bash
vox model-verify \
  --manifest manifests/models/f5-ptbr.json \
  --directory /diretorio/privado/f5-ptbr
```

O comando retorna `0` apenas quando nome, tamanho e SHA-256 dos dois arquivos
coincidem. Retorna `3` para arquivos ausentes ou divergentes e `2` para manifesto
ou diretório inválido. O relatório não revela o caminho absoluto do diretório.

## Limite de licença e arquitetura

Os pesos são CC BY-NC 4.0. O download e o uso devem ser deliberados e compatíveis
com finalidade não comercial. O manifesto registra `F5TTS_Base` apenas como
candidato de arquitetura, pois a combinação precisa ser confirmada por um teste
curto no runtime real antes de qualquer narração longa.

O runtime foi fixado em `f5-tts==1.1.22`, publicação ligada ao commit
`9c614e9657089213efc6a7421b30630be138a3f5`. O manifesto também registra o
SHA-256 da roda oficial publicada no PyPI. PyTorch não foi fixado porque sua
distribuição correta depende do hardware do worker: CUDA, ROCm, XPU, MPS ou CPU.

## Topologia

- GitHub: código, manifests e CI sem pesos;
- Neon/PostgreSQL: jobs, estados, versões, hashes e auditoria;
- armazenamento privado: checkpoints, referências e renders;
- worker de áudio: PyTorch, F5-TTS e GPU/CPU escolhida.

O próximo passo dependente de infraestrutura é executar `vox doctor` na máquina
que será o worker. Só então escolheremos a distribuição PyTorch correta.
