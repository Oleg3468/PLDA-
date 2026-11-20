/* PLDA web-сервис — логика интерфейса (vanilla JS, без внешних зависимостей). */

"use strict";

const state = {
  history: [],
  lastQuestion: "",
  currentDocId: null,
  lastMemoMarkdown: "",
  lastMemoFilename: "plda-memo.md",
};

/* ---------- утилиты ---------- */

function $(id) {
  return document.getElementById(id);
}

function escapeHtml(text) {
  const div = document.createElement("div");
  div.textContent = text == null ? "" : String(text);
  return div.innerHTML;
}

async function api(path, options) {
  const response = await fetch(path, options);
  let payload = null;
  try {
    payload = await response.json();
  } catch (error) {
    payload = null;
  }
  if (!response.ok) {
    const detail = payload && payload.detail ? payload.detail : response.status;
    throw new Error(typeof detail === "string" ? detail : JSON.stringify(detail));
  }
  return payload;
}

/* ---------- мини-рендер markdown ---------- */

function renderMarkdown(md) {
  const lines = escapeHtml(md).split("\n");
  const out = [];
  let list = null;

  const closeList = () => {
    if (list) {
      out.push(`</${list}>`);
      list = null;
    }
  };

  const inline = (text) => {
    return text
      .replace(/\[([^\]]+)\]\((https?:[^)\s]+)\)/g,
        '<a href="$2" target="_blank" rel="noopener">$1</a>')
      .replace(/\*\*([^*]+)\*\*/g, "<b>$1</b>")
      .replace(/`([^`]+)`/g, "<code>$1</code>");
  };

  for (const rawLine of lines) {
    const line = rawLine.trimEnd();

    if (!line.trim()) {
      closeList();
      continue;
    }

    const heading = line.match(/^(#{2,4})\s+(.*)$/);
    if (heading) {
      closeList();
      const level = Math.min(heading[1].length + 1, 5);
      out.push(`<h${level}>${inline(heading[2])}</h${level}>`);
      continue;
    }

    const bullet = line.match(/^\s*[-*]\s+(.*)$/);
    if (bullet) {
      if (list !== "ul") {
        closeList();
        out.push("<ul>");
        list = "ul";
      }
      out.push(`<li>${inline(bullet[1])}</li>`);
      continue;
    }

    const ordered = line.match(/^\s*\d+[.)]\s+(.*)$/);
    if (ordered) {
      if (list !== "ol") {
        closeList();
        out.push("<ol>");
        list = "ol";
      }
      out.push(`<li>${inline(ordered[1])}</li>`);
      continue;
    }

    closeList();
    out.push(`<p>${inline(line)}</p>`);
  }
  closeList();
  return out.join("\n");
}

/* ---------- источники ---------- */

function sourceCard(source) {
  const verified = Number(source.verified) === 1;
  const statusTag = verified
    ? `<span class="tag verified">✓ проверено${source.checked_at ? " " + escapeHtml(source.checked_at) : ""}</span>`
    : `<span class="tag unverified">требует проверки</span>`;
  const period = source.effective_from
    ? `${escapeHtml(source.effective_from)}${source.effective_to ? " — " + escapeHtml(source.effective_to) + " (утратил силу)" : ""}`
    : "—";
  const url = source.source_url
    ? `<a href="${escapeHtml(source.source_url)}" target="_blank" rel="noopener">${escapeHtml(source.source_url)}</a>`
    : "—";

  return `<div class="source-card">
    <div class="title">${escapeHtml(source.title)}</div>
    <div class="meta">
      <span class="tag">${escapeHtml(source.source_type)}</span>
      <span class="tag">${escapeHtml(source.jurisdiction)}</span>
      ${statusTag}
    </div>
    <p>${escapeHtml(source.text)}</p>
    <p class="hint">Действие: ${period} · ${url}</p>
  </div>`;
}

function renderSourcesBlock(sources) {
  if (!sources || !sources.length) return "";
  return `<div class="sources-block"><h4>📚 Источники для проверки</h4>${sources
    .map(sourceCard)
    .join("")}</div>`;
}

/* ---------- вкладки ---------- */

document.querySelectorAll(".tab").forEach((tab) => {
  tab.addEventListener("click", () => switchTab(tab.dataset.tab));
});

function switchTab(name) {
  document.querySelectorAll(".tab").forEach((el) =>
    el.classList.toggle("active", el.dataset.tab === name)
  );
  document.querySelectorAll(".panel").forEach((el) =>
    el.classList.toggle("active", el.id === name)
  );
  if (name === "review") {
    loadDocuments();
  }
  if (name === "sources" && !$("sourceResults").innerHTML) {
    searchSources();
  }
}

/* ---------- статус сервиса ---------- */

async function loadHealth() {
  try {
    const health = await api("/api/health");
    const modeBadge = $("modeBadge");
    if (health.llm_configured) {
      modeBadge.textContent = `🤖 LLM: ${health.llm_model}`;
      modeBadge.className = "badge badge-ok";
    } else {
      modeBadge.textContent = "⚙️ Оффлайн-режим (LLM не подключена)";
      modeBadge.className = "badge";
    }
    const stats = health.sources || {};
    $("sourcesBadge").textContent = `📚 Источников: ${stats.total || 0} (проверено: ${stats.verified || 0})`;
  } catch (error) {
    $("modeBadge").textContent = "⚠️ Сервис недоступен";
    $("modeBadge").className = "badge badge-rejected";
  }
  refreshPendingCount();
}

async function refreshPendingCount() {
  try {
    const data = await api("/api/documents?status=pending_review");
    const count = (data.documents || []).length;
    const pill = $("pendingCount");
    pill.textContent = String(count);
    pill.classList.toggle("hidden", count === 0);
  } catch (error) {
    /* тихо: вкладка проверки обновится при открытии */
  }
}

/* ---------- чат ---------- */

$("chatForm").addEventListener("submit", async (event) => {
  event.preventDefault();
  const input = $("chatInput");
  const text = input.value.trim();
  if (text.length < 3) return;

  const button = $("sendButton");
  button.disabled = true;
  appendMessage("user", escapeHtml(text).replace(/\n/g, "<br>"));

  input.value = "";
  try {
    const payload = await api("/api/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        message: text,
        jurisdiction: $("jurisdiction").value,
        anonymize: $("anonymize").checked,
        session_id: "web",
        history: state.history.slice(-8),
      }),
    });

    state.history.push({ role: "user", content: text });
    state.history.push({ role: "assistant", content: payload.answer_md });
    state.lastQuestion = text;

    const chips = [];
    chips.push(
      payload.mode === "llm"
        ? "🤖 ответ LLM по правилам PLDA"
        : "⚙️ оффлайн-режим: план по правилам PLDA"
    );
    if (payload.anonymized) {
      chips.push(`🛡️ обезличено полей: ${payload.masked_count}`);
    }
    if (payload.llm_error) {
      chips.push(`⚠️ LLM недоступна: ${escapeHtml(payload.llm_error)}`);
    }

    const body = renderMarkdown(payload.answer_md)
      + renderSourcesBlock(payload.sources)
      + `<div class="meta-chips">${chips
          .map((chip) => `<span class="chip">${chip}</span>`)
          .join("")}</div>
         <div style="margin-top:10px">
           <button type="button" class="secondary" id="toMemo">📝 Создать записку по этому вопросу</button>
         </div>`;

    appendMessage("assistant", body);
    const toMemo = document.getElementById("toMemo");
    if (toMemo) {
      toMemo.addEventListener("click", () => {
        $("memoQuestion").value = state.lastQuestion;
        $("memoJurisdiction").value = $("jurisdiction").value;
        switchTab("memo");
      });
    }
  } catch (error) {
    appendMessage("assistant", `<div class="error">${escapeHtml(error.message)}</div>`);
  } finally {
    button.disabled = false;
    input.focus();
  }
});

function appendMessage(role, html) {
  const window_ = $("chatWindow");
  const wrapper = document.createElement("div");
  wrapper.className = `message ${role}`;
  wrapper.innerHTML = `<div class="bubble">${html}</div>`;
  window_.appendChild(wrapper);
  window_.scrollTop = window_.scrollHeight;
}

/* ---------- записка ---------- */

$("memoForm").addEventListener("submit", async (event) => {
  event.preventDefault();
  const question = $("memoQuestion").value.trim();
  if (question.length < 5) return;

  const button = $("memoButton");
  button.disabled = true;
  try {
    const payload = await api("/api/memo", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        question,
        jurisdiction: $("memoJurisdiction").value,
        anonymize: $("memoAnonymize").checked,
        facts: splitLines($("memoFacts").value),
        dates: splitLines($("memoDates").value),
        unknowns: splitLines($("memoUnknowns").value),
        next_steps: splitLines($("memoSteps").value),
      }),
    });

    state.lastMemoMarkdown = payload.markdown;
    state.lastMemoFilename = `plda-memo-${payload.case_id}.md`;

    $("memoPreview").textContent = payload.markdown;
    $("memoResult").classList.remove("hidden");
    $("memoStatus").textContent = `ожидает проверки юриста · документ #${payload.id}`;
    $("memoStatus").className = "badge badge-pending";
    refreshPendingCount();
    $("memoResult").scrollIntoView({ behavior: "smooth" });
  } catch (error) {
    alert("Ошибка: " + error.message);
  } finally {
    button.disabled = false;
  }
});

