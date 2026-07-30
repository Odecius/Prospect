let csrfToken = "";
let companies = [];
let selectedCompany = null;
let currentPage = 1;
let externalCursor = null;

const byId = (id) => document.getElementById(id);
const show = (element, visible) => element.classList.toggle("hidden", !visible);

function notify(text) {
  byId("message").textContent = text;
  show(byId("message"), Boolean(text));
}

async function api(path, options = {}) {
  const headers = { ...(options.headers || {}) };
  if (options.body) headers["Content-Type"] = "application/json";
  if (options.method && options.method !== "GET") headers["X-CSRF-Token"] = csrfToken;
  const response = await fetch(path, { ...options, headers });
  if (response.status === 204) return null;
  const body = await response.json();
  if (!response.ok) throw { status: response.status, body };
  return body;
}

async function initialize() {
  const session = await api("/auth/session");
  if (!session.authenticated) return setAuthenticated(false);
  csrfToken = session.csrf_token;
  setAuthenticated(true);
  await loadReferencesAndCompanies();
}

function setAuthenticated(authenticated) {
  show(byId("login-panel"), !authenticated);
  show(byId("app-panel"), authenticated);
  show(byId("logout"), authenticated);
  if (authenticated && !byId("validation-start").value) setDefaultValidationPeriod();
}

function setDefaultValidationPeriod() {
  const end = new Date();
  const start = new Date(end);
  start.setUTCDate(start.getUTCDate() - 13);
  byId("validation-start").value = start.toISOString().slice(0, 10);
  byId("validation-end").value = end.toISOString().slice(0, 10);
}

async function loadReferencesAndCompanies() {
  const [categories, sources, searchResult, candidates, dashboard] = await Promise.all([
    api("/api/categories"), api("/api/sources"), searchCompanies(), api("/api/duplicate-candidates"),
    api("/api/reporting/dashboard")
  ]);
  fillSelect(byId("category"), categories);
  fillSelect(byId("search-category"), categories, "Todas");
  fillSelect(byId("source"), sources);
  companies = searchResult.items;
  renderCompanies();
  renderPager(searchResult);
  renderCandidates(candidates);
  renderDashboard(dashboard);
}

async function searchCompanies() {
  const params = new URLSearchParams({ page: currentPage, page_size: 25, sort: byId("search-sort").value });
  if (byId("search-query").value) params.set("query", byId("search-query").value);
  if (byId("search-state").value) params.set("state_code", byId("search-state").value);
  if (byId("search-category").value) params.set("category_id", byId("search-category").value);
  if (byId("search-pipeline").value) params.set("pipeline_status", byId("search-pipeline").value);
  if (byId("include-archived").checked) params.set("include_archived", "true");
  return api(`/api/companies-search?${params}`);
}

function renderPager(result) {
  const pages = Math.max(1, Math.ceil(result.total / result.page_size));
  byId("page-status").textContent = `Página ${result.page} de ${pages} — ${result.total} empresas`;
  byId("previous-page").disabled = result.page <= 1;
  byId("next-page").disabled = result.page >= pages;
}

async function searchExternal(cursor = null) {
  const result = await api("/api/external/google-places/search", { method: "POST", body: JSON.stringify({ term: byId("external-term").value, city: byId("external-city").value, state_code: byId("external-state").value, cursor }) });
  externalCursor = result.next_cursor;
  const container = byId("external-results"); container.replaceChildren();
  if (!result.items.length) container.textContent = "Nenhum resultado.";
  for (const place of result.items) {
    const card = document.createElement("article"); card.className = "external-place";
    const title = document.createElement("h3"); title.textContent = place.name || "Nome não informado"; card.append(title);
    const details = document.createElement("p"); details.textContent = `${place.formatted_address || "Endereço não informado"} — avaliação ${place.rating ?? "ausente"} (${place.user_rating_count ?? "sem contagem"})`; card.append(details);
    const website = document.createElement("p"); website.textContent = place.website_uri ? "Website informado" : "Website ausente"; card.append(website);
    const attribution = document.createElement("small"); attribution.setAttribute("translate", "no"); attribution.textContent = "Google Maps"; card.append(attribution);
    if (place.attributions.length) { const thirdParty = document.createElement("small"); thirdParty.textContent = ` — ${place.attributions.join(", ")}`; card.append(thirdParty); }
    const select = document.createElement("select"); select.setAttribute("aria-label", `Empresa interna para ${place.name || place.external_id}`);
    const empty = document.createElement("option"); empty.value = ""; empty.textContent = "Selecione uma empresa interna"; select.append(empty);
    for (const company of companies.filter((item) => !item.archived)) { const option = document.createElement("option"); option.value = company.id; option.textContent = company.name; select.append(option); }
    card.append(select);
    const link = document.createElement("button"); link.type = "button"; link.textContent = "Vincular Place ID após revisão";
    link.addEventListener("click", async () => { if (!select.value) return notify("Selecione uma empresa interna."); await api("/api/external/google-places/link", { method: "POST", body: JSON.stringify({ company_id: select.value, place_id: place.external_id }) }); notify("Place ID vinculado; demais dados externos não foram persistidos."); });
    card.append(link); container.append(card);
  }
  show(byId("external-next"), Boolean(externalCursor));
}

