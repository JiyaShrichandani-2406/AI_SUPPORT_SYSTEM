
"use strict";

/* =========================================================
   AI TECHNICAL SUPPORT SYSTEM
   Frontend <-> FastAPI <-> SQLite / AI / RAG / Gmail
========================================================= */


/* =========================================================
   1. API CONFIGURATION
========================================================= */

// When served by FastAPI at /app/, use the same origin.
// When served through VS Code Live Server, connect to port 8000.

const API_URL =
    window.location.port === "8000"
        ? window.location.origin
        : "http://127.0.0.1:8000";

const DESKTOP_QUERY = window.matchMedia("(min-width: 960px)");

const REQUEST_TIMEOUT = 240000;


/* =========================================================
   2. APPLICATION STATE
========================================================= */

let tickets = [];
let selectedTicketId = null;
let currentFilter = "ALL";
let currentReviewStatus = null;
let loadedResponseText = "";
let isLoadingTickets = false;
let toastTimer = null;


/* =========================================================
   3. HTML ELEMENT REFERENCES
========================================================= */

const $ = (id) => document.getElementById(id);

const el = {
    ticketList: $("ticketList"),
    listCount: $("listCount"),
    searchInput: $("searchInput"),
    connectionMessage: $("connectionMessage"),

    refreshButton: $("refreshButton"),
    refreshIcon: document.querySelector(".refresh-icon"),

    backButton: $("backButton"),

    noSelection: $("noSelection"),
    ticketDetails: $("ticketDetails"),

    detailStatusBadge: $("detailStatusBadge"),
    detailSubject: $("detailSubject"),

    reviewText: $("reviewResponseText"),
    reviewBadge: $("reviewStatusBadge"),
    reviewMessage: $("reviewMessage"),

    approveButton: $("approveButton"),
    saveEditButton: $("saveEditButton"),
    sendButton: $("sendButton"),

    statusSelect: $("statusSelect"),
    updateStatusButton: $("updateStatusButton"),
    statusMessage: $("statusMessage"),

    aiTriageId: $("aiTriageId"),
    sentInformation: $("sentInformation"),
    sentAt: $("sentAt"),

    toast: $("toast")
};


/* =========================================================
   4. GENERAL HELPERS
========================================================= */

function escapeHtml(value) {
    return String(value ?? "")
        .replaceAll("&", "&amp;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;")
        .replaceAll('"', "&quot;")
        .replaceAll("'", "&#039;");
}


function extractEmail(sender) {
    if (!sender) return "";

    const match = String(sender).match(/<([^>]+)>/);

    return match ? match[1] : String(sender);
}


function prettyLabel(value) {
    return String(value || "-").replaceAll("_", " ");
}


function statusClass(status) {
    return {
        RECEIVED: "status-received",
        TRIAGED: "status-triaged",
        IN_PROGRESS: "status-in-progress",
        RESOLVED: "status-resolved"
    }[status] || "";
}


function reviewClass(status) {
    return {
        PENDING_REVIEW: "status-pending-review",
        APPROVED: "status-approved",
        EDITED: "status-edited",
        SENT: "status-sent"
    }[status] || "";
}


function urgencyClass(urgency) {
    const value = String(urgency || "").toLowerCase();

    if (value === "high") return "urgency-high";
    if (value === "medium") return "urgency-medium";
    if (value === "low") return "urgency-low";

    return "";
}


function setBadge(element, text, className = "") {
    if (!element) return;

    element.className = "badge" + (className ? ` ${className}` : "");
    element.textContent = text || "-";
}


function setInlineMessage(element, message, isError = false) {
    if (!element) return;

    element.textContent = message || "";
    element.classList.toggle("error", isError);
}


function showToast(message, isError = false) {
    if (!el.toast) return;

    el.toast.textContent = message;

    el.toast.className = "toast";

    if (isError) {
        el.toast.classList.add("error");
    }

    clearTimeout(toastTimer);

    toastTimer = setTimeout(() => {
        el.toast.classList.add("hidden");
    }, 3500);
}


