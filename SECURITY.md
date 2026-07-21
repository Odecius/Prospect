# Segurança do ABC Prospect

## Situação atual

As Fases 1A e 1B implementam infraestrutura e autenticação administrativa local, sem interface ou entidades comerciais. Senhas usam Argon2, a sessão é assinada em cookie `HttpOnly` com `SameSite=Lax`, operações mutáveis autenticadas exigem CSRF e cookies são obrigatoriamente seguros em produção. A migration e o ciclo de autenticação foram validados com PostgreSQL/Docker real.

## Credenciais e configuração

- segredos nunca serão versionados;
- configuração sensível virá de variáveis de ambiente ou secret manager;
- `.env` local deverá estar no `.gitignore` e nunca rastreado;
- `.env.example` terá apenas nomes e valores fictícios;
- segredos expostos deverão ser revogados ou rotacionados antes de qualquer discussão sobre limpeza de histórico.

## Autenticação e autorização

- toda rota da aplicação, exceto healthchecks estritamente necessários, deverá exigir autenticação;
- sessões/cookies deverão usar `HttpOnly`, `Secure` em produção e política `SameSite` adequada;
- senhas locais usarão Argon2 com salt e nunca serão armazenadas em texto puro;
- autorização será aplicada no servidor, nunca apenas pela interface;
- o modelo começará com menor privilégio e poderá adotar papéis quando houver mais usuários.

## Proteção contra exposição pública

- acesso inicial restrito a ambiente interno ou a uma camada de acesso explicitamente aprovada;
- HTTPS obrigatório em produção;
- documentação interativa e endpoints administrativos não ficarão públicos por padrão;
- CORS restritivo;
- cabeçalhos de segurança e proteção CSRF avaliados para todos os fluxos com cookie;
- mensagens de erro não exporão stack traces, SQL ou configuração.

## Banco de dados

- usuário exclusivo da aplicação, sem privilégios administrativos;
- PostgreSQL não exposto diretamente à internet;
- conexões criptografadas quando atravessarem rede não confiável;
- consultas parametrizadas via SQLAlchemy;
- migrations e backups executados com identidades separadas quando viável;
- ambientes de desenvolvimento, teste e produção isolados.

## Logs e auditoria

Logs não devem incluir senhas, tokens, cookies, cabeçalhos de autorização, conteúdo integral de mensagens/propostas ou dados pessoais desnecessários. Eventos de segurança e alterações comerciais relevantes devem ter ator, horário e resultado, sem transformar logs em cópia dos registros de negócio.

## Backups e recuperação

- backups PostgreSQL criptografados e com retenção definida;
- acesso aos backups por menor privilégio;
- testes periódicos de restauração;
- RPO, RTO e procedimento de rollback definidos antes do deploy;
- exclusão segura conforme política de retenção e obrigações legais.

## Dados comerciais e pessoais

- coletar somente dados necessários para finalidade comercial legítima;
- registrar origem e data de obtenção;
- diferenciar contato corporativo de dado pessoal;
- permitir correção, bloqueio e exclusão quando aplicável;
- definir base legal, retenção e atendimento a direitos antes de ampliar a coleta;
- não enviar dados a provedores de IA sem avaliação e aprovação específicas.

## Scraping, fontes externas e spam

- não presumir que Google Maps ou qualquer serviço possa ser raspado livremente;
- revisar termos de uso, licenças, robots, limites e base legal antes de integrar;
- preferir APIs ou fontes autorizadas;
- aplicar rate limiting, cache e backoff quando permitido;
- nenhuma automação de envio em massa;
- revisão humana e ação explícita antes de qualquer contato;
- respeitar opt-out, frequência e legislação aplicável.

## Controles de aplicação planejados

- validação de entrada e limites de tamanho;
- proteção contra SQL injection, XSS, CSRF e enumeração de contas;
- rate limiting em autenticação e integrações, quando aplicável;
- dependências fixadas, revisadas e atualizadas de modo controlado;
- testes para autorização, validação e regras sensíveis.

## Checklist por fase

- [x] Modelo de autenticação aprovado.
- [x] Política de acesso e exposição inicial aprovada e aplicada localmente.
- [x] `.gitignore` e `.env.example` criados sem segredos reais.
- [x] Threat model mínimo da autenticação realizado.
- [ ] Retenção e base legal documentadas antes de concluir a Fase 2.
- [ ] Backup e restauração testados.
- [ ] HTTPS, logs e menor privilégio validados.
- [ ] Integrações externas avaliadas individualmente antes da Fase 7.
- [x] Google Places API (New) avaliada individualmente; chave somente no backend, resultados temporários e Place ID como única persistência.

As páginas públicas `/privacy` e `/terms` são exceções mínimas à autenticação para cumprir transparência e políticas da fonte. Não expõem dados comerciais nem configuração.