function fillSelect(select, values, placeholder = null) {
  const previous = select.value;
  select.replaceChildren();
  if (placeholder) { const option = document.createElement("option"); option.value = ""; option.textContent = placeholder; select.append(option); }
  for (const value of values) {
    const option = document.createElement("option");
    option.value = value.id;
    option.textContent = value.name;
    select.append(option);
  }
  if ([...select.options].some((option) => option.value === previous)) select.value = previous;
}

function renderDashboard(data) {
  const metrics = [
    ["Ativas", data.total_active], ["Sem website", data.without_website], ["Com score", data.with_score],
    ["Auditadas", data.with_completed_audit], ["Conteúdo aprovado", data.with_approved_content],
    ["Não contatar", data.do_not_contact]
  ];
  const container = byId("dashboard-metrics"); container.replaceChildren();
  for (const [label, value] of metrics) {
    const card = document.createElement("div"); card.className = "metric";
    const number = document.createElement("strong"); number.textContent = value; card.append(number);
    const text = document.createElement("span"); text.textContent = label; card.append(text); container.append(card);
  }
  const pipeline = byId("dashboard-pipeline"); pipeline.replaceChildren();
  for (const [status, count] of Object.entries(data.by_pipeline).sort()) {
    const item = document.createElement("span"); item.textContent = `${status}: ${count}`; pipeline.append(item);
  }
}

async function loadValidationSnapshot() {
  const startedAt = `${byId("validation-start").value}T00:00:00Z`;
  const inclusiveEnd = new Date(`${byId("validation-end").value}T00:00:00Z`);
  inclusiveEnd.setUTCDate(inclusiveEnd.getUTCDate() + 1);
  const params = new URLSearchParams({ started_at: startedAt, ended_at: inclusiveEnd.toISOString() });
  const data = await api(`/api/reporting/validation?${params}`);
  const percentage = (value) => value === null ? "—" : `${(value * 100).toFixed(1)}%`;
  const metrics = [
    ["Empresas criadas", data.companies_created],
    ["Com score", data.companies_scored],
    ["Com atividade", data.companies_with_activity],
    ["Contatadas", data.companies_contacted],
    ["Responderam", data.companies_replied],
    ["Com reunião", data.companies_with_meeting],
    ["Avançaram", data.companies_progressed],
    ["Ganhas", data.companies_won],
    ["Não contatar", data.companies_marked_do_not_contact],
    ["Resposta/contato", percentage(data.contact_response_rate)],
    ["Progressão/com score", percentage(data.score_progression_rate)]
  ];
  const container = byId("validation-metrics"); container.replaceChildren();
  for (const [label, value] of metrics) {
    const card = document.createElement("div"); card.className = "metric";
    const number = document.createElement("strong"); number.textContent = value; card.append(number);
    const text = document.createElement("span"); text.textContent = label; card.append(text); container.append(card);
  }
}

async function exportCompanies() {
  if (!window.confirm("Exportar até 500 empresas ativas do segmento atual? O arquivo não incluirá contatos, CNPJ ou notas.")) return;
  const payload = {
    query: byId("search-query").value || null,
    category_id: byId("search-category").value || null,
    state_code: byId("search-state").value || null,
    pipeline_status: byId("search-pipeline").value || null
  };
  const response = await fetch("/api/reporting/companies.csv", {
    method: "POST",
    headers: { "Content-Type": "application/json", "X-CSRF-Token": csrfToken },
    body: JSON.stringify(payload)
  });
  if (!response.ok) { const error = await response.json(); return notify(error.detail || "Exportação indisponível."); }
  const url = URL.createObjectURL(await response.blob());
  const link = document.createElement("a"); link.href = url; link.download = "abc-prospect-segmento.csv"; link.click();
  URL.revokeObjectURL(url); notify("Exportação manual concluída e auditada.");
}