function showConnectionMessage(message) {
    if (!el.connectionMessage) return;

    el.connectionMessage.textContent = message || "";

    el.connectionMessage.classList.toggle(
        "hidden",
        !message
    );
}


function formatDate(value) {
    if (!value) return "-";

    const date = new Date(value);

    if (Number.isNaN(date.getTime())) {
        return String(value);
    }

    return date.toLocaleString();
}


/* =========================================================
   5. FASTAPI REQUEST HELPER
========================================================= */

async function api(path, options = {}) {
    const controller = new AbortController();

    const timeout = setTimeout(() => {
        controller.abort();
    }, REQUEST_TIMEOUT);

    try {
        const response = await fetch(`${API_URL}${path}`, {
            ...options,
            signal: controller.signal,
            headers: {
                ...(options.body
                    ? { "Content-Type": "application/json" }
                    : {}),
                ...(options.headers || {})
            }
        });

        let data = null;

        try {
            data = await response.json();
        } catch (_) {
            // Some responses may not contain JSON.
        }

        if (!response.ok) {
            let message =
                data?.message ||
                data?.detail ||
                `Request failed with HTTP ${response.status}.`;

            if (Array.isArray(message)) {
                message = message
                    .map(item => item.msg || JSON.stringify(item))
                    .join("; ");
            } else if (typeof message !== "string") {
                message = JSON.stringify(message);
            }

            throw new Error(message);
        }

        if (data && data.status === "error") {
            throw new Error(
                data.message || "The backend reported an error."
            );
        }

        return data;

    } catch (error) {
        if (error.name === "AbortError") {
            throw new Error(
                "The request timed out. Check FastAPI, Ollama and the RAG service."
            );
        }

        if (error instanceof TypeError) {
            throw new Error(
                `Cannot connect to FastAPI at ${API_URL}. ` +
                "Start the backend and check the API address."
            );
        }

        throw error;

    } finally {
        clearTimeout(timeout);
    }
}


/* =========================================================
   6. MOBILE NAVIGATION
========================================================= */

function showDetailView() {
    if (!DESKTOP_QUERY.matches) {
        if (!document.body.classList.contains("show-detail")) {
            history.pushState(
                { view: "detail" },
                "",
                window.location.href
            );
        }

        window.scrollTo({ top: 0, behavior: "smooth" });
    }

    document.body.classList.add("show-detail");
}


function showListView() {
    document.body.classList.remove("show-detail");
}


/* =========================================================
   7. LOAD ALL TICKETS
========================================================= */

async function loadTickets() {
    if (isLoadingTickets) return;

    isLoadingTickets = true;

    showConnectionMessage("");

    if (el.refreshIcon) {
        el.refreshIcon.classList.add("spin");
    }

    el.refreshButton.disabled = true;

    try {
        // Backend: GET /tickets
        const data = await api("/tickets");

        if (!Array.isArray(data)) {
            throw new Error(
                "The backend returned an unexpected ticket-list format."
            );
        }

        // The backend list is displayed newest first.
        tickets = [...data].reverse();

        updateStatistics();
        renderTickets();

    } catch (error) {
        console.error("Unable to load tickets:", error);

        showConnectionMessage(
            `${error.message} ` +
            "Check that FastAPI is running at http://127.0.0.1:8000."
        );

        el.ticketList.innerHTML = `
            <li class="empty">
                Unable to load tickets from the backend.
                Use Refresh to try again.
            </li>
        `;

        el.listCount.textContent = "";

        tickets = [];
        updateStatistics();

    } finally {
        isLoadingTickets = false;

        el.refreshButton.disabled = false;

        if (el.refreshIcon) {
            el.refreshIcon.classList.remove("spin");
        }
    }
}


/* =========================================================
   8. FILTER AND SEARCH
========================================================= */

function filteredTickets() {
    const query = el.searchInput.value.trim().toLowerCase();

    return tickets.filter(ticket => {
        if (
            currentFilter !== "ALL" &&
            ticket.status !== currentFilter
        ) {
            return false;
        }

        if (!query) return true;

        const searchableText = [
            ticket.ticket_id,
            ticket.subject,
            ticket.sender,
            ticket.category,
            ticket.status,
            ticket.urgency,
            ticket.review_status
        ]
            .filter(Boolean)
            .join(" ")
            .toLowerCase();

        return searchableText.includes(query);
    });
}


