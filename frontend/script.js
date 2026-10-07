// =========================================================
// FASTAPI CONFIGURATION
// =========================================================

const API_URL = "http://127.0.0.1:8000";


// =========================================================
// GLOBAL STATE
// =========================================================

let selectedTicketId = null;
let tickets = [];


// =========================================================
// HTML ELEMENTS
// =========================================================

const ticketTableBody =
    document.getElementById("ticketTableBody");

const ticketDetailsSection =
    document.getElementById("ticketDetailsSection");

const noSelectionSection =
    document.getElementById("noSelectionSection");

const refreshButton =
    document.getElementById("refreshButton");

const updateStatusButton =
    document.getElementById("updateStatusButton");

const statusSelect =
    document.getElementById("statusSelect");

const connectionMessage =
    document.getElementById("connectionMessage");

const reviewResponseText =
    document.getElementById("reviewResponseText");

const reviewStatusBadge =
    document.getElementById("reviewStatusBadge");

const reviewMessage =
    document.getElementById("reviewMessage");

const approveButton =
    document.getElementById("approveButton");

const saveEditButton =
    document.getElementById("saveEditButton");

const sendButton =
    document.getElementById("sendButton");


// =========================================================
// LOAD ALL TICKETS
// =========================================================

async function loadTickets() {

    showConnectionMessage("");

    try {

        const response = await fetch(
            `${API_URL}/tickets`
        );

        if (!response.ok) {
            throw new Error(
                `FastAPI returned ${response.status}`
            );
        }

        tickets = await response.json();

        displayTickets(tickets);

        updateStatistics(tickets);

    } catch (error) {

        console.error(
            "Error loading tickets:",
            error
        );

        ticketTableBody.innerHTML = `
            <tr>
                <td colspan="4" class="empty-row">
                    Unable to connect to FastAPI.
                </td>
            </tr>
        `;

        updateStatistics([]);

        showConnectionMessage(
            "Unable to connect to FastAPI. Make sure Uvicorn is running on http://127.0.0.1:8000."
        );
    }
}


// =========================================================
// DISPLAY ALL TICKETS
// =========================================================

function displayTickets(ticketList) {

    ticketTableBody.innerHTML = "";

    if (
        !ticketList ||
        ticketList.length === 0
    ) {

        ticketTableBody.innerHTML = `
            <tr>
                <td colspan="4" class="empty-row">
                    No tickets available.
                </td>
            </tr>
        `;

        return;
    }


    ticketList.forEach(ticket => {

        const row =
            document.createElement("tr");

        row.classList.add("ticket-row");


        if (
            ticket.ticket_id ===
            selectedTicketId
        ) {
            row.classList.add("selected");
        }


        row.innerHTML = `

            <td>
                <span class="ticket-id">
                    ${escapeHtml(
                        ticket.ticket_id || "-"
                    )}
                </span>
            </td>

            <td>
                ${escapeHtml(
                    ticket.subject || "No subject"
                )}
            </td>

            <td>
                ${escapeHtml(
                    extractEmail(ticket.sender) || "-"
                )}
            </td>

            <td>
                ${createStatusBadge(
                    ticket.status || "-"
                )}
            </td>
        `;


        row.addEventListener(
            "click",
            () => {

                loadTicketDetails(
                    ticket.ticket_id
                );

            }
        );


        ticketTableBody.appendChild(row);

    });
}


// =========================================================
// UPDATE DASHBOARD STATISTICS
// =========================================================

