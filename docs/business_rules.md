# Regras de negócio

Este documento centraliza as regras de negócio do ABC Prospect sem substituir suas fontes canônicas. Decisões são aprovadas em [`../DECISIONS.md`](../DECISIONS.md), o modelo conceitual está em [`../DATA_MODEL.md`](../DATA_MODEL.md), as fases e seus bloqueios estão em [`../ROADMAP.md`](../ROADMAP.md), os controles de segurança e privacidade estão em [`../SECURITY.md`](../SECURITY.md) e os termos oficiais estão em [`glossary.md`](glossary.md).

Uma regra marcada como **pendente** não pode ser presumida na implementação. A decisão correspondente deve ser documentada e aprovada antes da fase que depende dela.

## Cadastro de empresas

### Regras aprovadas

- nome, categoria, cidade, UF e origem são obrigatórios;
- `country_code` começa como `BR`;
- `pipeline_status` começa como `NEW`;
- CNPJ, website, telefone, email corporativo e observações são opcionais;
- ao menos uma referência de origem válida deve ser criada na mesma operação do cadastro;
- a ausência de score não impede cadastro, edição, consulta, pesquisa ou qualificação;
- dados pessoais não são necessários para completar o cadastro mínimo;
- uma empresa pode ser arquivada, mas seu histórico relevante deve permanecer rastreável conforme a política de retenção.

### Validação dos dados

- nome não pode ser vazio após normalização;
- categoria deve existir e estar ativa;
- cidade deve usar a forma normalizada definida pela taxonomia geográfica;
- UF deve ser um código oficial brasileiro válido com dois caracteres;
- CNPJ, quando informado, deve ser normalizado e validado antes da persistência;
- email, telefone, domínio e textos usados em busca devem possuir formas normalizadas sem apagar o valor original necessário à exibição;
- URLs devem usar formato válido e protocolos permitidos;
- avaliações devem respeitar a escala aprovada e contagens não podem ser negativas;
- erros devem ser claros para o usuário e não podem expor SQL, stack trace, segredos ou configuração interna.

Os campos e relacionamentos conceituais completos estão em [`../DATA_MODEL.md`](../DATA_MODEL.md).

## Duplicidade de empresas

### Regras aprovadas

1. CNPJ normalizado é um identificador forte e deve ser único quando informado.
2. A combinação de fonte e identificador externo deve ser única quando o identificador existir.
3. Coincidências de telefone, email, domínio, nome e localização geram candidatos para revisão.
4. Nomes iguais, isoladamente, não bloqueiam cadastros incompletos.
5. Casos ambíguos nunca são mesclados automaticamente.
6. A decisão humana deve registrar responsável, horário, evidências e registros envolvidos.
7. Uma mesclagem deve permitir correção segura e preservar proveniência e histórico.

### Pendente antes de concluir a Fase 2

- limiares de similaridade;
- comportamento exato ao encontrar CNPJ ou referência de fonte existentes;
- fluxo de manter separado, vincular, mesclar e desfazer;
- precedência entre valores conflitantes durante a mesclagem.

## Pipeline

### Estados aprovados

`NEW`, `QUALIFIED`, `CONTACTED`, `REPLIED`, `MEETING`, `PROPOSAL_SENT`, `NEGOTIATION`, `WON`, `LOST`, `DO_NOT_CONTACT` e `ARCHIVED`.

### Regras aprovadas

- toda empresa começa em `NEW`;
- o fluxo comercial principal segue por qualificação, contato, resposta, reunião, proposta e negociação, chegando a `WON` ou `LOST`;
- `DO_NOT_CONTACT` interrompe novas abordagens comerciais enquanto esse estado estiver vigente;
- `ARCHIVED` retira a empresa do fluxo ativo sem apagar automaticamente seu histórico;
- toda alteração de status deve registrar ator, horário, estado anterior e estado novo;
- autorização e validação de transição devem ocorrer no servidor.

### Pendente antes de iniciar a Fase 5

- matriz exata de transições permitidas;
- regras de reabertura de `WON`, `LOST`, `DO_NOT_CONTACT` e `ARCHIVED`;
- motivos obrigatórios para encerramento ou bloqueio de contato;
- tipos de atividade e resultados associados às transições.

Nenhuma transição ainda pendente deve ser inferida apenas pela ordem da lista de estados.

## Score

### Regras aprovadas

- cada cálculo cria uma avaliação histórica; resultados anteriores não são sobrescritos;
- cada avaliação registra valor, versão da fórmula, componentes, data e justificativa suficiente;
- o score deve ser explicável e não toma decisões comerciais autonomamente;
- dados ausentes devem ser tratados explicitamente, sem assumir silenciosamente o melhor ou o pior resultado;
- recálculo cria uma nova avaliação e preserva a anterior;
- o score atual é a avaliação válida mais recente;
- nenhuma empresa precisa de score antes da Fase 4.

### Pendente antes de iniciar a Fase 4

