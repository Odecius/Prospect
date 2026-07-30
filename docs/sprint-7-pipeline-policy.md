# Política de pipeline e atividades

A progressão normal ocorre etapa a etapa: `NEW`, `QUALIFIED`, `CONTACTED`, `REPLIED`, `MEETING`, `PROPOSAL_SENT`, `NEGOTIATION` e `WON`. `LOST` pode encerrar qualquer etapa prevista pela matriz implementada.

`DO_NOT_CONTACT` e `ARCHIVED` interrompem qualquer estado ativo. Estados terminais só podem reabrir em `NEW`, sempre com justificativa. Cada alteração registra estado anterior, novo estado, ator, horário e motivo.

Atividades aceitas: nota, pesquisa, contato, resposta, reunião e próximo passo. Em `DO_NOT_CONTACT`, o servidor rejeita atividades do tipo contato. O sistema não envia mensagens.