function renderCompanies() {
  const tbody = byId("companies");
  tbody.replaceChildren();
  show(byId("empty"), companies.length === 0);
  for (const company of companies) {
    const row = document.createElement("tr");
    row.classList.toggle("archived", company.archived);
    for (const text of [company.name, `${company.city}/${company.state_code}`, company.pipeline_status]) {
      const cell = document.createElement("td"); cell.textContent = text; row.append(cell);
    }
    const actions = document.createElement("td"); actions.className = "actions";
    const edit = document.createElement("button"); edit.type = "button"; edit.textContent = "Editar";
    edit.addEventListener("click", () => editCompany(company)); actions.append(edit);
    const contacts = document.createElement("button"); contacts.type = "button"; contacts.className = "secondary"; contacts.textContent = "Contatos";
    contacts.addEventListener("click", () => selectCompanyContacts(company)); actions.append(contacts);
    const score = document.createElement("button"); score.type = "button"; score.className = "secondary"; score.textContent = "Avaliar";
    score.addEventListener("click", () => evaluateCompany(company)); actions.append(score);
    const status = document.createElement("button"); status.type = "button"; status.className = "secondary"; status.textContent = "Mudar estado";
    status.addEventListener("click", () => transitionCompany(company)); actions.append(status);
    const drafts = document.createElement("button"); drafts.type = "button"; drafts.className = "secondary"; drafts.textContent = "Rascunhos IA";
    drafts.addEventListener("click", () => selectCompanyDrafts(company)); actions.append(drafts);
    if (!company.archived) {
      const archive = document.createElement("button"); archive.type = "button"; archive.className = "danger"; archive.textContent = "Arquivar";
      archive.addEventListener("click", () => archiveCompany(company)); actions.append(archive);
    }
    row.append(actions); tbody.append(row);
  }
}

async function selectCompanyDrafts(company) {
  selectedCompany = company;
  byId("ai-draft-company").textContent = `Empresa selecionada: ${company.name}`;
  const drafts = await api(`/api/companies/${company.id}/message-drafts`);
  const container = byId("message-drafts"); container.replaceChildren();
  if (!company.archived && company.pipeline_status !== "DO_NOT_CONTACT") {
    const types = [["COMMERCIAL_INTRODUCTION", "Mensagem"], ["COMMERCIAL_DIAGNOSTIC", "Diagnóstico"], ["PROPOSAL_DRAFT", "Proposta"]];
    for (const [type, label] of types) {
      const generate = document.createElement("button"); generate.type = "button";
      generate.textContent = `Gerar ${label.toLowerCase()}`;
      generate.addEventListener("click", () => generateMessageDraft(company, type)); container.append(generate);
    }
  }
  if (!drafts.length) { const empty = document.createElement("p"); empty.textContent = "Nenhum rascunho registrado."; container.append(empty); }
  for (const draft of drafts) container.append(renderMessageDraft(draft, company));
}

function renderMessageDraft(draft, company) {
  const card = document.createElement("article"); card.className = "candidate";
  const heading = document.createElement("strong"); heading.textContent = `${draft.draft_type} — ${draft.status} — ${draft.model}`; card.append(heading);
  const content = draft.reviewed_content || draft.generated_content;
  const subject = document.createElement("p"); subject.textContent = `Assunto: ${content.subject}`; card.append(subject);
  const body = document.createElement("p"); body.className = "draft-body"; body.textContent = content.body; card.append(body);
  if (draft.generated_content.evidence_refs?.length) {
    const evidence = document.createElement("small"); evidence.textContent = `Evidências: ${draft.generated_content.evidence_refs.join(", ")}`; card.append(evidence);
  }
  const note = document.createElement("small"); note.textContent = "Rascunho interno; não enviado automaticamente."; card.append(note);
  if (draft.status === "DRAFT" && company.pipeline_status !== "DO_NOT_CONTACT") {
    const approve = document.createElement("button"); approve.type = "button"; approve.textContent = "Revisar e aprovar";
    approve.addEventListener("click", () => reviewMessageDraft(draft, company, "APPROVED")); card.append(approve);
    const reject = document.createElement("button"); reject.type = "button"; reject.className = "danger"; reject.textContent = "Rejeitar";
    reject.addEventListener("click", () => reviewMessageDraft(draft, company, "REJECTED")); card.append(reject);
  }
  return card;
}

