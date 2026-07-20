# Políticas aprovadas para a Sprint 3

**Estado:** aprovadas por delegação explícita em 2026-07-20.

## Taxonomia inicial

A taxonomia do MVP é controlada, plana e expansível. Subcategorias ficam fora da Sprint 3. As 15 categorias iniciais são: Alimentação e bebidas; Comércio varejista; Serviços profissionais; Saúde e bem-estar; Beleza e estética; Construção e serviços para imóveis; Automotivo; Educação e cursos; Hospedagem e turismo; Tecnologia e serviços digitais; Cultura, lazer e eventos; Indústria e produção; Transporte e logística; Serviços para animais; Outros.

Nomes e slugs normalizados são únicos. Categorias utilizadas não são apagadas: podem ser desativadas, preservando os vínculos existentes. Somente o administrador pode criar, renomear ou desativar categorias. A categoria `Outros` é única. Categorias externas futuras exigirão mapeamento humano e preservação do valor e da fonte originais.

As categorias iniciais serão criadas por seed versionada na migration da Sprint 3. Similaridade de nomes gerará aviso quando a razão normalizada for igual ou superior a 0,85; não haverá bloqueio por similaridade.

## Privacidade e LGPD

A Sprint 3 armazena somente dados empresariais mínimos, origem e auditoria operacional. Representantes, contatos pessoais, dados sensíveis, scraping, importações e atividades de contato ficam fora do escopo. Campos livres não serão introduzidos nesta sprint.

As bases legais permanecem sujeitas a validação jurídica profissional. Legítimo interesse, consentimento, procedimentos preliminares, obrigação legal e exercício regular de direitos são alternativas, não decisões definitivas.

Prazos conservadores de referência: revisão de prospect sem atividade após 12 meses; com interação, após 24 meses; logs técnicos por 90 dias; auditoria de segurança por 12 meses; backups por 30 a 90 dias. Esses prazos são configuráveis e exigem validação jurídica antes da produção. `DO_NOT_CONTACT` deve ser respeitado imediatamente e preservado com identificadores mínimos pelo tempo necessário para impedir novo contato.

O administrador é o responsável operacional inicial por acesso, correção, exportação, arquivamento e encaminhamento de incidentes. Exclusão física e exportação serão aprovadas e implementadas em fase própria; a Sprint 3 implementa arquivamento reversível e preserva autoria e horários.

## Duplicidade

Não existe eliminação, sobrescrita ou mesclagem automática. Correspondências são classificadas como exatas, prováveis, possíveis ou distintas.

Na Sprint 3, CNPJ normalizado válido e repetido é uma correspondência exata e bloqueia o novo cadastro. Nome normalizado igual na mesma cidade e UF é uma provável duplicidade: gera aviso explicável, mas permite continuar mediante confirmação humana. Os demais sinais — telefone, domínio, perfil, endereço e referência externa — entram na Sprint 4.

CNPJs diferentes não autorizam mesclagem automática e exigirão revisão especial no fluxo futuro. A entidade persistente de candidatos, os limiares avançados e a operação de mesclagem pertencem à Sprint 4. A mesclagem futura deverá preservar contatos, fontes, atividades, scores, auditorias, documentos, identificadores anteriores, ator, horário e justificativa.

## Validação jurídica pendente

Antes do uso comercial em produção, exigem avaliação profissional: base legal por finalidade; teste de legítimo interesse; avisos de transparência; retenção e exclusão; empresários individuais; canais de contato; direitos dos titulares; fontes externas; incidentes; operadores e transferências internacionais.
