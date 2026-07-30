# Glossário oficial

Este glossário estabelece o significado dos termos usados no ABC Prospect. Toda documentação futura deve adotar estas definições. Quando um termo exigir mudança de significado, a alteração deve ser aprovada e registrada antes de ser aplicada aos demais documentos ou ao código.

## Empresa

Organização cadastrada como objeto central da prospecção. Possui nome, categoria, cidade, UF, origem e estado do pipeline obrigatórios. Pode reunir contatos, evidências, atividades, scores, auditorias e rascunhos comerciais assistidos.

## Lead

Empresa identificada como possível cliente, mas ainda não suficientemente avaliada para ser considerada uma oportunidade qualificada. No ABC Prospect, não é uma entidade separada: é uma forma de descrever uma empresa nas etapas iniciais do pipeline.

## Oportunidade

Empresa cuja adequação ou interesse comercial já recebeu qualificação suficiente para justificar acompanhamento prioritário. Não é uma entidade separada no modelo inicial; sua situação é representada pelo contexto da empresa, pelo pipeline, pelas evidências e, futuramente, pelo score.

## Score

Avaliação numérica, explicável e versionada da oportunidade comercial. É calculada somente após aprovação da fórmula e não é necessária para cadastrar, editar, pesquisar ou qualificar uma empresa.

## Pipeline

Fluxo controlado que representa a evolução comercial de uma empresa, desde o cadastro até um resultado ou retirada do fluxo ativo.

## Pipeline Status

Estado atual da empresa no pipeline. Começa em `NEW` e aceita apenas `NEW`, `QUALIFIED`, `CONTACTED`, `REPLIED`, `MEETING`, `PROPOSAL_SENT`, `NEGOTIATION`, `WON`, `LOST`, `DO_NOT_CONTACT` e `ARCHIVED`.

## Categoria

Classificação controlada da atividade ou segmento principal da empresa. É obrigatória no cadastro e pertence a uma taxonomia governada pelo projeto.

## Origem

Fonte de onde vieram os dados ou a identificação da empresa. É obrigatória e deve ser registrada por uma referência de fonte, com data de observação e proveniência suficiente para auditoria.

## Cidade

Município associado ao cadastro operacional da empresa. É obrigatório no escopo inicial brasileiro e deve usar forma normalizada conforme a taxonomia geográfica aprovada.

## UF

Sigla da Unidade Federativa brasileira associada à cidade da empresa. É obrigatória, possui dois caracteres e deve aceitar somente códigos oficiais válidos.

## Auditoria de Website

Avaliação pontual, reproduzível e versionada da presença ou qualidade técnica e comercial de um website. Não constitui pentest e deve preservar critérios, data, resultado e eventuais falhas de execução.

## Atividade Comercial

Registro cronológico de uma ação ou acontecimento relevante na relação com uma empresa, como pesquisa, contato, resposta, reunião, mudança de estado ou próximo passo. Deve identificar ator e horário.

## Contato

Canal de comunicação corporativo ou dado de uma pessoa vinculada à empresa, como telefone, email ou website. Deve possuir tipo, valor normalizado, origem quando aplicável e tratamento compatível com privacidade e finalidade.

## Proposta

Rascunho comercial assistido e versionado, preparado para revisão humana. No MVP, não constitui documento enviado, aceite, faturamento ou decisão final e não possui automação de envio.

## Produto Interno

Aplicação ABC Prospect destinada inicialmente à operação interna da ABC Solutions. Seu escopo principal corresponde às Fases 1 a 13 e é considerado concluído após a aprovação da Fase 13.

## SaaS

Possível produto futuro multiempresa e multi-tenant. Não integra o escopo, o percentual nem os critérios de conclusão do Produto Interno e somente poderá começar como projeto independente após decisão formal.

## MVP

Menor versão do Produto Interno capaz de validar, com segurança e uso real, se o processo de prospecção ficou mais rápido, consistente e útil. MVP não significa ausência de autenticação, proteção de dados, rastreabilidade ou revisão humana.