async function generateMessageDraft(company, draftType) {
  if (!window.confirm("Gerar rascunho usando somente dados empresariais mínimos?")) return;
  try {
    await api(`/api/companies/${company.id}/message-drafts`, { method: "POST", body: JSON.stringify({ draft_type: draftType }) });
    notify("Rascunho gerado. Revise antes de qualquer uso."); await selectCompanyDrafts(company);
  } catch (error) { notify(error.body?.detail || "Geração de IA indisponível."); }
}

async function reviewMessageDraft(draft, company, decision) {
  const reason = window.prompt("Justificativa da revisão:"); if (!reason) return;
  const payload = { decision, reason };
  if (decision === "APPROVED") {
    const subject = window.prompt("Revise o assunto:", draft.generated_content.subject); if (!subject) return;
    const body = window.prompt("Revise o corpo:", draft.generated_content.body); if (!body) return;
    payload.subject = subject; payload.body = body;
  }
  await api(`/api/message-drafts/${draft.id}/review`, { method: "POST", body: JSON.stringify(payload) });
  notify(decision === "APPROVED" ? "Rascunho aprovado, mas não enviado." : "Rascunho rejeitado.");
  await selectCompanyDrafts(company);
}

async function evaluateCompany(company) {
  const fit = window.prompt("Adequação (0–100; deixe vazio se ausente):"); if (fit === null) return;
  const reputation = window.prompt("Reputação (0–100; deixe vazio se ausente):"); if (reputation === null) return;
  const digitalGap = window.prompt("Lacuna digital (0–100; deixe vazio se ausente):"); if (digitalGap === null) return;
  const rationale = window.prompt("Justificativa da avaliação:"); if (!rationale) return;
  const value = (item) => item === "" ? null : Number(item);
  const result = await api(`/api/companies/${company.id}/scores`, { method: "POST", body: JSON.stringify({ fit: value(fit), reputation: value(reputation), digital_gap: value(digitalGap), rationale }) });
  notify(`Avaliação registrada: ${result.total ?? "incompleta"}.`);
}

async function transitionCompany(company) {
  const newStatus = window.prompt("Novo estado (ex.: QUALIFIED, DO_NOT_CONTACT, ARCHIVED):"); if (!newStatus) return;
  const reason = window.prompt("Justificativa obrigatória:"); if (!reason) return;
  await api(`/api/companies/${company.id}/transition`, { method: "POST", body: JSON.stringify({ new_status: newStatus.toUpperCase(), reason }) });
  notify("Estado alterado e registado no histórico."); await loadReferencesAndCompanies();
}

async function selectCompanyContacts(company) {
  selectedCompany = company;
  byId("contact-company-id").value = company.id;
  byId("contact-company").textContent = company.name;
  show(byId("contact-form"), !company.archived);
  const contacts = await api(`/api/companies/${company.id}/contacts`);
  const list = byId("contacts"); list.replaceChildren();
  const auditOptions = byId("website-audit-options"); auditOptions.replaceChildren();
  byId("website-audit-company").textContent = `Empresa selecionada: ${company.name}`;
  for (const contact of contacts) {
    const item = document.createElement("li");
    item.textContent = `${contact.contact_type}: ${contact.value}${contact.invalidated ? " (inválido)" : ""}`;
    if (!contact.invalidated) {
      const invalidate = document.createElement("button"); invalidate.type = "button"; invalidate.className = "danger compact"; invalidate.textContent = "Invalidar";
      invalidate.addEventListener("click", async () => { await api(`/api/contacts/${contact.id}/invalidate`, { method: "POST" }); await selectCompanyContacts(company); });
      item.append(invalidate);
    }
    list.append(item);
    if (contact.contact_type === "WEBSITE" && !contact.invalidated && !company.archived) {
      const auditButton = document.createElement("button"); auditButton.type = "button"; auditButton.className = "secondary";
      auditButton.textContent = `Auditar ${contact.value}`;
      auditButton.addEventListener("click", () => runWebsiteAudit(company, contact));
      auditOptions.append(auditButton);
    }
  }
  if (!auditOptions.children.length) auditOptions.textContent = "Cadastre um contato WEBSITE ativo para habilitar a auditoria.";
  await loadWebsiteAudits(company);
}

