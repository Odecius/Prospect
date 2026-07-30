# Runbook operacional

## Escopo e regra de parada

Este runbook prepara uma operação interna de instância única. Ele não autoriza exposição
pública, uso de dados reais em testes nem ativação automática de integrações. Pare o
procedimento diante de segredo exposto, backup não restaurável, migration sem plano,
healthcheck instável, acesso além da rede aprovada ou divergência entre SHA, imagem e
documentação.

## Pré-publicação

- [ ] revisão e CI aprovados no SHA exato;
- [ ] imagem vinculada ao SHA e referenciada por digest imutável;
- [ ] inventário de dependências e vulnerabilidades revisado;
- [ ] arquivo de ambiente fora do repositório, permissões restritas e sem placeholders;
- [ ] `DATABASE_URL` usa credencial codificada para URL e conecta somente ao serviço `db`;
- [ ] banco sem porta publicada;
- [ ] proxy HTTPS e acesso privado validados;
- [ ] integrações externas desativadas ou aprovadas individualmente;
- [ ] migration atual e migration alvo registradas;
- [ ] backup recente restaurado com sucesso em ambiente descartável;
- [ ] digest anterior e procedimento de rollback disponíveis;
- [ ] janela, responsáveis e critérios de abortar registrados.

## Publicação controlada

1. Registre horário, operador, SHA, digest anterior e novo digest.
2. Confirme espaço em disco, saúde do banco e validade do certificado.
3. Produza o backup e valide seu checksum e criptografia.
4. Execute `alembic upgrade head` uma única vez, em processo controlado.
5. Atualize somente a imagem da aplicação e aguarde `/ready`.
6. Valide login/logout, dashboard, pesquisa, cadastro e um fluxo de leitura.
7. Confirme ausência de erros, segredos e conteúdo pessoal desnecessário nos logs.
8. Registre o resultado e encerre a janela.

## Checklist pós-publicação

- [ ] `/health` retorna somente `{"status":"ok"}`;
- [ ] `/ready` retorna `200` e passa a `503` quando o banco está indisponível;
- [ ] documentação OpenAPI não está disponível em produção;
- [ ] cookie de sessão possui `HttpOnly`, `Secure` e `SameSite=Lax`;
- [ ] HSTS, CSP, `X-Content-Type-Options` e `X-Frame-Options` estão presentes;
- [ ] aplicação é acessível somente pelo caminho de rede aprovado;
- [ ] PostgreSQL não possui porta publicada;
- [ ] containers executam sem novos privilégios e a aplicação não executa como root;
- [ ] logs rotacionam e não contêm credenciais;
- [ ] auditoria e IA permanecem no estado explicitamente aprovado;
- [ ] métricas básicas de disponibilidade, disco e falha de backup estão ativas.

## Rollback

Para falha sem mudança incompatível de schema, restaure `APP_IMAGE` ao digest anterior e
repita o checklist. Para mudança de schema incompatível, interrompa a escrita, preserve a
instância e siga o plano específico da migration. Restaure o backup em banco separado,
valide-o e só então planeje a troca. Downgrade e restauração sobre o banco ativo exigem
decisão humana explícita porque podem apagar dados.

## Teste de recuperação da Sprint 14

Em 2026-07-23, um PostgreSQL 17.5 descartável recebeu uma tabela e um registro sentinela,
gerou dump custom com `pg_dump`, teve o banco recriado, restaurou com `pg_restore` e
recuperou o valor esperado. O teste não usou o volume de desenvolvimento nem dados reais.

Repetir o exercício após mudanças relevantes e periodicamente no ambiente operacional.
Registrar duração, tamanho, checksum, resultado e responsável, sem registrar conteúdo do
backup.

## Incidente

1. Restrinja o acesso e preserve evidências técnicas mínimas.
2. Não copie tokens, cookies, dumps ou dados pessoais para chat/ticket.
3. Registre início, impacto, versão e ações.
4. Rotacione credenciais potencialmente expostas.
5. Recupere primeiro em ambiente isolado.
6. Avalie obrigações contratuais e de LGPD com responsável e apoio jurídico.
7. Documente causa, correção e prevenção antes de reabrir o serviço.
