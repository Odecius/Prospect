# Política do score v1

O score é uma avaliação humana assistida, explicável e não automatiza decisões comerciais.

- `fit`: adequação comercial, peso 40%;
- `reputation`: reputação observada, peso 30%;
- `digital_gap`: oportunidade decorrente da lacuna digital, peso 30%;
- cada componente aceita 0–100 ou ausência explícita;
- o total arredondado só existe quando os três componentes foram avaliados;
- justificativa, componentes, pesos, versão, ator e horário são imutáveis;
- recálculo cria novo registro; histórico nunca é sobrescrito;
- versão inicial: `v1-human-40-30-30`.

O resultado apenas ordena trabalho para revisão humana. Não autoriza contato, não altera pipeline e não substitui análise profissional.
