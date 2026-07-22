# Política da Sprint 10 — auditoria de websites

**Estado:** aprovada para implementação conservadora em 2026-07-22.

## Finalidade e escopo

A auditoria registra sinais técnicos e comerciais básicos da página inicial de um website já cadastrado como contato da empresa. Ela auxilia a revisão humana e não constitui pentest, monitoramento, prova de conformidade ou avaliação automática definitiva.

## Regras obrigatórias

- somente contatos ativos do tipo `WEBSITE`, pertencentes a uma empresa ativa, podem ser auditados;
- somente `http` e `https`, nas portas 80 e 443, sem credenciais na URL;
- destinos locais, privados, reservados, multicast e link-local são bloqueados, inclusive após redirecionamentos;
- no máximo três redirecionamentos, cinco segundos por requisição e 512 KiB de resposta;
- apenas a página inicial é consultada; links, assets, JavaScript e formulários não são executados;
- não existe varredura de portas, exploração, descoberta de diretórios ou tentativa de autenticação;
- limite padrão de cinco auditorias por minuto por usuário e intervalo de um minuto por website;
- o HTML e cabeçalhos brutos não são persistidos;
- resultados são snapshots imutáveis e nunca alteram score ou pipeline automaticamente.

## Sinais registrados

- disponibilidade, status HTTP, URL final e duração;
- uso de HTTPS e eventual redirecionamento de HTTP para HTTPS;
- tamanho limitado da resposta e tipo HTML;
- presença de `title`, descrição, viewport, idioma e canonical;
- sinais textuais simples de telefone, email, WhatsApp e formulário de contato;
- código de falha seguro quando a auditoria não termina.

Esses sinais descrevem somente o que foi observado naquele instante. Ausência de um sinal não prova que o recurso inexiste no restante do website.

## Retenção, privacidade e auditoria

Snapshots permanecem vinculados à empresa para rastreabilidade e seguem o período de retenção configurável do produto. Não são coletados dados sensíveis, conteúdo de formulários ou identificadores de visitantes. Cada execução registra ator e horário.

## Limitação operacional

A validação de DNS na aplicação reduz SSRF, mas a produção também deve aplicar controle de saída na rede ou proxy para defesa contra DNS rebinding. Auditorias permanecem desativadas em produção até esse controle ser confirmado.