function updateStatistics(ticketList) {

    const total =
        ticketList.length;


    const received =
        ticketList.filter(
            ticket =>
                ticket.status === "RECEIVED"
        ).length;


    const triaged =
        ticketList.filter(
            ticket =>
                ticket.status === "TRIAGED"
        ).length;


    const inProgress =
        ticketList.filter(
            ticket =>
                ticket.status === "IN_PROGRESS"
        ).length;


    const resolved =
        ticketList.filter(
            ticket =>
                ticket.status === "RESOLVED"
        ).length;


    document.getElementById(
        "totalTickets"
    ).textContent = total;


    document.getElementById(
        "receivedTickets"
    ).textContent = received;


    document.getElementById(
        "triagedTickets"
    ).textContent = triaged;


    document.getElementById(
        "inProgressTickets"
    ).textContent = inProgress;


    document.getElementById(
        "resolvedTickets"
    ).textContent = resolved;
}


// =========================================================
// LOAD ONE TICKET
// =========================================================

async function loadTicketDetails(ticketId) {

    try {

        const response = await fetch(
            `${API_URL}/tickets/${encodeURIComponent(ticketId)}`
        );


        if (!response.ok) {

            throw new Error(
                `FastAPI returned ${response.status}`
            );
        }


        const data =
            await response.json();


        if (!data.ticket) {

            throw new Error(
                "Ticket information was not returned."
            );
        }


        selectedTicketId =
            data.ticket.ticket_id;


        displayTicketDetails(data);

        displayTickets(tickets);


    } catch (error) {

        console.error(
            "Error loading ticket details:",
            error
        );

        alert(
            "Unable to load the selected ticket."
        );
    }
}


// =========================================================
// DISPLAY TICKET DETAILS
// =========================================================

function displayTicketDetails(data) {

    const ticket =
        data.ticket;

    const ai =
        data.ai_analysis;


    // Show ticket details
    ticketDetailsSection.classList.remove(
        "hidden"
    );

    noSelectionSection.classList.add(
        "hidden"
    );


    // ------------------------------------------------------
    // BASIC TICKET INFORMATION
    // ------------------------------------------------------

    document.getElementById(
        "detailTicketId"
    ).textContent =
        ticket.ticket_id || "-";


    document.getElementById(
        "detailSender"
    ).textContent =
        ticket.sender || "-";


    document.getElementById(
        "detailSubject"
    ).textContent =
        ticket.subject || "No subject";


    document.getElementById(
        "detailReceivedAt"
    ).textContent =
        ticket.received_at || "-";


    document.getElementById(
        "detailGmailId"
    ).textContent =
        ticket.gmail_message_id || "-";


    document.getElementById(
        "detailMessage"
    ).textContent =
        ticket.message || "-";


    // ------------------------------------------------------
    // STATUS
    // ------------------------------------------------------

    document.getElementById(
        "detailStatusBadge"
    ).textContent =
        ticket.status || "-";


    setStatusBadgeClass(
        document.getElementById(
            "detailStatusBadge"
        ),
        ticket.status
    );


    statusSelect.value =
        ticket.status || "RECEIVED";


    // ------------------------------------------------------
    // AI TRIAGE
    // ------------------------------------------------------

    if (!ai) {

        document.getElementById(
            "aiSummary"
        ).textContent =
            "No AI analysis available.";

        document.getElementById(
            "aiCategory"
        ).textContent = "-";

        document.getElementById(
            "aiIntent"
        ).textContent = "-";

        document.getElementById(
            "aiUrgency"
        ).textContent = "-";

        document.getElementById(
            "aiSentiment"
        ).textContent = "-";

        document.getElementById(
            "aiKeyDetails"
        ).innerHTML =
            "<li>No AI analysis available.</li>";

        reviewResponseText.value = "";
        reviewStatusBadge.textContent = "-";
        reviewMessage.textContent = "";

        return;
    }


    document.getElementById(
        "aiSummary"
    ).textContent =
        ai.summary || "-";


    document.getElementById(
        "aiCategory"
    ).textContent =
        ai.category || "-";


    document.getElementById(
        "aiIntent"
    ).textContent =
        ai.intent || "-";


    document.getElementById(
        "aiUrgency"
    ).textContent =
        ai.urgency || "-";


    document.getElementById(
        "aiSentiment"
    ).textContent =
        ai.sentiment || "-";


    // ------------------------------------------------------
    // KEY DETAILS
    // ------------------------------------------------------

    const keyDetailsElement =
        document.getElementById(
            "aiKeyDetails"
        );


    keyDetailsElement.innerHTML = "";


    if (
        Array.isArray(ai.key_details) &&
        ai.key_details.length > 0
    ) {

        ai.key_details.forEach(
            detail => {

                const li =
                    document.createElement("li");

                li.textContent =
                    detail;

                keyDetailsElement.appendChild(
                    li
                );
            }
        );

    } else {

        keyDetailsElement.innerHTML =
            "<li>No key details available.</li>";
    }


    // ------------------------------------------------------
    // HUMAN REVIEW — CLIENT RESPONSE
    // ------------------------------------------------------

    reviewResponseText.value =
        ai.final_response || ai.ai_response || "";

    reviewStatusBadge.textContent =
        ai.review_status || "-";

    setReviewStatusBadgeClass(
        reviewStatusBadge,
        ai.review_status
    );

    reviewMessage.textContent = "";
}


