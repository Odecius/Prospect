# Política da Sprint 12 — diagnóstico e rascunho de proposta

**Estado:** implementada conservadoramente em 2026-07-22.

## Finalidade

Produzir conteúdo interno de apoio comercial em três tipos controlados: mensagem inicial, diagnóstico comercial e rascunho de proposta. Todo resultado é um rascunho sujeito a edição, aprovação ou rejeição humana. Aprovação não envia, publica, precifica, altera pipeline ou representa decisão comercial final.

## Evidências e minimização

O contexto enviado ao provedor pode conter somente:

- tipo do rascunho e idioma;
- nome empresarial, categoria, cidade e UF;
- sinais booleanos permitidos da auditoria mais recente;
- total, versão da fórmula e componentes numéricos `fit`, `reputation` e `digital_gap` do score mais recente.

Explicações livres do score, contatos, nomes de pessoas, emails, telefones, CNPJ, URLs, Place ID, notas, atividades, HTML e conteúdo remoto não são enviados. O resultado guarda referências locais como `company_profile`, `website_audit:<id>` e `opportunity_score:<id>` para revisão da origem; os identificadores não são incluídos no contexto externo.

## Regras do conteúdo

- não inventar preço, prazo, garantia, cliente, resultado, consentimento ou fato;
- indicar incertezas e separar evidência de sugestão;
- não gerar website, landing page, código, logo ou instrução de publicação;
- não criar instrução de envio ou contato automático;
- rejeitar tipos diferentes dos três valores controlados;
- respeitar imediatamente `DO_NOT_CONTACT`, arquivamento e mesclagem;
- preservar versão do prompt, modelo, uso, ator, horário e decisão humana.

## Fluxo humano

1. a pessoa autenticada escolhe mensagem, diagnóstico ou proposta;
2. o serviço valida empresa, status, limite e tipo;
3. o provedor devolve assunto, corpo e alertas estruturados;
4. o sistema anexa referências locais de evidência e persiste o rascunho;
5. a pessoa confere as fontes, edita e aprova ou rejeita com justificativa;
6. a decisão torna a versão imutável;
7. qualquer utilização externa é manual e permanece fora do ABC Prospect.

## Arquitetura

A Sprint 12 reutiliza `generated_messages` e o workflow existente. Não cria tabela, migration, documento comercial completo, PDF, preço, website, mecanismo de publicação ou estado de envio.

## Produção e riscos pendentes

A integração continua desativada sem configuração explícita. Antes do uso comercial em produção ainda são obrigatórios chave restrita, teto e alertas de custo, avaliação contratual e jurídica/LGPD, retenção documentada, controle de saída e validação humana dos exemplos. IA pode errar, exagerar ou inferir além das evidências; aprovação humana reduz, mas não elimina, essa responsabilidade.