function splitLines(value) {
  return value
    .split("\n")
    .map((line) => line.trim())
    .filter(Boolean);
}

$("memoDownload").addEventListener("click", () => {
  if (!state.lastMemoMarkdown) return;
  const blob = new Blob([state.lastMemoMarkdown], {
    type: "text/markdown;charset=utf-8",
  });
  const link = document.createElement("a");
  link.href = URL.createObjectURL(blob);
  link.download = state.lastMemoFilename;
  link.click();
  URL.revokeObjectURL(link.href);
});

/* ---------- источники ---------- */

$("sourceSearch").addEventListener("click", () => searchSources());
$("sourceQuery").addEventListener("keydown", (event) => {
  if (event.key === "Enter") searchSources();
});

async function searchSources() {
  const query = $("sourceQuery").value.trim();
  const jurisdiction = $("sourceJurisdiction").value;
  const params = new URLSearchParams();
  if (query) params.set("q", query);
  if (jurisdiction) params.set("jurisdiction", jurisdiction);

  $("sourceResults").innerHTML = "<p class='hint'>Поиск…</p>";
  try {
    const data = await api("/api/sources?" + params.toString());
    const results = data.results || [];
    $("sourceMeta").textContent = query
      ? `По запросу «${query}» найдено: ${results.length}. Статус «требует проверки» — ссылка не проверялась в этой сессии.`
      : `Стартовый каталог: ${results.length} источников.`;
    $("sourceResults").innerHTML = results.length
      ? results.map(sourceCard).join("")
      : "<div class='empty'>Ничего не найдено. Уточните запрос или сформулируйте его иначе.</div>";
  } catch (error) {
    $("sourceResults").innerHTML = `<div class="error">${escapeHtml(error.message)}</div>`;
  }
}