// =========================================================
// UPDATE TICKET STATUS
// =========================================================

async function updateTicketStatus() {

    if (!selectedTicketId) {

        alert(
            "Please select a ticket first."
        );

        return;
    }


    const newStatus =
        statusSelect.value;


    try {

        const response = await fetch(

            `${API_URL}/tickets/${encodeURIComponent(selectedTicketId)}`,

            {
                method: "PUT",

                headers: {
                    "Content-Type":
                        "application/json"
                },

                body: JSON.stringify({
                    status: newStatus
                })
            }
        );


        const result =
            await response.json();


        if (!response.ok) {

            throw new Error(
                result.message ||
                "Status update failed."
            );
        }


        document.getElementById(
            "statusMessage"
        ).textContent =
            "Ticket status updated successfully.";


        // Reload tickets
        await loadTickets();


        // Reload selected ticket
        await loadTicketDetails(
            selectedTicketId
        );


    } catch (error) {

        console.error(
            "Status update error:",
            error
        );

        document.getElementById(
            "statusMessage"
        ).textContent =
            "Unable to update ticket status.";
    }
}


// =========================================================
// APPROVE AI RESPONSE
// =========================================================

async function approveResponse() {

    if (!selectedTicketId) {

        alert(
            "Please select a ticket first."
        );

        return;
    }


    try {

        const response = await fetch(

            `${API_URL}/tickets/${encodeURIComponent(selectedTicketId)}/approve`,

            { method: "POST" }
        );


        const result =
            await response.json();


        if (!response.ok || result.status === "error") {

            throw new Error(
                result.message ||
                "Approve failed."
            );
        }


        reviewMessage.textContent =
            result.message;


        await loadTicketDetails(
            selectedTicketId
        );


    } catch (error) {

        console.error(
            "Approve error:",
            error
        );

        reviewMessage.textContent =
            "Unable to approve response.";
    }
}


// =========================================================
// SAVE EDITED RESPONSE
// =========================================================

async function saveEditedResponse() {

    if (!selectedTicketId) {

        alert(
            "Please select a ticket first."
        );

        return;
    }


    const editedText =
        reviewResponseText.value.trim();


    if (!editedText) {

        alert(
            "Response text cannot be empty."
        );

        return;
    }


    try {

        const response = await fetch(

            `${API_URL}/tickets/${encodeURIComponent(selectedTicketId)}/edit`,

            {
                method: "PUT",

                headers: {
                    "Content-Type":
                        "application/json"
                },

                body: JSON.stringify({
                    final_response: editedText
                })
            }
        );


        const result =
            await response.json();


        if (!response.ok || result.status === "error") {

            throw new Error(
                result.message ||
                "Save edit failed."
            );
        }


        reviewMessage.textContent =
            result.message;


        await loadTicketDetails(
            selectedTicketId
        );


    } catch (error) {

        console.error(
            "Save edit error:",
            error
        );

        reviewMessage.textContent =
            "Unable to save edited response.";
    }
}