/* =========================================================
   9. RENDER TICKET LIST
========================================================= */

function renderTickets() {
    const list = filteredTickets();

    el.listCount.textContent = tickets.length
        ? `${list.length} of ${tickets.length}`
        : "";

    if (list.length === 0) {
        el.ticketList.innerHTML = `
            <li class="empty">
                ${
                    tickets.length
                        ? "No tickets match your search or filter."
                        : "No tickets available."
                }
            </li>
        `;

        return;
    }

    el.ticketList.innerHTML = list.map(ticket => {
        const tags = [];

        if (ticket.category) {
            tags.push(`
                <span class="badge">
                    ${escapeHtml(ticket.category)}
                </span>
            `);
        }

        if (ticket.urgency) {
            tags.push(`
                <span class="badge ${urgencyClass(ticket.urgency)}">
                    ${escapeHtml(ticket.urgency)}
                </span>
            `);
        }

        if (ticket.review_status) {
            tags.push(`
                <span class="badge ${reviewClass(ticket.review_status)}">
                    ${escapeHtml(prettyLabel(ticket.review_status))}
                </span>
            `);
        }

        return `
            <li
                class="ticket-item ${
                    ticket.ticket_id === selectedTicketId ? "selected" : ""
                }"
                data-id="${escapeHtml(ticket.ticket_id)}"
                tabindex="0"
                role="button"
                aria-label="Open ticket ${escapeHtml(ticket.ticket_id)}"
                aria-pressed="${
                    ticket.ticket_id === selectedTicketId
                }"
            >
                <div class="row">
                    <span class="tid">
                        ${escapeHtml(ticket.ticket_id)}
                    </span>

                    <span class="badge ${statusClass(ticket.status)}">
                        ${escapeHtml(prettyLabel(ticket.status))}
                    </span>
                </div>

                <div class="subject">
                    ${escapeHtml(ticket.subject || "No subject")}
                </div>

                <div class="customer">
                    ${escapeHtml(extractEmail(ticket.sender) || "-")}
                </div>

                ${
                    tags.length
                        ? `<div class="tags">${tags.join("")}</div>`
                        : ""
                }
            </li>
        `;
    }).join("");
}


/* =========================================================
   10. UPDATE STATISTICS
========================================================= */

function updateStatistics() {
    const count = status =>
        tickets.filter(ticket => ticket.status === status).length;

    $("totalTickets").textContent = tickets.length;
    $("receivedTickets").textContent = count("RECEIVED");
    $("triagedTickets").textContent = count("TRIAGED");
    $("inProgressTickets").textContent = count("IN_PROGRESS");
    $("resolvedTickets").textContent = count("RESOLVED");
}


/* =========================================================
   11. LOAD ONE TICKET
========================================================= */

async function loadTicketDetails(ticketId) {
    if (!ticketId) return;

    try {
        // Backend: GET /tickets/{ticket_id}
        const data = await api(
            `/tickets/${encodeURIComponent(ticketId)}`
        );

        if (!data || !data.ticket) {
            throw new Error(
                "The backend did not return ticket information."
            );
        }

        selectedTicketId = data.ticket.ticket_id;

        renderTicketDetails(data);
        renderTickets();

        showDetailView();

    } catch (error) {
        console.error("Unable to load ticket details:", error);

        showToast(error.message || "Unable to load ticket details.", true);
    }
}


/* =========================================================
   12. RENDER TICKET DETAILS
========================================================= */

