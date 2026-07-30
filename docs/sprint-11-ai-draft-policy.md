# Política da Sprint 11 — IA para rascunhos

**Estado:** aprovada para implementação conservadora em 2026-07-22.

## Finalidade

Gerar um rascunho curto de abordagem comercial para revisão humana. O ABC Prospect não envia mensagens, não escolhe destinatários, não agenda cadências e não toma decisões comerciais automaticamente.

## Provedor e protocolo

- provedor inicial: OpenAI Responses API;
- modelo padrão: `gpt-5.6-luna`, escolhido para texto curto sensível a custo;
- `store=false` em todas as requisições;
- saída estruturada estrita com assunto, corpo e alertas de revisão;
- nenhuma tool, web search, arquivo, memória, conversa anterior ou execução em background;
- timeout de 15 segundos, no máximo uma retentativa transitória e 300 tokens de saída;
- limite padrão de três gerações por minuto por usuário.

## Minimização

Somente estes dados empresariais podem sair do ABC Prospect:

- nome da empresa;
- categoria normalizada;
- cidade e UF;
- sinais booleanos da auditoria mais recente do website, quando existentes;
- tipo fixo de rascunho e idioma.

Não são enviados nomes de pessoas, emails, telefones, histórico comercial, notas livres, CNPJ, Place ID, URLs, conteúdo do website, scores completos ou dados sensíveis. Valores empresariais são tratados como dados não confiáveis e nunca como instruções. A Sprint 12 permite somente o resumo numérico do score documentado em `sprint-12-commercial-content-policy.md`; explicações livres continuam proibidas.

## Fluxo humano

1. pessoa autenticada solicita um rascunho para empresa ativa;
2. o servidor recusa empresas `DO_NOT_CONTACT`, arquivadas ou mescladas;
3. o provedor devolve um rascunho estruturado;
4. o rascunho é persistido como `DRAFT`, com modelo, versão, ator, uso e snapshot minimizado;
5. uma pessoa pode editar, aprovar ou rejeitar, sempre com justificativa;
6. aprovar não envia a mensagem e não altera o pipeline;
7. rascunhos e decisões são imutáveis após a revisão.

## Retenção e produção

Rascunhos seguem a retenção configurável do histórico comercial. Conteúdo não deve aparecer em logs técnicos. A funcionalidade permanece desativada por padrão e exige chave restrita, limite de custo, alerta de faturamento, contrato/termos revisados e validação jurídica profissional antes do uso comercial em produção.

## Limitações

O texto pode conter erro, exagero, tom inadequado ou inferência incorreta. A aprovação humana é obrigatória, mas não substitui a responsabilidade de quem usar o texto fora do sistema.

## Referências oficiais consultadas

- [Responses API recomendada para projetos novos](https://developers.openai.com/api/docs/guides/migrate-to-responses)
- [Structured Outputs](https://developers.openai.com/api/docs/guides/structured-outputs)
- [Modelos e custos](https://developers.openai.com/api/docs/models)