// =========================================================
// SEND TO CUSTOMER
// =========================================================

async function sendToCustomer() {

    if (!selectedTicketId) {

        alert(
            "Please select a ticket first."
        );

        return;
    }


    if (!confirm(
        "Send this response to the customer now?"
    )) {

        return;
    }


    try {

        const response = await fetch(

            `${API_URL}/tickets/${encodeURIComponent(selectedTicketId)}/send`,

            { method: "POST" }
        );


        const result =
            await response.json();


        if (!response.ok || result.status === "error") {

            throw new Error(
                result.message ||
                "Send failed."
            );
        }


        reviewMessage.textContent =
            result.message;


        await loadTickets();

        await loadTicketDetails(
            selectedTicketId
        );


    } catch (error) {

        console.error(
            "Send error:",
            error
        );

        reviewMessage.textContent =
            error.message ||
            "Unable to send response.";
    }
}


// =========================================================
// STATUS BADGE
// =========================================================

function createStatusBadge(status) {

    const safeStatus =
        status || "-";

    const statusClass =
        getStatusClass(safeStatus);

    return `
        <span class="status-badge ${statusClass}">
            ${escapeHtml(safeStatus)}
        </span>
    `;
}


function setStatusBadgeClass(
    element,
    status
) {

    element.className =
        "status-badge";

    const statusClass =
        getStatusClass(status);

    if (statusClass) {

        element.classList.add(
            statusClass
        );
    }
}


function getStatusClass(status) {

    switch (status) {

        case "RECEIVED":
            return "status-received";

        case "TRIAGED":
            return "status-triaged";

        case "IN_PROGRESS":
            return "status-in-progress";

        case "RESOLVED":
            return "status-resolved";

        default:
            return "";
    }
}


// =========================================================
// REVIEW STATUS BADGE
// =========================================================

function getReviewStatusClass(status) {

    switch (status) {

        case "PENDING_REVIEW":
            return "status-pending-review";

        case "APPROVED":
            return "status-approved";

        case "EDITED":
            return "status-edited";

        case "SENT":
            return "status-sent";

        default:
            return "";
    }
}


function setReviewStatusBadgeClass(
    element,
    status
) {

    element.className =
        "status-badge";

    const statusClass =
        getReviewStatusClass(status);

    if (statusClass) {

        element.classList.add(
            statusClass
        );
    }
}


// =========================================================
// EXTRACT EMAIL ADDRESS
// =========================================================

function extractEmail(sender) {

    if (!sender) {
        return "";
    }


    const match =
        sender.match(
            /<([^>]+)>/
        );


    if (match) {
        return match[1];
    }


    return sender;
}


// =========================================================
// HTML ESCAPING
// =========================================================

function escapeHtml(value) {

    return String(value)
        .replaceAll("&", "&amp;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;")
        .replaceAll('"', "&quot;")
        .replaceAll("'", "&#039;");
}


// =========================================================
// CONNECTION MESSAGE
// =========================================================

function showConnectionMessage(
    message
) {

    if (!message) {

        connectionMessage.textContent = "";

        connectionMessage.classList.add(
            "hidden"
        );

        return;
    }


    connectionMessage.textContent =
        message;

    connectionMessage.classList.remove(
        "hidden"
    );
}


// =========================================================
// EVENT LISTENERS
// =========================================================

refreshButton.addEventListener(
    "click",
    async () => {

        await loadTickets();

    }
);


updateStatusButton.addEventListener(
    "click",
    updateTicketStatus
);


approveButton.addEventListener(
    "click",
    approveResponse
);


saveEditButton.addEventListener(
    "click",
    saveEditedResponse
);


sendButton.addEventListener(
    "click",
    sendToCustomer
);


// =========================================================
// INITIAL DASHBOARD LOAD
// =========================================================

loadTickets();