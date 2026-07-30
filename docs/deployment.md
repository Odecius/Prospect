# Operação segura

## Estado

A Sprint 14 preparou e validou localmente os artefatos operacionais. Nenhum servidor foi
alterado e nenhum deploy foi realizado. O primeiro uso em Ubuntu continua condicionado à
aprovação da infraestrutura, do acesso privado, do proxy HTTPS, do armazenamento de
segredos e dos objetivos de recuperação.

## Topologia preparada

O arquivo `compose.production.yaml` descreve uma implantação conservadora:

- imagem da aplicação identificada por versão ou digest imutável;
- aplicação sem privilégios adicionais, filesystem somente leitura e `/tmp` temporário;
- porta HTTP publicada apenas em `127.0.0.1`, para consumo por proxy local;
- PostgreSQL sem porta publicada e conectado por rede interna;
- credenciais fornecidas externamente, sem valores padrão;
- integrações externas desativadas por padrão;
- logs JSON rotacionados em cinco arquivos de 10 MB;
- liveness em `/health` e readiness com consulta mínima ao banco em `/ready`;
- reinício automático e healthchecks com períodos de inicialização.

O proxy deverá ser o único componente exposto, exigir HTTPS e restringir o acesso por
VPN, rede privada ou uma camada de identidade aprovada. O Compose não instala nem
configura esse controle externo.

## Configuração

1. Construa, teste, publique e assine a imagem por um processo controlado.
2. Copie `deploy/production.env.example` para um arquivo fora do repositório.
3. Substitua todos os placeholders e use `APP_IMAGE` com digest `sha256`.
4. Gere `APP_SECRET_KEY` e `POSTGRES_PASSWORD` aleatórios e independentes.
   Em `DATABASE_URL`, aplique codificação URL aos caracteres reservados da senha.
5. Mantenha auditoria de websites e IA desativadas até seus controles específicos.
6. Valide sem iniciar serviços:

   `docker compose --env-file /caminho/seguro/production.env -f compose.production.yaml config --quiet`

Configuração de produção rejeita segredo conhecido de desenvolvimento, banco diferente de
PostgreSQL e a senha de desenvolvimento presente na URL. Valores de segredo nunca devem
ser impressos em logs ou anexados a tickets.

## Backup e restauração

Backups devem usar `pg_dump` no formato custom, ser criptografados antes de sair do host e
ser armazenados com menor privilégio em destino separado. O nome recomendado contém data,
ambiente e versão. A retenção, o RPO e o RTO ainda precisam de decisão operacional.

Uma restauração nunca deve ser testada sobre o banco ativo. Crie um PostgreSQL descartável,
restaure com `pg_restore --exit-on-error --no-owner --no-acl` e verifique migrations,
contagens mínimas, autenticação e fluxos críticos.

## Publicação e rollback

O procedimento completo está em [operations-runbook.md](operations-runbook.md). Em resumo:

1. registrar SHA do commit, digest da imagem e migration atual;
2. obter e verificar backup restaurável;
3. executar migrations como etapa única e explícita;
4. iniciar a imagem imutável;
5. validar `/health`, `/ready`, login, páginas autenticadas e logs;
6. interromper a publicação se algum critério falhar;
7. para rollback de código, restaurar o digest anterior;
8. para schema incompatível, seguir o plano específico da migration ou restaurar em uma
   instância separada; nunca executar downgrade destrutivo por reflexo.

## Decisões ainda externas ao código

- servidor, hardening e política de atualizações do Ubuntu;
- VPN/rede privada/camada de identidade;
- proxy, domínio e certificados;
- secret manager e responsáveis pelo acesso;
- RPO, RTO, retenção, criptografia e destino de backup;
- monitoramento, alertas e plantão;
- janela e responsável por migration, rollback e restauração.

Essas decisões são bloqueios do deploy real, não lacunas escondidas no código.
