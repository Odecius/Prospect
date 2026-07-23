# Sprint 15 — protocolo de validação comercial

## Estado

O protocolo e a medição técnica estão prontos. O piloto real ainda não foi executado e
nenhum resultado foi presumido. O produto permanece em 96% até existir amostra suficiente,
feedback humano e decisão registrada.

## Pergunta de validação

O ABC Prospect torna a seleção e o acompanhamento de prospects mais consistentes e úteis,
sem piorar o tempo de trabalho nem enfraquecer os controles de privacidade e não contato?

Volume de cadastros, contatos ou mensagens, isoladamente, não prova valor.

## Período e amostra conservadores

- período padrão: 14 dias corridos, prorrogável até atingir a amostra mínima;
- máximo por retrato técnico: 90 dias;
- mínimo: 20 empresas realmente revisadas, 15 com score e 8 elegíveis efetivamente
  contatadas;
- incluir resultados desfavoráveis, `LOST` e `DO_NOT_CONTACT`;
- não completar a amostra com registros fictícios, duplicados ou contatos desnecessários;
- registrar interrupções, mudanças de processo e fatores externos.

Se a amostra não for atingida, o resultado será `INCONCLUSIVO`, nunca sucesso presumido.

## Métricas reproduzíveis

A área “Validação comercial” e `GET /api/reporting/validation` exigem início e fim com fuso
horário e retornam:

- empresas criadas, pontuadas e com atividade;
- empresas contatadas, com resposta, reunião, avanço, ganho e `DO_NOT_CONTACT`;
- taxa descritiva de resposta por empresa contatada;
- proporção de empresas pontuadas que depois tiveram progressão positiva no período.

As contagens são por empresa distinta. O fim do período da API é exclusivo; a interface
converte a data final inclusiva. Associação entre score e progressão não demonstra
causalidade, e denominador zero produz taxa ausente.

## Medições humanas obrigatórias

Antes do piloto, cronometre cinco tarefas equivalentes no processo anterior. Durante o
piloto, cronometre ao menos cinco tarefas comparáveis: cadastrar/revisar, pesquisar,
priorizar e registrar próximo passo. Registre somente duração e tipo da tarefa, sem dados
do prospect.

Ao final, a pessoa operadora responde de 1 a 5:

1. Foi fácil encontrar e atualizar uma empresa?
2. A origem e o histórico deram confiança?
3. O score ajudou a priorizar sem esconder sua explicação?
4. O pipeline tornou o próximo passo mais claro?
5. Os bloqueios, especialmente `DO_NOT_CONTACT`, foram claros?
6. O sistema reduziu retrabalho?

Registrar também até três dificuldades, três benefícios e workarounds usados, sem nomes,
contatos ou conteúdo comercial de terceiros.

## Avaliação do score

Selecione de modo reproduzível cinco empresas de cada faixa `0–39`, `40–69` e `70–100`,
quando houver. Antes de olhar o resultado comercial, uma pessoa revisa as evidências e
classifica a prioridade como baixa, média ou alta. Compare:

- concordância entre faixa e revisão humana;
- progressão posterior por faixa;
- casos em que dados ausentes distorceram o resultado;
- falsos positivos e falsos negativos explicados.

Não reajustar pesos durante a mesma amostra. Se houver poucos casos por faixa, declarar a
análise inconclusiva.

## Segurança e integridade

São critérios de parada imediata:

- contato registrado após `DO_NOT_CONTACT`;
- envio ou decisão automatizada não autorizada;
- segredo ou dado pessoal desnecessário em logs/exportações;
- perda de histórico ou sobrescrita sem revisão;
- acesso fora das pessoas ou rede autorizadas.

Incidentes não podem ser compensados por melhores métricas comerciais.

## Decisão final

- `CONTINUAR_EM_MANUTENÇÃO`: amostra suficiente, nenhum critério de parada, fluxo não ficou
  mais lento de forma material e feedback indica utilidade;
- `CORRIGIR_E_REVALIDAR`: não houve incidente crítico, mas usabilidade, tempo, qualidade
  do score ou amostra são insuficientes;
- `INTERROMPER`: ocorreu risco crítico não resolvido ou o processo permaneceu
  materialmente pior após correções razoáveis;
- `INCONCLUSIVO`: período ou amostra insuficientes.

A decisão é humana e deve citar evidências e limitações. A API nunca escolhe o resultado.

## Registro de encerramento

Copiar e preencher:

```text
Período:
Responsável:
Amostra (criadas / pontuadas / contatadas):
Tempo anterior (mediana):
Tempo com ABC Prospect (mediana):
Resposta / reunião / avanço / ganho:
DO_NOT_CONTACT e incidentes:
Concordância do score:
Resumo do feedback:
Limitações e vieses:
Melhorias P0 / P1 / P2:
Decisão: CONTINUAR_EM_MANUTENÇÃO | CORRIGIR_E_REVALIDAR | INTERROMPER | INCONCLUSIVO
Justificativa:
Data e responsável pela decisão:
```

Somente após esse registro, com pendências críticas resolvidas, a Sprint 15 pode ser
encerrada e o Produto Interno declarado 100%.
