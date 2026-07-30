# Política da Sprint 13 — dashboard e exportação manual

**Estado:** implementada conservadoramente em 2026-07-23.

## Indicadores

O dashboard apresenta somente métricas diretamente relacionadas à prospecção: empresas ativas, distribuição por pipeline, `DO_NOT_CONTACT`, ausência de website válido, presença de score, auditoria concluída e conteúdo comercial aprovado. Os totais derivam do banco transacional e não constituem decisão automática.

## Segmentação

A pesquisa operacional combina texto, categoria, UF e estado do pipeline. Ordenação e paginação permanecem reproduzíveis. `DO_NOT_CONTACT` é exibido como estado próprio e nunca é convertido em indicação de contato.

## Exportação manual

- exige pessoa autenticada, token CSRF, confirmação na interface e filtros explícitos;
- inclui no máximo 500 empresas ativas por operação;
- acima do limite, exige refinamento dos filtros;
- campos permitidos: empresa, categoria, cidade, UF, pipeline, presença de website e score mais recente;
- não inclui CNPJ, contatos, pessoas, emails, telefones, notas, atividades, fontes, conteúdo de IA ou URLs;
- protege células textuais contra interpretação como fórmulas por planilhas;
- gera arquivo local somente após ação humana; não envia, agenda ou compartilha conteúdo.

## Auditoria

Cada exportação registra tipo, filtros normalizados, lista de campos, quantidade, ator e horário em `export_audits`. O arquivo não é armazenado pelo sistema e seu conteúdo não aparece em logs técnicos.

## Limites

O dashboard não é BI genérico, recomendador autônomo ou ferramenta de campanhas. Exportações devem seguir minimização, finalidade e retenção aplicáveis. A pessoa responsável deve proteger o arquivo depois do download e respeitar imediatamente `DO_NOT_CONTACT`.