function renderTicketDetails(data) {
    const ticket = data.ticket;
    const ai = data.ai_analysis;

    el.noSelection.classList.add("hidden");
    el.ticketDetails.classList.remove("hidden");

    $("detailSubject").textContent =
        ticket.subject || "No subject";

    $("detailTicketId").textContent =
        ticket.ticket_id || "-";

    $("detailSender").textContent =
        ticket.sender || "-";

    $("detailReceivedAt").textContent =
        formatDate(ticket.received_at);

    $("detailGmailId").textContent =
        ticket.gmail_message_id || "-";

    $("detailMessage").textContent =
        ticket.message || "-";

    setBadge(
        el.detailStatusBadge,
        prettyLabel(ticket.status),
        statusClass(ticket.status)
    );

    el.statusSelect.value = ticket.status || "RECEIVED";

    setInlineMessage(el.statusMessage, "");
    setInlineMessage(el.reviewMessage, "");

    // Reset sent metadata before rendering this ticket.
    el.sentInformation.classList.add("hidden");
    el.sentAt.textContent = "-";

    /* -----------------------------------------
       AI ANALYSIS
    ------------------------------------------ */

    if (!ai) {
        $("aiSummary").textContent =
            "No AI analysis is available for this ticket.";

        ["aiCategory", "aiIntent", "aiUrgency", "aiSentiment"]
            .forEach(id => {
                $(id).textContent = "-";
            });

        el.aiTriageId.textContent = "-";

        $("aiKeyDetails").innerHTML = `
            <li>No AI analysis available.</li>
        `;

        el.reviewText.value = "";
        loadedResponseText = "";
        currentReviewStatus = null;

        setBadge(el.reviewBadge, "Unavailable");
        setReviewControls(null);

        return;
    }

    $("aiSummary").textContent = ai.summary || "-";
    $("aiCategory").textContent = ai.category || "-";
    $("aiIntent").textContent = ai.intent || "-";
    $("aiUrgency").textContent = ai.urgency || "-";
    $("aiSentiment").textContent = ai.sentiment || "-";

    el.aiTriageId.textContent = ai.triage_id || "-";

    // Render key details safely without inserting server text as HTML.
    const keyList = $("aiKeyDetails");

    keyList.replaceChildren();

    if (Array.isArray(ai.key_details) && ai.key_details.length > 0) {
        ai.key_details.forEach(detail => {
            const item = document.createElement("li");

            item.textContent =
                typeof detail === "string"
                    ? detail
                    : JSON.stringify(detail);

            keyList.appendChild(item);
        });
    } else {
        const item = document.createElement("li");

        item.textContent = "No key details available.";

        keyList.appendChild(item);
    }

    /* -----------------------------------------
       HUMAN REVIEW
    ------------------------------------------ */

    loadedResponseText =
        ai.final_response || ai.ai_response || "";

    el.reviewText.value = loadedResponseText;

    currentReviewStatus = ai.review_status || "PENDING_REVIEW";

    setBadge(
        el.reviewBadge,
        prettyLabel(currentReviewStatus),
        reviewClass(currentReviewStatus)
    );

    setReviewControls(currentReviewStatus);

    if (currentReviewStatus === "SENT") {
        if (ai.sent_at) {
            el.sentInformation.classList.remove("hidden");

            el.sentAt.textContent = formatDate(ai.sent_at);
        }

        setInlineMessage(
            el.reviewMessage,
            "This response has already been sent to the customer."
        );
    }
}


/* =========================================================
   13. REVIEW BUTTON STATES
========================================================= */

function setReviewControls(reviewStatus) {
    const sent = reviewStatus === "SENT";
    const noDraft = reviewStatus === null;

    el.reviewText.disabled = sent || noDraft;
    el.approveButton.disabled = sent || noDraft;
    el.saveEditButton.disabled = sent || noDraft;
    el.sendButton.disabled = sent || noDraft;

    el.sendButton.textContent = sent
        ? "Already Sent"
        : "Send to Customer";

    el.approveButton.textContent =
        reviewStatus === "APPROVED"
            ? "Approved"
            : "Approve As-Is";

    el.approveButton.disabled =
        sent || noDraft || reviewStatus === "APPROVED";
}


/* =========================================================
   14. BUTTON BUSY STATE
========================================================= */

async function withBusy(button, task) {
    const originalText = button.textContent;

    button.disabled = true;

    try {
        await task();
    } finally {
        button.textContent = originalText;

        if (button === el.updateStatusButton) {
            button.disabled = false;
        }

        setReviewControls(currentReviewStatus);
    }
}


