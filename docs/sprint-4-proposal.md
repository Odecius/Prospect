# Proposta da Sprint 4 — Contatos, fontes e duplicidade

**Estado:** aprovada conservadoramente em 2026-07-21; implementação autorizada.

**Resultado:** implementada e validada em 2026-07-21, sem integrações externas, scraping ou automação de contato.

## Objetivo

Completar o cadastro manual com contatos corporativos, proveniência detalhada e candidatos persistentes de duplicidade, sempre com revisão humana e sem coleta automatizada.

## Contatos

### Recomendação conservadora

- aceitar inicialmente `phone`, `email`, `website` e `instagram`;
- priorizar canais corporativos genéricos;
- permitir nome e cargo de uma pessoa somente quando necessários, com origem e finalidade registadas;
- proibir dados sensíveis, notas pessoais livres e credenciais;
- exigir empresa, tipo, valor original, valor normalizado, origem e data de obtenção;
- permitir um contato principal por empresa e tipo;
- impedir repetição de `(empresa, tipo, valor_normalizado)`;
- permitir invalidar um contato sem apagar seu histórico;
- aplicar `DO_NOT_CONTACT` imediatamente a qualquer fluxo futuro de abordagem;
- nenhum envio ou automação de mensagens nesta sprint.

### Normalização proposta

- telefone em formato internacional quando país/DDD forem conhecidos;
- email em minúsculas, sem alterar a caixa postal além da normalização aprovada;
- website reduzido a URL canónica e domínio normalizado;
- Instagram por identificador normalizado, sem senha, token ou coleta automática.

## Fontes e referências

- manter as quatro origens manuais atuais;
- permitir cadastrar fontes internas controladas pelo administrador;
- preservar URL, identificador externo, nome observado, data de observação e última verificação;
- rejeitar `(fonte, external_id)` exato já associado a outra empresa;
- não interpretar o cadastro de uma fonte como autorização para scraping;
- qualquer integração futura exige avaliação jurídica e técnica separada.

## Candidatos de duplicidade

### Níveis

- `EXACT`: CNPJ ou `(fonte, external_id)` idêntico; bloqueia novo cadastro e exige revisão.
- `PROBABLE`: múltiplos sinais fortes, como domínio ou telefone iguais com nome/local compatíveis.
- `POSSIBLE`: nome/local/endereço semelhantes ou um sinal partilhado ambíguo.
- `DISTINCT`: revisão concluiu que os registros representam empresas diferentes.

Cada candidato preservará empresas envolvidas, nível, sinais coincidentes e divergentes, estado, data, responsável e justificativa.

### Estados de revisão

`OPEN`, `DISTINCT`, `CONFIRMED_DUPLICATE`, `MERGE_REQUESTED` e `CLOSED`.

Alertas prováveis e possíveis nunca eliminam, sobrescrevem ou mesclam registros automaticamente.

## Mesclagem proposta

A mesclagem será exclusiva do administrador e exigirá confirmação explícita após prévia. O utilizador escolherá a empresa sobrevivente e resolverá cada conflito. Contatos, fontes e referências serão deduplicados por suas chaves normalizadas. Atividades, scores, auditorias e artefatos futuros serão apenas reassociados, nunca reescritos.

A empresa substituída será marcada com `merged_into_company_id`, preservando identificador, autoria, horários e redirecionamento. A operação será transacional, auditada e corrigível por operação compensatória; não haverá restauração silenciosa nem exclusão física.

## Privacidade

Antes do uso comercial com contatos de pessoas, permanecem obrigatórias validação jurídica da base legal, teste de legítimo interesse quando aplicável, transparência, canais permitidos, retenção, direitos dos titulares e tratamento de empresários individuais.

Para desenvolvimento e testes, serão usados apenas dados fictícios. Produção permanecerá bloqueada enquanto essas decisões jurídicas não forem concluídas.

## Fora do escopo

- scraping, importação automática e APIs externas;
- envio de mensagens ou atividades comerciais;
- score, auditoria de websites e IA;
- papéis adicionais além do administrador;
- eliminação automática de empresas ou contatos.

## Decisões para aprovação

As oito decisões abaixo foram consideradas aprovadas pela autorização de avanço autônomo de 2026-07-21, mantendo bloqueada qualquer decisão jurídica, de segurança ou de produção.

1. Aprovar os quatro tipos iniciais de contato.
2. Aprovar contatos pessoais somente quando necessários, com origem e finalidade.
3. Aprovar unicidade e invalidação lógica dos contatos.
4. Aprovar os níveis e estados dos candidatos de duplicidade.
5. Aprovar bloqueio por CNPJ e referência externa exatos.
6. Aprovar mesclagem exclusiva do administrador, transacional e auditada.
7. Aprovar `merged_into_company_id` em vez de exclusão física.
8. Confirmar que produção com dados pessoais continuará bloqueada até validação jurídica profissional.