/* ---------- проверка юриста ---------- */

async function loadDocuments() {
  $("docsList").innerHTML = "<p class='hint'>Загрузка…</p>";
  $("docDetail").classList.add("hidden");
  try {
    const data = await api("/api/documents");
    const documents = data.documents || [];
    if (!documents.length) {
      $("docsList").innerHTML =
        "<div class='empty'>Очередь пуста: сформируйте записку во вкладке «Записка».</div>";
      return;
    }
    $("docsList").innerHTML = documents
      .map((doc) => {
        const badge =
          doc.status === "approved"
            ? "badge badge-ok"
            : doc.status === "rejected"
              ? "badge badge-rejected"
              : "badge badge-pending";
        const label =
          doc.status === "approved"
            ? "проверено юристом"
            : doc.status === "rejected"
              ? "отклонено"
              : "ожидает проверки";
        return `<div class="doc-row" data-id="${doc.id}">
          <div>
            <div class="doc-title">#${doc.id} · ${escapeHtml(doc.title || "Без названия")}</div>
            <div class="doc-sub">${escapeHtml(doc.case_id)} · создано ${escapeHtml(doc.created_at)}${doc.anonymized ? " · обезличено" : ""}</div>
          </div>
          <span class="${badge}">${label}</span>
        </div>`;
      })
      .join("");

    document.querySelectorAll(".doc-row").forEach((row) => {
      row.addEventListener("click", () => openDocument(Number(row.dataset.id)));
    });
  } catch (error) {
    $("docsList").innerHTML = `<div class="error">${escapeHtml(error.message)}</div>`;
  }
}

async function openDocument(id) {
  try {
    const doc = await api(`/api/documents/${id}`);
    state.currentDocId = id;
    $("docTitle").textContent = `#${doc.id} · ${doc.title || "Без названия"}`;
    $("docMeta").textContent =
      `${doc.case_id} · создано ${doc.created_at}` +
      (doc.reviewed_at ? ` · проверено ${doc.reviewed_at}` : "");
    $("docContent").value = doc.content_md;
    $("reviewNote").value = doc.reviewer_note || "";

    const badge = $("docStatus");
    if (doc.status === "approved") {
      badge.textContent = "проверено юристом";
      badge.className = "badge badge-ok";
    } else if (doc.status === "rejected") {
      badge.textContent = "отклонено";
      badge.className = "badge badge-rejected";
    } else {
      badge.textContent = "ожидает проверки";
      badge.className = "badge badge-pending";
    }

    $("docsList").classList.add("hidden");
    $("docDetail").classList.remove("hidden");
  } catch (error) {
    alert("Ошибка: " + error.message);
  }
}

$("docBack").addEventListener("click", () => {
  $("docDetail").classList.add("hidden");
  $("docsList").classList.remove("hidden");
});

async function submitReview(action) {
  if (!state.currentDocId) return;
  try {
    await api(`/api/documents/${state.currentDocId}/review`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        action,
        content_md: $("docContent").value,
        reviewer_note: $("reviewNote").value.trim() || null,
      }),
    });
    await loadDocuments();
    refreshPendingCount();
  } catch (error) {
    alert("Ошибка: " + error.message);
  }
}

$("approveButton").addEventListener("click", () => submitReview("approve"));
$("rejectButton").addEventListener("click", () => submitReview("reject"));

/* ---------- старт ---------- */

loadHealth();
searchSources();