/* =========================================================
   15. UPDATE TICKET STATUS
========================================================= */

async function updateTicketStatus() {
    if (!selectedTicketId) {
        showToast("Select a ticket first.", true);
        return;
    }

    await withBusy(el.updateStatusButton, async () => {
        try {
            const ticketId = selectedTicketId;
            const newStatus = el.statusSelect.value;

            // Backend: PUT /tickets/{ticket_id}
            await api(
                `/tickets/${encodeURIComponent(ticketId)}`,
                {
                    method: "PUT",
                    body: JSON.stringify({
                        status: newStatus
                    })
                }
            );

            showToast("Ticket status updated successfully.");

            await loadTickets();
            await loadTicketDetails(ticketId);

        } catch (error) {
            setInlineMessage(
                el.statusMessage,
                error.message || "Unable to update ticket status.",
                true
            );
        }
    });
}


/* =========================================================
   16. SAVE EDITED RESPONSE
========================================================= */

async function saveEdit(silent = false) {
    if (!selectedTicketId) {
        throw new Error("Select a ticket first.");
    }

    const text = el.reviewText.value.trim();

    if (!text) {
        throw new Error("Response text cannot be empty.");
    }

    const ticketId = selectedTicketId;

    // Backend: PUT /tickets/{ticket_id}/edit
    const result = await api(
        `/tickets/${encodeURIComponent(ticketId)}/edit`,
        {
            method: "PUT",
            body: JSON.stringify({
                final_response: text
            })
        }
    );

    loadedResponseText = text;
    currentReviewStatus = "EDITED";

    setBadge(
        el.reviewBadge,
        "EDITED",
        reviewClass("EDITED")
    );

    setReviewControls(currentReviewStatus);

    if (!silent) {
        showToast(result.message || "Response edit saved.");
    }

    return result;
}


/* =========================================================
   17. SAVE EDIT BUTTON
========================================================= */

async function saveEditedResponse() {
    if (!selectedTicketId) {
        showToast("Select a ticket first.", true);
        return;
    }

    await withBusy(el.saveEditButton, async () => {
        try {
            const ticketId = selectedTicketId;

            await saveEdit(false);

            await loadTickets();
            await loadTicketDetails(ticketId);

        } catch (error) {
            setInlineMessage(
                el.reviewMessage,
                error.message || "Unable to save the response.",
                true
            );
        }
    });
}


/* =========================================================
   18. APPROVE RESPONSE
========================================================= */

async function approveResponse() {
    if (!selectedTicketId) {
        showToast("Select a ticket first.", true);
        return;
    }

    await withBusy(el.approveButton, async () => {
        try {
            const ticketId = selectedTicketId;

            const currentText = el.reviewText.value.trim();

            if (!currentText) {
                throw new Error("Response text cannot be empty.");
            }

            // Save the latest text first if the user changed it.
            if (currentText !== loadedResponseText.trim()) {
                await saveEdit(true);
            }

            // Backend: POST /tickets/{ticket_id}/approve
            const result = await api(
                `/tickets/${encodeURIComponent(ticketId)}/approve`,
                {
                    method: "POST"
                }
            );

            showToast(result.message || "Response approved.");

            await loadTickets();
            await loadTicketDetails(ticketId);

        } catch (error) {
            setInlineMessage(
                el.reviewMessage,
                error.message || "Unable to approve the response.",
                true
            );
        }
    });
}


/* =========================================================
   19. SEND RESPONSE TO CUSTOMER
========================================================= */

