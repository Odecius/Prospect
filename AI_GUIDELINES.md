# AI Guidelines — ABC Prospect

## Fonte de verdade e ordem de leitura

Antes de qualquer alteração, agentes de IA devem ler:

1. `README.md`;
2. `PROJECT_CONTEXT.md`;
3. `AI_NOTES.md`;
4. `TODO.md` e `ROADMAP.md`;
5. `DECISIONS.md`;
6. `docs/glossary.md` e `docs/business_rules.md`;
7. `docs/traceability.md`, `docs/sprint_plan.md` e a documentação operacional relevante em `docs/`;
8. `C:\Projetos\Abc\ABC-Development-Standard`, somente para consulta.

Em conflito entre o padrão central e uma necessidade deste projeto, registrar opções e aguardar aprovação. Não modificar o padrão central.

## Limites obrigatórios

- Não alterar, mover, renomear ou commitar arquivos de outros projetos.
- Não copiar código de outros projetos sem autorização e atribuição explícitas.
- Não implementar funcionalidade fora do escopo solicitado.
- Não executar deploy sem autorização explícita.
- Não fazer commit, push, force push, rebase ou alteração remota sem solicitação explícita.
- Não armazenar segredos, credenciais, tokens ou dados pessoais reais em código, fixtures, logs ou documentação.
- Não adicionar dependências sem necessidade clara e aprovação compatível com o escopo.
- Não presumir permissão para scraping, especialmente de Google Maps ou serviços semelhantes.
- Não automatizar contato comercial em massa.
- Não enviar mensagem comercial sem revisão e ação humana.

## Forma de trabalho

- Entender o estado atual antes de editar.
- Fazer mudanças pequenas, coesas e verificáveis.
- Preservar a arquitetura monolítica modular até decisão registrada em contrário.
- Validar entradas e tratar erros explicitamente.
- Preferir recursos nativos e soluções simples.
- Adicionar ou atualizar testes proporcionais ao risco; sempre executar os testes aplicáveis.
- Atualizar documentação quando arquitetura, setup, segurança, dados, deploy ou comportamento mudar.
- Registrar decisões relevantes em `DECISIONS.md`.
- Informar todos os arquivos alterados e o resultado das verificações.
- Mostrar `git status --short` ao concluir.

## Segurança e dados

- Usar variáveis de ambiente ou secret manager; `.env` deve permanecer ignorado.
- Usar somente valores fictícios em exemplos.
- Não registrar conteúdo integral de contatos, mensagens ou propostas.
- Minimizar dados pessoais e respeitar finalidade, retenção e exclusão.
- Aplicar menor privilégio a banco, aplicação e infraestrutura.
- Tratar toda integração externa como não confiável.

## Branding

Ao implementar uma interface, preservar a exigência do selo oficial ABC Solutions no rodapé, centralizado, responsivo, com texto alternativo e a assinatura **“Developed by Abc Solutions | Built with quality and care”**. O asset deve ser copiado para este projeto somente quando autorizado, com origem registrada; não referenciar o caminho de outro projeto em produção.

## Critério de conclusão

Uma tarefa só pode ser declarada concluída após revisar escopo, testes/verificações, documentação, segurança, arquivos sensíveis e estado Git. Lacunas devem ser informadas, nunca ocultadas.