async function loadWebsiteAudits(company) {
  const audits = await api(`/api/companies/${company.id}/website-audits`);
  const container = byId("website-audits"); container.replaceChildren();
  if (!audits.length) { container.textContent = "Nenhuma auditoria registrada para esta empresa."; return; }
  for (const audit of audits) {
    const card = document.createElement("article"); card.className = "candidate";
    const heading = document.createElement("strong");
    heading.textContent = `${audit.status} — ${new Date(audit.created_at).toLocaleString("pt-BR")}`; card.append(heading);
    const summary = document.createElement("p");
    summary.textContent = audit.status === "COMPLETED"
      ? `HTTP ${audit.http_status}; ${audit.duration_ms} ms; HTTPS: ${audit.findings.uses_https ? "sim" : "não"}; responsivo declarado: ${audit.findings.viewport_present ? "sim" : "não"}.`
      : `Falha controlada: ${audit.error_code}.`;
    card.append(summary);
    const note = document.createElement("small");
    note.textContent = "Snapshot informativo; nenhuma decisão ou score foi alterado automaticamente."; card.append(note);
    container.append(card);
  }
}

async function runWebsiteAudit(company, contact) {
  if (!window.confirm(`Auditar somente a página inicial de ${contact.value}?`)) return;
  try {
    const audit = await api(`/api/companies/${company.id}/website-audits`, {
      method: "POST", body: JSON.stringify({ contact_id: contact.id })
    });
    notify(audit.status === "COMPLETED" ? "Auditoria concluída e registrada." : `Auditoria terminou com falha controlada: ${audit.error_code}.`);
    await loadWebsiteAudits(company);
  } catch (error) { notify(error.body?.detail || "Não foi possível auditar o website."); }
}

function companyName(id) { return companies.find((company) => company.id === id)?.name || id; }

function renderCandidates(candidates) {
  const container = byId("duplicate-candidates"); container.replaceChildren();
  const open = candidates.filter((item) => item.status !== "CLOSED");
  if (!open.length) { container.textContent = "Nenhuma correspondência pendente."; return; }
  for (const candidate of open) {
    const card = document.createElement("article"); card.className = "candidate";
    const summary = document.createElement("p"); summary.textContent = `${companyName(candidate.company_a_id)} × ${companyName(candidate.company_b_id)} — ${candidate.level}`; card.append(summary);
    const evidence = document.createElement("small"); evidence.textContent = `Sinais: ${JSON.stringify(candidate.signals)}`; card.append(evidence);
    if (candidate.status === "OPEN") {
      const distinct = document.createElement("button"); distinct.type = "button"; distinct.className = "secondary compact"; distinct.textContent = "São distintos";
      distinct.addEventListener("click", () => reviewCandidate(candidate.id, "DISTINCT")); card.append(distinct);
      const confirm = document.createElement("button"); confirm.type = "button"; confirm.className = "compact"; confirm.textContent = "Confirmar duplicidade";
      confirm.addEventListener("click", () => reviewCandidate(candidate.id, "CONFIRMED_DUPLICATE")); card.append(confirm);
    } else if (candidate.status === "CONFIRMED_DUPLICATE" || candidate.status === "MERGE_REQUESTED") {
      const merge = document.createElement("button"); merge.type = "button"; merge.className = "danger compact"; merge.textContent = "Mesclar mantendo a primeira";
      merge.addEventListener("click", () => mergeCandidate(candidate)); card.append(merge);
    }
    container.append(card);
  }
}

async function reviewCandidate(id, status) {
  const reason = window.prompt("Informe a justificativa da revisão:");
  if (!reason) return;
  await api(`/api/duplicate-candidates/${id}/review`, { method: "POST", body: JSON.stringify({ status, reason }) });
  await loadReferencesAndCompanies();
}

async function mergeCandidate(candidate) {
  const reason = window.prompt(`A empresa ${companyName(candidate.company_b_id)} será arquivada. Informe a justificativa:`);
  if (!reason) return;
  if (!window.confirm("Confirmar a mesclagem? O histórico será preservado.")) return;
  await api(`/api/duplicate-candidates/${candidate.id}/merge`, { method: "POST", body: JSON.stringify({ survivor_company_id: candidate.company_a_id, reason }) });
  notify("Empresas mescladas com histórico preservado."); await loadReferencesAndCompanies();
}