async function sendToCustomer() {
    if (!selectedTicketId) {
        showToast("Select a ticket first.", true);
        return;
    }

    if (currentReviewStatus === "SENT") {
        showToast("This response has already been sent.", true);
        return;
    }

    const responseText = el.reviewText.value.trim();

    if (!responseText) {
        showToast("The response cannot be empty.", true);
        return;
    }

    const confirmed = window.confirm(
        "Send this response to the customer using Gmail?"
    );

    if (!confirmed) return;

    await withBusy(el.sendButton, async () => {
        const ticketId = selectedTicketId;

        el.sendButton.textContent = "Sending...";

        try {
            const id = encodeURIComponent(ticketId);

            // Ensure the text shown in the editor is saved.
            const edited =
                el.reviewText.value.trim() !==
                loadedResponseText.trim();

            if (edited) {
                await saveEdit(true);
            }

            // The backend requires APPROVED or EDITED before sending.
            if (
                currentReviewStatus !== "APPROVED" &&
                currentReviewStatus !== "EDITED"
            ) {
                await api(`/tickets/${id}/approve`, {
                    method: "POST"
                });

                currentReviewStatus = "APPROVED";
            }

            // Backend: POST /tickets/{ticket_id}/send
            const result = await api(
                `/tickets/${id}/send`,
                {
                    method: "POST"
                }
            );

            // Success is shown only after FastAPI confirms the request.
            showToast(
                result.message || "Response sent successfully."
            );

            await loadTickets();
            await loadTicketDetails(ticketId);

        } catch (error) {
            console.error("Unable to send response:", error);

            setInlineMessage(
                el.reviewMessage,
                error.message || "Unable to send the response.",
                true
            );

            showToast("Sending failed. Check the error message.", true);

            // Reload server state because the result of a failed
            // network request may be uncertain.
            await loadTickets();
            await loadTicketDetails(ticketId);
        }
    });
}


/* =========================================================
   20. REFRESH BUTTON
========================================================= */

async function refreshDashboard() {
    await loadTickets();

    // Keep the currently selected ticket open and refresh its data.
    if (selectedTicketId) {
        await loadTicketDetails(selectedTicketId);
    }
}


/* =========================================================
   21. EVENT LISTENERS
========================================================= */

// Refresh dashboard.
el.refreshButton.addEventListener(
    "click",
    refreshDashboard
);


// Back button for mobile ticket details.
el.backButton.addEventListener("click", () => {
    if (
        !DESKTOP_QUERY.matches &&
        history.state &&
        history.state.view === "detail"
    ) {
        history.back();
    } else {
        showListView();
    }
});


// Update ticket status.
el.updateStatusButton.addEventListener(
    "click",
    updateTicketStatus
);


// Human review actions.
el.approveButton.addEventListener(
    "click",
    approveResponse
);

el.saveEditButton.addEventListener(
    "click",
    saveEditedResponse
);

el.sendButton.addEventListener(
    "click",
    sendToCustomer
);


// Search.
el.searchInput.addEventListener("input", renderTickets);


// Open a ticket using mouse/touch.
el.ticketList.addEventListener("click", event => {
    const item = event.target.closest(".ticket-item");

    if (item) {
        loadTicketDetails(item.dataset.id);
    }
});


// Open a ticket using keyboard.
el.ticketList.addEventListener("keydown", event => {
    if (event.key !== "Enter" && event.key !== " ") {
        return;
    }

    const item = event.target.closest(".ticket-item");

    if (item) {
        event.preventDefault();

        loadTicketDetails(item.dataset.id);
    }
});


// Statistics act as status filters.
document.querySelectorAll(".stat-card").forEach(card => {
    card.addEventListener("click", () => {
        currentFilter = card.dataset.filter;

        document.querySelectorAll(".stat-card").forEach(item => {
            item.classList.toggle("active", item === card);
        });

        showListView();
        renderTickets();
    });
});


// Mobile browser Back button.
window.addEventListener("popstate", () => {
    showListView();
});


// Adjust navigation when the browser changes size.
DESKTOP_QUERY.addEventListener("change", () => {
    if (DESKTOP_QUERY.matches) {
        document.body.classList.remove("show-detail");
    }
});


/* =========================================================
   22. START APPLICATION
========================================================= */

async function initializeDashboard() {
    try {
        // Confirm that FastAPI is reachable before loading tickets.
        // Backend: GET /
        await api("/");

        await loadTickets();

    } catch (error) {
        console.error("Backend initialization failed:", error);

        showConnectionMessage(
            `${error.message} Start FastAPI and refresh this page.`
        );

        el.ticketList.innerHTML = `
            <li class="empty">
                Backend connection unavailable.
            </li>
        `;
    }
}

initializeDashboard();
