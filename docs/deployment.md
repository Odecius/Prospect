# Deployment

## Estado atual

Existe uma fundação de aplicação, mas não existe processo de deploy validado. Nenhum deploy está autorizado antes da Fase 12 e das decisões de infraestrutura correspondentes.

## Destino planejado

Ubuntu Server com aplicação e PostgreSQL isolados adequadamente. A topologia final, o método de acesso e o provedor ainda dependem de decisão.

## Requisitos antes do primeiro deploy

- imagem/container versionado e executado sem privilégios;
- proxy reverso e HTTPS;
- aplicação interna não exposta além do necessário;
- PostgreSQL sem porta pública;
- secrets fora do repositório e da imagem;
- migrations como etapa explícita e controlada;
- backups criptografados e restauração testada;
- logs para saída padrão, rotação e retenção definidas;
- healthcheck e monitoramento mínimo;
- rollback da aplicação e plano compatível com mudanças de schema;
- checklist de segurança e teste pós-deploy.

## Sequência planejada

1. validar build e testes;
2. revisar imagem, configuração e secrets;
3. executar backup verificável;
4. aplicar migration aprovada;
5. publicar a versão;
6. validar healthcheck, autenticação, logs e fluxos críticos;
7. executar rollback se critérios falharem;
8. registrar versão e resultado no changelog/runbook.

## Decisões pendentes

- servidor e mecanismo de acesso (rede privada, VPN ou alternativa);
- domínio/certificados e proxy reverso;
- armazenamento de secrets;
- RPO, RTO, retenção e local de backup;
- monitoramento e alertas;
- janela e responsável por migrations/rollback.

Consulte [`../ARCHITECTURE.md`](../ARCHITECTURE.md), [`../SECURITY.md`](../SECURITY.md) e [`../DECISIONS.md`](../DECISIONS.md). Qualquer comando de produção deverá ser adicionado somente após validação no ambiente real e autorização explícita.