function editCompany(company) {
  byId("company-id").value = company.id;
  byId("name").value = company.name;
  byId("category").value = company.category_id;
  byId("city").value = company.city;
  byId("state").value = company.state_code;
  byId("tax-id").value = company.tax_id || "";
  byId("form-title").textContent = "Editar empresa";
  show(byId("cancel-edit"), true);
  window.scrollTo({ top: 0, behavior: "smooth" });
}

function resetForm() {
  byId("company-form").reset(); byId("company-id").value = "";
  byId("form-title").textContent = "Cadastrar empresa"; show(byId("cancel-edit"), false);
}

async function saveCompany(confirmDuplicate = false) {
  const id = byId("company-id").value;
  const payload = {
    name: byId("name").value, category_id: byId("category").value, city: byId("city").value,
    state_code: byId("state").value, source_id: byId("source").value,
    source_url: byId("source-url").value || null, tax_id: byId("tax-id").value || null,
    source_external_id: byId("source-external-id").value || null,
    source_raw_name: byId("source-raw-name").value || null,
    confirm_possible_duplicate: confirmDuplicate
  };
  try {
    await api(id ? `/api/companies/${id}` : "/api/companies", { method: id ? "PUT" : "POST", body: JSON.stringify(payload) });
    resetForm(); notify("Empresa guardada com sucesso."); await loadReferencesAndCompanies();
  } catch (error) {
    if (error.status === 409 && error.body.detail?.type === "possible_duplicate") {
      const confirmed = window.confirm(`${error.body.detail.reason} Deseja manter os registros separados?`);
      if (confirmed) return saveCompany(true);
    }
    notify(typeof error.body?.detail === "string" ? error.body.detail : JSON.stringify(error.body?.detail || "Erro ao guardar."));
  }
}

async function archiveCompany(company) {
  if (!window.confirm(`Arquivar ${company.name}?`)) return;
  await api(`/api/companies/${company.id}/archive`, { method: "POST" });
  notify("Empresa arquivada."); await loadReferencesAndCompanies();
}

byId("login-form").addEventListener("submit", async (event) => {
  event.preventDefault(); notify("");
  try {
    const session = await api("/auth/login", { method: "POST", body: JSON.stringify({ email: byId("email").value, password: byId("password").value }) });
    csrfToken = session.csrf_token; byId("password").value = ""; setAuthenticated(true); await loadReferencesAndCompanies();
  } catch { notify("Credenciais inválidas."); }
});
byId("company-form").addEventListener("submit", (event) => { event.preventDefault(); saveCompany(); });
byId("contact-form").addEventListener("submit", async (event) => {
  event.preventDefault();
  try {
    await api(`/api/companies/${byId("contact-company-id").value}/contacts`, { method: "POST", body: JSON.stringify({
      contact_type: byId("contact-type").value, value: byId("contact-value").value,
      is_primary: byId("contact-primary").checked, person_name: byId("person-name").value || null,
      job_title: byId("job-title").value || null
    }) });
    byId("contact-form").reset(); notify("Contato adicionado."); await selectCompanyContacts(selectedCompany); await loadReferencesAndCompanies();
  } catch (error) { notify(error.body?.detail || "Erro ao adicionar contato."); }
});
byId("search-form").addEventListener("submit", async (event) => { event.preventDefault(); currentPage = 1; await loadReferencesAndCompanies(); });
byId("validation-form").addEventListener("submit", async (event) => {
  event.preventDefault();
  try { await loadValidationSnapshot(); } catch (error) { notify(error.body?.detail || "Validação indisponível."); }
});
byId("previous-page").addEventListener("click", async () => { currentPage -= 1; await loadReferencesAndCompanies(); });
byId("next-page").addEventListener("click", async () => { currentPage += 1; await loadReferencesAndCompanies(); });
byId("external-search-form").addEventListener("submit", async (event) => { event.preventDefault(); externalCursor = null; try { await searchExternal(); } catch (error) { notify(error.body?.detail || "Pesquisa externa indisponível."); } });
byId("external-next").addEventListener("click", async () => { try { await searchExternal(externalCursor); } catch (error) { notify(error.body?.detail || "Não foi possível carregar a próxima página."); } });
byId("export-companies").addEventListener("click", () => exportCompanies().catch(() => notify("Exportação indisponível.")));
byId("cancel-edit").addEventListener("click", resetForm);
byId("logout").addEventListener("click", async () => { await api("/auth/logout", { method: "POST" }); csrfToken = ""; setAuthenticated(false); });

initialize().catch(() => notify("Não foi possível iniciar a aplicação."));