- componentes e pesos;
- escala, faixas e arredondamento;
- versão inicial da fórmula;
- tratamento específico de cada dado ausente;
- eventos que permitem ou exigem recálculo;
- aprovação de exemplos reais ou fictícios representativos.

## Arquivamento e retenção

### Regras aprovadas

- arquivar não equivale a excluir;
- uma empresa arquivada sai do fluxo ativo;
- histórico comercial, origem, scores e decisões de duplicidade não devem ser apagados apenas pela mudança para `ARCHIVED`;
- `DO_NOT_CONTACT` não pode ser usado como sinônimo de arquivamento;
- correção, bloqueio e exclusão devem ser possíveis quando legalmente aplicáveis.

### Pendente antes de concluir a Fase 2

- períodos de retenção por tipo de dado;
- condições de anonimização ou exclusão;
- regras de reativação de registros arquivados;
- tratamento de referências históricas quando houver pedido de exclusão.

## Demonstrações

### Regras aprovadas

- uma Demo Website deve ser identificada claramente como demonstração;
- publicação exige revisão e ação humana;
- a demonstração não pode se apresentar como website oficial da empresa;
- direitos de marca, textos, imagens, templates e demais assets devem ser respeitados e rastreados;
- criação, revisão, publicação, expiração e remoção devem ser auditáveis;
- acesso deve permanecer restrito ao necessário.

### Pendente antes de iniciar a Fase 10

- prazo padrão e condições de expiração;
- armazenamento e formato de `storage_reference`;
- processo de publicação e remoção;
- política de acesso e compartilhamento;
- tratamento de demonstrações vinculadas a empresas arquivadas ou `DO_NOT_CONTACT`.

## Propostas

### Regras aprovadas

- propostas pertencem a uma empresa e possuem número e versão auditáveis;
- valores não podem ser negativos e devem registrar moeda;
- toda proposta deve possuir estado e validade quando aplicável;
- revisão humana é obrigatória antes do envio;
- versões enviadas não devem ser alteradas silenciosamente;
- acesso ao documento deve ser protegido;
- envio ou mudança de estado relevante deve gerar atividade comercial rastreável.

### Pendente antes de iniciar a Fase 11

- modelo comercial e itens obrigatórios;
- regra de numeração;
- estados e transições da proposta;
- aprovação interna necessária;
- formato, armazenamento e retenção do documento;
- regras tributárias e comerciais aplicáveis.

## Contatos e atividades comerciais

- contatos devem ser minimizados à finalidade comercial legítima;
- deve-se diferenciar contato corporativo de dado pessoal;
- valor original e valor normalizado devem ser protegidos conforme sua sensibilidade;
- origem e data de obtenção devem ser registradas quando aplicável;
- atividades relevantes devem registrar empresa, tipo, ator e horário;
- conteúdo livre deve ser mínimo e não deve replicar dados sensíveis desnecessariamente;
- nenhuma mensagem pode ser enviada automaticamente ou em massa;
- qualquer mensagem futuramente gerada por IA exige revisão e ação humana explícita.

## Perfis e permissões

### Regra atual

O uso começa com um único administrador autenticado. Todas as operações de negócio devem ser autorizadas no servidor; ocultar controles na interface não constitui autorização.

### Evolução futura pendente

Se houver mais usuários, os papéis e permissões deverão ser aprovados antes da implementação. A futura matriz deve aplicar menor privilégio e, no mínimo, considerar separadamente visualização, edição, alteração de pipeline, mesclagem, revisão de mensagens, publicação de demonstrações, aprovação de propostas e administração.

## LGPD e dados comerciais

- coletar somente dados necessários para finalidade legítima, específica e documentada;
- registrar origem, data de obtenção e finalidade quando aplicável;
- diferenciar dados de pessoa jurídica, contato corporativo e dado pessoal;
- não presumir que um dado publicamente acessível possa ser coletado, reutilizado ou mantido sem limites;
- permitir correção, bloqueio, anonimização ou exclusão quando aplicável;
- definir base legal e retenção antes de concluir a Fase 2;
- respeitar `DO_NOT_CONTACT`, opt-out e restrições de frequência;
- não registrar dados pessoais desnecessários em logs, fixtures ou exemplos;
- não enviar dados a provedores externos ou de IA sem avaliação e aprovação específicas;
- proteger backups e aplicar exclusão conforme a política aprovada;
- revisar termos de uso, licenças, limites e base legal antes de integrar qualquer fonte externa.

Este documento descreve princípios de produto e engenharia, não substitui avaliação jurídica aplicável à operação real.

## Governança das regras

1. Uma nova regra ou alteração relevante deve ser registrada primeiro em `DECISIONS.md`.
2. `DATA_MODEL.md`, `ROADMAP.md`, `SECURITY.md`, este documento e a matriz de rastreabilidade devem ser atualizados conforme o impacto.
3. Somente depois da aprovação documental a implementação correspondente pode começar.
4. Testes devem demonstrar cada regra implementada e suas condições de erro.
5. Divergências entre documentação e implementação interrompem o trabalho até revisão e aprovação.

