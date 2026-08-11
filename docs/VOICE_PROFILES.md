# Perfis vocais iniciais

Os quatro perfis são especificações de identidade sintética, não cópias disfarçadas de pessoas.

| ID | Impressão etária | Timbre e prosódia | Uso inicial |
|---|---|---|---|
| `vox-br-young-01` | adulto jovem | luminoso, pitch médio-alto, ritmo ágil | conteúdo jovem e explicações curtas |
| `vox-br-neutral-01` | adulto | equilibrado, claro, ritmo moderado | narração geral e documentários |
| `vox-br-rasp-01` | adulto | rouquidão controlada, pitch médio-alto, ataque firme | personagens, opinião e trechos intensos |
| `vox-br-senior-01` | aproximadamente 65 anos | ressonância madura, ritmo ponderado, respiração natural | história, reflexão e autoridade serena |

## Construção

- Separar pitch, formantes, duração, curva melódica, textura espectral e soprosidade.
- Evitar transformação simples de pitch, que costuma soar caricata.
- Usar apenas referências sintéticas compatíveis ou material explicitamente autorizado.
- Guardar referências fora do Git e fora do banco.
- Alterar uma categoria por iteração e versionar o manifest.

## Critérios de aceitação

1. Português brasileiro natural e inteligível.
2. Quatro identidades claramente distinguíveis.
3. Nenhum perfil reconhecível como uma pessoa-fonte não autorizada.
4. Estabilidade em frases longas, números, datas, siglas e nomes próprios.
5. Ausência de repetição, cortes, ressonância metálica e emendas audíveis.
6. Manifest com backend, versão, hashes, parâmetros e licença.

Os valores numéricos de pitch e formantes serão definidos somente após os primeiros testes auditivos.
