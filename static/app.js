const SKY_RECENT_KEY = "bot_o_brain_sky_recent_searches";
const SKY_PINNED_KEY = "bot_o_brain_sky_pinned_flights";

// Global Navigation Actions
window.openServicesModal = function() {
    const modal = document.getElementById("servicesModal");
    if (modal) modal.classList.remove("hidden");
};

window.closeServicesModal = function() {
    const modal = document.getElementById("servicesModal");
    if (modal) modal.classList.add("hidden");
    if (window.backToCategories) window.backToCategories();
};

// =========================================================================
// AI SERVICES HUB CATEGORIZED ACTIONS (GLOBAL MODULE SCOPE)
// =========================================================================
window.openServiceCategory = function(category) {
    const catGrid = document.getElementById("serviceCategoriesGrid");
    const subMenuBox = document.getElementById("serviceSubMenuBox");
    const subMenuTitle = document.getElementById("subMenuTitle");
    const subMenuGrid = document.getElementById("subMenuGrid");
    const actionBox = document.getElementById("serviceActionBox");

    if (!catGrid || !subMenuBox || !subMenuTitle || !subMenuGrid) return;

    catGrid.classList.add("hidden");
    if (actionBox) actionBox.classList.add("hidden");
    subMenuBox.classList.remove("hidden");

    if (category === "bookings") {
        subMenuTitle.innerHTML = "🎫 Bookings &amp; Reservations";
        subMenuGrid.innerHTML = `
            <div class="service-card" onclick="selectService('flight')">
                <div class="service-card-icon" style="background: rgba(56, 189, 248, 0.15); color: #38bdf8;">
                    <i class="fa-solid fa-plane-departure"></i>
                </div>
                <div class="service-card-info">
                    <h3>Flight Ticket Booking</h3>
                    <p>Search live Google Flights, reserve PNR seats, &amp; pay</p>
                </div>
                <i class="fa-solid fa-chevron-right service-arrow"></i>
            </div>
            <div class="service-card" onclick="selectService('movie')">
                <div class="service-card-icon" style="background: rgba(168, 85, 247, 0.15); color: #a855f7;">
                    <i class="fa-solid fa-film"></i>
                </div>
                <div class="service-card-info">
                    <h3>Movie Ticket Booking</h3>
                    <p>Search showtimes &amp; reserve cinema tickets</p>
                </div>
                <i class="fa-solid fa-chevron-right service-arrow"></i>
            </div>
            <div class="service-card" onclick="selectService('hotel')">
                <div class="service-card-icon" style="background: rgba(56, 189, 248, 0.15); color: #38bdf8;">
                    <i class="fa-solid fa-hotel"></i>
                </div>
                <div class="service-card-info">
                    <h3>Hotel Room Booking</h3>
                    <p>Find &amp; reserve deluxe rooms and luxury suites</p>
                </div>
                <i class="fa-solid fa-chevron-right service-arrow"></i>
            </div>
        `;
    } else if (category === "messaging") {
        subMenuTitle.innerHTML = "💬 Messaging &amp; Communications";
        subMenuGrid.innerHTML = `
            <div class="service-card" onclick="selectService('email')">
                <div class="service-card-icon" style="background: rgba(239, 68, 68, 0.15); color: #ef4444;">
                    <i class="fa-solid fa-envelope"></i>
                </div>
                <div class="service-card-info">
                    <h3>Send Email / Gmail</h3>
                    <p>Send emails via SMTP directly from chat</p>
                </div>
                <i class="fa-solid fa-chevron-right service-arrow"></i>
            </div>
            <div class="service-card" onclick="selectService('whatsapp')">
                <div class="service-card-icon" style="background: rgba(34, 197, 94, 0.15); color: #22c55e;">
                    <i class="fa-brands fa-whatsapp"></i>
                </div>
                <div class="service-card-info">
                    <h3>WhatsApp Message</h3>
                    <p>Send WhatsApp text messages to any number</p>
                </div>
                <i class="fa-solid fa-chevron-right service-arrow"></i>
            </div>
            <div class="service-card" onclick="selectService('telegram')">
                <div class="service-card-icon" style="background: rgba(59, 130, 246, 0.15); color: #3b82f6;">
                    <i class="fa-brands fa-telegram"></i>
                </div>
                <div class="service-card-info">
                    <h3>Telegram Message</h3>
                    <p>Send updates to Telegram chats or channels</p>
                </div>
                <i class="fa-solid fa-chevron-right service-arrow"></i>
            </div>
        `;
    } else if (category === "utilities") {
        subMenuTitle.innerHTML = "🛠️ Other AI Services &amp; Vault";
        subMenuGrid.innerHTML = `
            <div class="service-card" onclick="selectService('vault')">
                <div class="service-card-icon" style="background: rgba(16, 185, 129, 0.15); color: #10b981;">
                    <i class="fa-solid fa-database"></i>
                </div>
                <div class="service-card-info">
                    <h3>Memory Vault Manager</h3>
                    <p>Inspect, add, and manage vector stored facts</p>
                </div>
                <i class="fa-solid fa-chevron-right service-arrow"></i>
            </div>
            <div class="service-card" onclick="selectService('rag')">
                <div class="service-card-icon" style="background: rgba(245, 158, 11, 0.15); color: #f59e0b;">
                    <i class="fa-solid fa-book-bookmark"></i>
                </div>
                <div class="service-card-info">
                    <h3>Knowledge Base RAG</h3>
                    <p>Upload PDFs, CSVs, &amp; text files for context retrieval</p>
                </div>
                <i class="fa-solid fa-chevron-right service-arrow"></i>
            </div>
        `;
    }
};

window.backToCategories = function() {
    const catGrid = document.getElementById("serviceCategoriesGrid");
    const subMenuBox = document.getElementById("serviceSubMenuBox");
    const actionBox = document.getElementById("serviceActionBox");

    if (catGrid) catGrid.classList.remove("hidden");
    if (subMenuBox) subMenuBox.classList.add("hidden");
    if (actionBox) actionBox.classList.add("hidden");
};

window.backToSubMenu = function() {
    const subMenuBox = document.getElementById("serviceSubMenuBox");
    const actionBox = document.getElementById("serviceActionBox");

    if (actionBox) actionBox.classList.add("hidden");
    if (subMenuBox) subMenuBox.classList.remove("hidden");
};

window.selectService = function(type) {
    const subMenuBox = document.getElementById("serviceSubMenuBox");
    const actionBox = document.getElementById("serviceActionBox");
    const actionTitle = document.getElementById("serviceActionTitle");

    if (type === "flight") {
        window.closeServicesModal();
        window.openFlightBot();
        return;
    } else if (type === "vault") {
        window.closeServicesModal();
        if (window.openVaultSection) window.openVaultSection();
        return;
    } else if (type === "rag") {
        window.closeServicesModal();
        if (window.openRagSection) window.openRagSection();
        return;
    }

    if (!actionBox || !actionTitle) return;

    if (subMenuBox) subMenuBox.classList.add("hidden");
    actionBox.classList.remove("hidden");
    document.querySelectorAll(".service-form").forEach(f => f.classList.add("hidden"));

    if (type === "email") {
        actionTitle.innerHTML = "📧 Send Email / Gmail";
        document.getElementById("formEmail")?.classList.remove("hidden");
    } else if (type === "whatsapp") {
        actionTitle.innerHTML = "💬 Send WhatsApp Message";
        document.getElementById("formWhatsApp")?.classList.remove("hidden");
    } else if (type === "telegram") {
        actionTitle.innerHTML = "✈️ Send Telegram Message";
        document.getElementById("formTelegram")?.classList.remove("hidden");
    } else if (type === "movie") {
        actionTitle.innerHTML = "🎬 Movie Ticket Booking";
        document.getElementById("formMovie")?.classList.remove("hidden");
    } else if (type === "hotel") {
        actionTitle.innerHTML = "🏨 Hotel Room Booking";
        document.getElementById("formHotel")?.classList.remove("hidden");
    }
};

window.closeServiceAction = function() {
    const actionBox = document.getElementById("serviceActionBox");
    if (actionBox) actionBox.classList.add("hidden");
};

// "Chat with Bot" — the generic assistant. Never touches SkyBot's DOM/state.
window.openChatSection = function() {
    const hero = document.getElementById("welcomeHero");
    const appLayout = document.getElementById("appLayout");
    const skyLayout = document.getElementById("skyBotLayout");
    const hotelLayout = document.getElementById("hotelBotLayout");
    if (hero) hero.classList.add("hidden");
    if (appLayout) appLayout.classList.remove("hidden");
    if (skyLayout) skyLayout.classList.add("hidden");
    if (hotelLayout) hotelLayout.classList.add("hidden");
};

window.showWelcomeHero = function() {
    const hero = document.getElementById("welcomeHero");
    const appLayout = document.getElementById("appLayout");
    const skyLayout = document.getElementById("skyBotLayout");
    const hotelLayout = document.getElementById("hotelBotLayout");
    if (hero) hero.classList.remove("hidden");
    if (appLayout) appLayout.classList.add("hidden");
    if (skyLayout) skyLayout.classList.add("hidden");
    if (hotelLayout) hotelLayout.classList.add("hidden");
};

// ---------------------------------------------------------------------------
// SKYBOT — Rich welcome hero shown inside the empty chat window
// ---------------------------------------------------------------------------
function getSkyWelcomeHTML() {
    return `
        <div class="sky-welcome animate-in">
            <div class="sky-welcome-plane"><i class="fa-solid fa-plane"></i></div>
            <h2>Where would you like to fly today?</h2>
            <p>I'll search live flights, compare fares, suggest the fastest routes, and help book your journey.</p>
            <div class="sky-cta-row">
                <button type="button" class="sky-cta-btn" data-prompt="Search live flights from Delhi to Mumbai on 2026-07-26"><i class="fa-solid fa-plane-departure"></i> Search Delhi → Mumbai</button>
                <button type="button" class="sky-cta-btn" data-prompt="Book a flight ticket to Goa for the weekend"><i class="fa-solid fa-umbrella-beach"></i> Goa Weekend</button>
                <button type="button" class="sky-cta-btn" data-prompt="Show me international flight options"><i class="fa-solid fa-earth-asia"></i> International Flights</button>
                <button type="button" class="sky-cta-btn" data-prompt="What is the cheapest flight available today"><i class="fa-solid fa-tags"></i> Cheapest Today</button>
            </div>
        </div>
    `;
}

// ---------------------------------------------------------------------------
// SKYBOT — Collapsible cockpit: auto-compacts once a conversation starts so
// the chat reply is never buried below the fold, with a manual override.
// ---------------------------------------------------------------------------
let skyCockpitManualOverride = false;

window.toggleSkyCockpit = function() {
    const cockpit = document.getElementById("skyCockpitPanel");
    if (!cockpit) return;
    skyCockpitManualOverride = true;
    cockpit.classList.toggle("sky-compact");
};

function collapseSkyCockpit() {
    if (skyCockpitManualOverride) return;
    const cockpit = document.getElementById("skyCockpitPanel");
    if (cockpit) cockpit.classList.add("sky-compact");
}

function expandSkyCockpit() {
    skyCockpitManualOverride = false;
    const cockpit = document.getElementById("skyCockpitPanel");
    if (cockpit) cockpit.classList.remove("sky-compact");
}

function flashSkyGlow() {
    const cockpit = document.getElementById("skyCockpitPanel");
    if (!cockpit) return;
    cockpit.classList.remove("sky-glow");
    void cockpit.offsetWidth;
    cockpit.classList.add("sky-glow");
}

// ---------------------------------------------------------------------------
// SKYBOT — Recent searches & pinned flights (localStorage, per-browser)
// ---------------------------------------------------------------------------
function getSkyRecentSearches() {
    try {
        return JSON.parse(localStorage.getItem(SKY_RECENT_KEY)) || [];
    } catch (e) {
        return [];
    }
}

function addSkyRecentSearch(orig, dest) {
    let list = getSkyRecentSearches().filter(r => !(r.orig === orig && r.dest === dest));
    list.unshift({ orig, dest, ts: Date.now() });
    list = list.slice(0, 5);
    localStorage.setItem(SKY_RECENT_KEY, JSON.stringify(list));
    renderSkyRecentSearches();
}

function renderSkyRecentSearches() {
    const container = document.getElementById("skyRecentSearches");
    if (!container) return;
    const list = getSkyRecentSearches();
    if (list.length === 0) {
        container.innerHTML = `<div class="sky-empty-mini">No recent searches yet</div>`;
        return;
    }
    container.innerHTML = list.map(r => `
        <div class="sky-recent-item" data-orig="${r.orig}" data-dest="${r.dest}">
            <span><i class="fa-solid fa-plane" style="color:#58E1FF;margin-right:6px;"></i>${r.orig} → ${r.dest}</span>
            <i class="fa-solid fa-chevron-right" style="font-size:0.65rem;color:#64748b;"></i>
        </div>
    `).join("");
}

function getSkyPinnedFlights() {
    try {
        return JSON.parse(localStorage.getItem(SKY_PINNED_KEY)) || [];
    } catch (e) {
        return [];
    }
}

function togglePinFlight(flight, btnEl) {
    let pinned = getSkyPinnedFlights();
    const idx = pinned.findIndex(f => f.flight_number === flight.flight_number);
    if (idx >= 0) {
        pinned.splice(idx, 1);
        if (btnEl) btnEl.classList.remove("pinned");
    } else {
        pinned.unshift(flight);
        pinned = pinned.slice(0, 8);
        if (btnEl) btnEl.classList.add("pinned");
    }
    localStorage.setItem(SKY_PINNED_KEY, JSON.stringify(pinned));
    renderSkyPinnedFlights();
}
window.togglePinFlight = togglePinFlight;

function renderSkyPinnedFlights() {
    const container = document.getElementById("skyPinnedFlights");
    if (!container) return;
    const list = getSkyPinnedFlights();
    if (list.length === 0) {
        container.innerHTML = `<div class="sky-empty-mini">Pin a flight from search results</div>`;
        return;
    }
    container.innerHTML = list.map(f => `
        <div class="sky-pinned-item">
            <span><i class="fa-solid fa-thumbtack" style="color:#FFD54F;margin-right:6px;"></i>${f.airline} · ${f.flight_number}</span>
            <span style="color:#FFD54F;font-weight:700;">₹${f.price_inr.toLocaleString()}</span>
        </div>
    `).join("");
}

// SkyBot lives entirely in its own #skyBotLayout view — a dedicated service
// under "AI Services", not a mode of the general chatbot. Opening it never
// touches #appLayout's DOM, sidebar, or session state, and vice versa.
window.openFlightBot = function() {
    window.closeServicesModal();

    const hero = document.getElementById("welcomeHero");
    const appLayout = document.getElementById("appLayout");
    const skyLayout = document.getElementById("skyBotLayout");
    const hotelLayout = document.getElementById("hotelBotLayout");
    if (hero) hero.classList.add("hidden");
    if (appLayout) appLayout.classList.add("hidden");
    if (skyLayout) skyLayout.classList.remove("hidden");
    if (hotelLayout) hotelLayout.classList.add("hidden");

    expandSkyCockpit();
    renderSkyRecentSearches();
    renderSkyPinnedFlights();

    if (typeof window.skyStartFreshIfEmpty === "function") {
        window.skyStartFreshIfEmpty();
    }
};

window.openHotelBot = function() {
    window.closeServicesModal();

    const hero = document.getElementById("welcomeHero");
    const appLayout = document.getElementById("appLayout");
    const skyLayout = document.getElementById("skyBotLayout");
    const hotelLayout = document.getElementById("hotelBotLayout");
    if (hero) hero.classList.add("hidden");
    if (appLayout) appLayout.classList.add("hidden");
    if (skyLayout) skyLayout.classList.add("hidden");
    if (hotelLayout) hotelLayout.classList.remove("hidden");

    const hotelMessagesInnerEl = document.getElementById("hotelMessagesInner");
    if (hotelMessagesInnerEl && hotelMessagesInnerEl.children.length === 0) {
        hotelMessagesInnerEl.innerHTML = `
            <div class="msg bot-msg animate-in">
                <div class="msg-avatar"><i class="fa-solid fa-bell-concierge" style="color: #f59e0b;"></i></div>
                <div class="msg-bubble">
                    <span class="speaker-name">GrandStay — Luxury Hotel AI Concierge</span>
                    <p>Welcome to <strong>GrandStay Hotel Concierge</strong>! 🏨<br>I can search live hotel availability across any destination, find the cheapest budget stays, recommend luxury 5-star resorts, generate PNR room reservations, and confirm payments via UPI.</p>
                    <small class="hint-text">Try asking: <em>"Find cheapest hotels in Delhi"</em> or <em>"Book a room in Goa"</em></small>
                </div>
            </div>
        `;
    }
};

window.closeHotelBot = function() {
    window.showWelcomeHero();
};

window.toggleHotelCockpit = function() {
    const cockpit = document.getElementById("hotelCockpitPanel");
    if (!cockpit) return;
    cockpit.classList.toggle("sky-compact");
};

window.collapseHotelCockpit = function() {
    const cockpit = document.getElementById("hotelCockpitPanel");
    if (cockpit) cockpit.classList.add("sky-compact");
};

window.expandHotelCockpit = function() {
    const cockpit = document.getElementById("hotelCockpitPanel");
    if (cockpit) cockpit.classList.remove("sky-compact");
};

window.setHotelCity = function(city) {
    const cityInput = document.getElementById("hbCity");
    if (cityInput) cityInput.value = city;
    window.runHotelSearchWidget();
};

window.runHotelSearchWidget = function() {
    const city = document.getElementById("hbCity")?.value.trim() || "Delhi";
    const checkIn = document.getElementById("hbCheckIn")?.value.trim() || "Tomorrow";
    const sort = document.getElementById("hbSort")?.value || "cheapest";

    window.collapseHotelCockpit();
    const prompt = `Search hotels in ${city} sorted by ${sort} check-in ${checkIn}`;
    window.sendHotelPrompt(prompt);
};


window.sendHotelPrompt = function(promptText) {
    if (!promptText) return;
    window.openHotelBot();
    hotelSendMessage(promptText);
};

window.setRouteChip = function(orig, dest) {
    const oInput = document.getElementById("fbOrigin");
    const dInput = document.getElementById("fbDest");
    if (oInput) oInput.value = orig;
    if (dInput) dInput.value = dest;

    window.runRouteSearchWidget();
};

window.swapRouteInputs = function() {
    const oInput = document.getElementById("fbOrigin");
    const dInput = document.getElementById("fbDest");
    const btn = document.getElementById("skySwapBtn");
    if (!oInput || !dInput) return;
    const tmp = oInput.value;
    oInput.value = dInput.value;
    dInput.value = tmp;
    if (btn) {
        btn.classList.toggle("swapped");
    }
};

window.runRouteSearchWidget = async function() {
    const orig = document.getElementById("fbOrigin")?.value.trim() || "Delhi";
    const dest = document.getElementById("fbDest")?.value.trim() || "Mumbai";
    const date = document.getElementById("fbDate")?.value || "2026-07-26";
    const pax = document.getElementById("fbPax")?.value || "1";
    const cls = document.getElementById("fbClass")?.value || "Economy";

    const searchBtn = document.getElementById("skySearchBtn");
    const originalBtnHtml = searchBtn ? searchBtn.innerHTML : "";
    if (searchBtn) {
        searchBtn.classList.remove("sky-pulse");
        void searchBtn.offsetWidth;
        searchBtn.classList.add("sky-pulse", "sky-loading");
        searchBtn.innerHTML = `<i class="fa-solid fa-spinner"></i> Searching…`;
    }

    addSkyRecentSearch(orig, dest);

    let prompt = `Search live flights from ${orig} to ${dest} on ${date}`;
    if (pax && pax !== "1") prompt += ` for ${pax} passengers`;
    if (cls && cls !== "Economy") prompt += ` in ${cls} class`;

    try {
        if (typeof window.skySendMessage === "function") {
            await window.skySendMessage(prompt);
        }
    } finally {
        if (searchBtn) {
            searchBtn.classList.remove("sky-loading");
            searchBtn.innerHTML = originalBtnHtml;
        }
    }
};


document.addEventListener("DOMContentLoaded", () => {


    // DOM Elements
    const chatForm = document.getElementById("chatForm");
    const userInput = document.getElementById("userInput");
    const chatMessages = document.getElementById("chatMessages");
    const messagesInner = document.getElementById("messagesInner");
    const sendBtn = document.getElementById("sendBtn");
    const fileInput = document.getElementById("fileInput");
    const attachBtn = document.getElementById("attachBtn");
    const attachmentPreviewBar = document.getElementById("attachmentPreviewBar");

    const mascotFace = document.getElementById("mascotFace");
    const mascotStatus = document.getElementById("mascotStatus");
    const currentChatTitle = document.getElementById("currentChatTitle");

    // SkyBot — standalone DOM, never shared with the general chat above
    const skyChatForm = document.getElementById("skyChatForm");
    const skyUserInput = document.getElementById("skyUserInput");
    const skySendBtn = document.getElementById("skySendBtn");
    const skyChatMessagesEl = document.getElementById("skyChatMessages");
    const skyMessagesInnerEl = document.getElementById("skyMessagesInner");
    const skyNewSearchBtn = document.getElementById("skyNewSearchBtn");
    let skySessionId = null;

    let currentChatMode = "full"; // "full" vs "memory_only" vs "rag_only"

    // Services Modal & Mode Toggle DOM
    const toggleServicesBtn = document.getElementById("toggleServicesBtn");
    const servicesModal = document.getElementById("servicesModal");
    const closeServicesModalBtn = document.getElementById("closeServicesModalBtn");
    const modeToggleChip = document.getElementById("modeToggleChip");
    const modeLabel = document.getElementById("modeLabel");
    const modeIcon = document.getElementById("modeIcon");


    if (toggleServicesBtn && servicesModal) {
        toggleServicesBtn.addEventListener("click", () => {
            if (!currentUser) {
                openModal("login", "Sign in required to access AI Services Hub.");
                return;
            }
            servicesModal.classList.remove("hidden");
        });
    }
    if (closeServicesModalBtn && servicesModal) {
        closeServicesModalBtn.addEventListener("click", () => {
            servicesModal.classList.add("hidden");
            window.closeServiceAction();
        });
    }


    // Sidebar
    const newChatSidebarBtn = document.getElementById("newChatSidebarBtn");
    const toggleSidebarBtn = document.getElementById("toggleSidebarBtn");
    const chatSidebar = document.getElementById("chatSidebar");
    const sessionSearchInput = document.getElementById("sessionSearchInput");

    // User Auth DOM
    const userPill = document.getElementById("userPill");
    const usernameDisplay = document.getElementById("usernameDisplay");
    const authBtn = document.getElementById("authBtn");
    const logoutBtn = document.getElementById("logoutBtn");

    // Auth Modal DOM
    const authModal = document.getElementById("authModal");
    const closeAuthModal = document.getElementById("closeAuthModal");
    const authTabs = document.getElementById("authTabs");
    const tabLogin = document.getElementById("tabLogin");
    const tabSignup = document.getElementById("tabSignup");
    const authForm = document.getElementById("authForm");

    // Form Groups
    const groupFullName = document.getElementById("groupFullName");
    const groupEmail = document.getElementById("groupEmail");
    const groupLoginIdentifier = document.getElementById("groupLoginIdentifier");
    const groupUsername = document.getElementById("groupUsername");
    const groupConfirmPassword = document.getElementById("groupConfirmPassword");

    // Form Fields
    const authFullName = document.getElementById("authFullName");
    const authEmail = document.getElementById("authEmail");
    const authLoginIdentifier = document.getElementById("authLoginIdentifier");
    const authUsername = document.getElementById("authUsername");
    const authPassword = document.getElementById("authPassword");
    const authConfirmPassword = document.getElementById("authConfirmPassword");

    const authErrorMsg = document.getElementById("authErrorMsg");
    const authSubmitBtn = document.getElementById("authSubmitBtn");
    const authModalTitle = document.getElementById("authModalTitle");
    const authModalSubtitle = document.getElementById("authModalSubtitle");

    // OTP
    const otpView = document.getElementById("otpView");
    const otpForm = document.getElementById("otpForm");
    const authOtpCode = document.getElementById("authOtpCode");
    const otpErrorMsg = document.getElementById("otpErrorMsg");
    const otpSubmitBtn = document.getElementById("otpSubmitBtn");
    const resendOtpBtn = document.getElementById("resendOtpBtn");
    const otpNoticeText = document.getElementById("otpNoticeText");

    const dashboardGrid = document.getElementById("dashboardGrid");

    // Panels
    const vaultPanel = document.getElementById("vaultPanel");
    const flowPanel = document.getElementById("flowPanel");
    const ragPanel = document.getElementById("ragPanel");

    const toggleVaultBtn = document.getElementById("toggleVaultBtn");
    const toggleFlowBtn = document.getElementById("toggleFlowBtn");
    const toggleRagBtn = document.getElementById("toggleRagBtn");

    const quickVaultBtn = document.getElementById("quickVaultBtn");
    const quickFlowBtn = document.getElementById("quickFlowBtn");

    const closeVaultBtn = document.getElementById("closeVaultBtn");
    const closeFlowBtn = document.getElementById("closeFlowBtn");
    const closeRagBtn = document.getElementById("closeRagBtn");

    // RAG
    const ragDropBox = document.getElementById("ragDropBox");
    const ragFileInput = document.getElementById("ragFileInput");
    const ragDocList = document.getElementById("ragDocList");
    const ragBadge = document.getElementById("ragBadge");
    const ragChunkBadge = document.getElementById("ragChunkBadge");
    const ragSearchInput = document.getElementById("ragSearchInput");

    const vaultBadge = document.getElementById("vaultBadge");
    const quickVaultCount = document.getElementById("quickVaultCount");
    const memoryCountBadge = document.getElementById("memoryCountBadge");

    const memoryGrid = document.getElementById("memoryGrid");
    const memorySearchInput = document.getElementById("memorySearchInput");
    const customMemoryInput = document.getElementById("customMemoryInput");
    const addMemoryBtn = document.getElementById("addMemoryBtn");

    const step1 = document.getElementById("step1");
    const step2 = document.getElementById("step2");
    const step3 = document.getElementById("step3");
    const step4 = document.getElementById("step4");

    const retrievedPill = document.getElementById("retrievedPill");
    const retrievedText = document.getElementById("retrievedText");
    const extractedPill = document.getElementById("extractedPill");
    const extractedText = document.getElementById("extractedText");

    const itemsToday = document.getElementById("itemsToday");
    const itemsYesterday = document.getElementById("itemsYesterday");
    const itemsPrevious7 = document.getElementById("itemsPrevious7");
    const itemsOlder = document.getElementById("itemsOlder");
    const emptyHistory = document.getElementById("emptyHistory");

    // State
    let currentUser = null;
    let currentSessionId = null;
    let authMode = "login";
    let pendingVerificationEmail = "";
    let currentAttachment = null;
    let allSessions = [];
    let allMemories = [];

    const mascotIcons = {
        idle: '<i class="fa-solid fa-robot"></i>',
        thinking: '<i class="fa-solid fa-circle-notch fa-spin"></i>',
        success: '<i class="fa-solid fa-check"></i>',
        learning: '<i class="fa-solid fa-brain"></i>',
        reset: '<i class="fa-solid fa-rotate"></i>',
        error: '<i class="fa-solid fa-triangle-exclamation"></i>'
    };

    initAuthState();

    function initAuthState() {
        const savedUser = localStorage.getItem("bot_o_brain_user");
        if (savedUser) {
            try {
                currentUser = JSON.parse(savedUser);
                updateAuthUI();
            } catch (e) {
                currentUser = null;
            }
        }
        fetchStats();
        fetchMemories();
        fetchSessions();
    }

    function getAuthHeaders() {
        const headers = { "Content-Type": "application/json" };
        if (currentUser && currentUser.id) {
            headers["X-User-Id"] = currentUser.id;
        }
        return headers;
    }

    function updateAuthUI() {
        const vaultBadge = document.getElementById("vaultBadge");
        const ragBadge = document.getElementById("ragBadge");

        if (currentUser) {
            const displayName = currentUser.full_name
                ? `${currentUser.full_name}`
                : currentUser.username;
            usernameDisplay.innerText = displayName;
            authBtn.classList.add("hidden");
            logoutBtn.classList.remove("hidden");
            userPill.classList.remove("hidden");
        } else {
            usernameDisplay.innerText = "Guest Mode";
            authBtn.classList.remove("hidden");
            logoutBtn.classList.add("hidden");
            userPill.classList.remove("hidden");
            if (vaultBadge) vaultBadge.innerText = "Locked";
            if (ragBadge) ragBadge.innerText = "Locked";
        }
    }

    // Auth Modal
    if (authBtn) authBtn.addEventListener("click", () => openModal());
    if (closeAuthModal) closeAuthModal.addEventListener("click", () => closeModal());

    if (logoutBtn) {
        logoutBtn.addEventListener("click", () => {
            localStorage.removeItem("bot_o_brain_user");
            currentUser = null;
            currentSessionId = null;
            updateAuthUI();
            messagesInner.innerHTML = `
                <div class="msg bot-msg animate-in">
                    <div class="msg-avatar"><i class="fa-solid fa-robot"></i></div>
                    <div class="msg-bubble">
                        <span class="speaker-name">BOT-O-BRAIN</span>
                        <p>You have been signed out. Sign in anytime to access your private memory vault.</p>
                    </div>
                </div>
            `;
            fetchStats();
            fetchMemories();
            fetchSessions();
            openModal();
        });
    }

    if (tabLogin) tabLogin.addEventListener("click", () => setAuthMode("login"));
    if (tabSignup) tabSignup.addEventListener("click", () => setAuthMode("signup"));

    function setAuthMode(mode) {
        authMode = mode;
        authErrorMsg.classList.add("hidden");
        otpErrorMsg.classList.add("hidden");

        if (mode === "login") {
            authForm.classList.remove("hidden");
            authTabs.classList.remove("hidden");
            otpView.classList.add("hidden");

            tabLogin.classList.add("active");
            tabSignup.classList.remove("active");

            groupLoginIdentifier.classList.remove("hidden");
            groupFullName.classList.add("hidden");
            groupEmail.classList.add("hidden");
            groupUsername.classList.add("hidden");
            groupConfirmPassword.classList.add("hidden");

            authSubmitBtn.innerText = "Sign In";
            authModalTitle.innerText = "Welcome Back";
            authModalSubtitle.innerText = "Sign in to access your private memory vault and chat history.";

        } else if (mode === "signup") {
            authForm.classList.remove("hidden");
            authTabs.classList.remove("hidden");
            otpView.classList.add("hidden");

            tabSignup.classList.add("active");
            tabLogin.classList.remove("active");

            groupLoginIdentifier.classList.add("hidden");
            groupFullName.classList.remove("hidden");
            groupEmail.classList.remove("hidden");
            groupUsername.classList.remove("hidden");
            groupConfirmPassword.classList.remove("hidden");

            authSubmitBtn.innerText = "Create Account";
            authModalTitle.innerText = "Create Account";
            authModalSubtitle.innerText = "Register with your email for a secure, verified account.";

        } else if (mode === "otp") {
            authForm.classList.add("hidden");
            authTabs.classList.add("hidden");
            otpView.classList.remove("hidden");

            authModalTitle.innerText = "Email Verification";
            authModalSubtitle.innerText = "Enter the 6-digit verification code sent to your email.";
        }
    }

    function showAuthNotice(msg) {
        if (authModalSubtitle) {
            authModalSubtitle.innerHTML = `<span style="color: #ef4444; font-weight: 600;">🔒 ${escapeHtml(msg)}</span>`;
        }
    }

    function openModal(mode = "login", notice = null) {
        authModal.classList.remove("hidden");
        setAuthMode(mode);
        if (notice) showAuthNotice(notice);
    }

    function closeModal() {
        authModal.classList.add("hidden");
    }

    // Auth Form Submit
    authForm.addEventListener("submit", async (e) => {
        e.preventDefault();
        authErrorMsg.classList.add("hidden");

        if (authMode === "signup") {
            const fullName = authFullName.value.trim();
            const email = authEmail.value.trim();
            const username = authUsername.value.trim();
            const password = authPassword.value.trim();
            const confirmPassword = authConfirmPassword.value.trim();

            if (!fullName || !email || !username || !password || !confirmPassword) {
                showAuthError("All fields are required.");
                return;
            }
            if (password !== confirmPassword) {
                showAuthError("Passwords do not match.");
                return;
            }

            authSubmitBtn.innerText = "Sending verification code...";

            try {
                const res = await fetch("/api/auth/signup", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({
                        full_name: fullName,
                        email: email,
                        username: username,
                        password: password,
                        confirm_password: confirmPassword
                    })
                });

                const data = await res.json();
                if (!res.ok) throw new Error(data.detail || "Signup failed.");

                pendingVerificationEmail = email;
                if (data.otp_demo) {
                    authOtpCode.value = data.otp_demo;
                    otpNoticeText.innerHTML = `
                        Verification code sent to <strong>${escapeHtml(email)}</strong>
                        <div style="margin-top: 12px; padding: 12px; background: rgba(245, 158, 11, 0.12); border: 1px dashed #f59e0b; border-radius: 10px; text-align: center;">
                            <div style="font-size: 0.75rem; color: #d97706; font-weight: 700; text-transform: uppercase; letter-spacing: 1px;">🧪 Testing Demo OTP Code</div>
                            <div style="font-size: 1.8rem; font-weight: 800; color: #1e293b; letter-spacing: 8px; font-family: monospace; margin-top: 4px;">${data.otp_demo}</div>
                        </div>
                    `;
                } else {
                    otpNoticeText.innerText = `A 6-digit verification code has been sent to ${email}`;
                }
                setAuthMode("otp");

            } catch (err) {
                showAuthError(err.message);
            } finally {
                authSubmitBtn.innerText = "Create Account";
            }

        } else if (authMode === "login") {
            const loginIdentifier = authLoginIdentifier.value.trim();
            const password = authPassword.value.trim();

            if (!loginIdentifier || !password) {
                showAuthError("Please enter your credentials.");
                return;
            }

            authSubmitBtn.innerText = "Signing in...";

            try {
                const res = await fetch("/api/auth/login", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({
                        login_identifier: loginIdentifier,
                        password: password
                    })
                });

                const data = await res.json();
                if (!res.ok) {
                    if (data.detail && data.detail.includes("Email not verified")) {
                        pendingVerificationEmail = loginIdentifier;
                        otpNoticeText.innerText = "Please verify your email to continue.";
                        setAuthMode("otp");
                        throw new Error(data.detail);
                    }
                    throw new Error(data.detail || "Login failed.");
                }

                currentUser = data.user;
                localStorage.setItem("bot_o_brain_user", JSON.stringify(currentUser));
                updateAuthUI();
                closeModal();

                authLoginIdentifier.value = "";
                authPassword.value = "";

                currentSessionId = null;
                fetchStats();
                fetchMemories();
                fetchSessions();
                setMascot("success", `Welcome back, ${currentUser.full_name || currentUser.username}`);
                setTimeout(() => setMascot("idle", "Ready to assist"), 2500);

            } catch (err) {
                showAuthError(err.message);
            } finally {
                authSubmitBtn.innerText = "Sign In";
            }
        }
    });

    // OTP Submit
    otpForm.addEventListener("submit", async (e) => {
        e.preventDefault();
        const otpCode = authOtpCode.value.trim();
        if (!otpCode || otpCode.length !== 6) {
            showOtpError("Please enter a valid 6-digit code.");
            return;
        }

        otpSubmitBtn.innerText = "Verifying...";
        otpErrorMsg.classList.add("hidden");

        try {
            const res = await fetch("/api/auth/verify-otp", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    email: pendingVerificationEmail,
                    otp_code: otpCode
                })
            });

            const data = await res.json();
            if (!res.ok) throw new Error(data.detail || "Verification failed.");

            currentUser = data.user;
            localStorage.setItem("bot_o_brain_user", JSON.stringify(currentUser));
            updateAuthUI();
            closeModal();

            authOtpCode.value = "";
            currentSessionId = null;

            fetchStats();
            fetchMemories();
            fetchSessions();
            setMascot("success", `Account verified. Welcome, ${currentUser.full_name}`);
            setTimeout(() => setMascot("idle", "Ready to assist"), 2500);

        } catch (err) {
            showOtpError(err.message);
        } finally {
            otpSubmitBtn.innerText = "Verify Account";
        }
    });

    // Resend OTP
    if (resendOtpBtn) {
        resendOtpBtn.addEventListener("click", async (e) => {
            e.preventDefault();
            if (!pendingVerificationEmail) return;

            resendOtpBtn.innerText = "Resending...";
            try {
                const res = await fetch("/api/auth/resend-otp", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ email: pendingVerificationEmail })
                });

                const data = await res.json();
                if (!res.ok) throw new Error(data.detail || "Resend failed.");

                if (data.otp_demo) {
                    authOtpCode.value = data.otp_demo;
                    otpNoticeText.innerHTML = `
                        New verification code sent to <strong>${escapeHtml(pendingVerificationEmail)}</strong>
                        <div style="margin-top: 12px; padding: 12px; background: rgba(245, 158, 11, 0.12); border: 1px dashed #f59e0b; border-radius: 10px; text-align: center;">
                            <div style="font-size: 0.75rem; color: #d97706; font-weight: 700; text-transform: uppercase; letter-spacing: 1px;">🧪 Testing Demo OTP Code</div>
                            <div style="font-size: 1.8rem; font-weight: 800; color: #1e293b; letter-spacing: 8px; font-family: monospace; margin-top: 4px;">${data.otp_demo}</div>
                        </div>
                    `;
                }
            } catch (err) {
                showOtpError(err.message);
            } finally {
                resendOtpBtn.innerText = "Resend OTP";
            }
        });
    }

    function showAuthError(msg) {
        authErrorMsg.innerText = msg;
        authErrorMsg.classList.remove("hidden");
    }

    function showOtpError(msg) {
        otpErrorMsg.innerText = msg;
        otpErrorMsg.classList.remove("hidden");
    }

    // Sidebar Toggle
    if (toggleSidebarBtn && chatSidebar) {
        toggleSidebarBtn.addEventListener("click", () => {
            chatSidebar.classList.toggle("collapsed");
        });
    }

    // New Chat
    if (newChatSidebarBtn) newChatSidebarBtn.addEventListener("click", () => startNewChatSession());

    // Textarea
    if (userInput) {
        userInput.addEventListener("keydown", (e) => {
            if (e.key === "Enter" && !e.shiftKey) {
                e.preventDefault();
                chatForm.dispatchEvent(new Event("submit", { cancelable: true, bubbles: true }));
            }
        });
        userInput.addEventListener("input", () => {
            userInput.style.height = "auto";
            userInput.style.height = Math.min(userInput.scrollHeight, 140) + "px";
        });
    }

    // Drawer Toggles
    if (toggleVaultBtn) toggleVaultBtn.addEventListener("click", () => {
        if (!currentUser) {
            openModal("login", "Sign in required to view and manage your Memory Vault.");
            return;
        }
        toggleDrawer(vaultPanel, toggleVaultBtn);
    });
    if (toggleFlowBtn) toggleFlowBtn.addEventListener("click", () => toggleDrawer(flowPanel, toggleFlowBtn));
    if (toggleRagBtn) toggleRagBtn.addEventListener("click", () => {
        if (!currentUser) {
            openModal("login", "Sign in required to upload & query Knowledge Base documents.");
            return;
        }
        toggleDrawer(ragPanel, toggleRagBtn);
        fetchRagDocuments();
    });

    if (quickVaultBtn) quickVaultBtn.addEventListener("click", () => toggleDrawer(vaultPanel, toggleVaultBtn));
    if (quickFlowBtn) quickFlowBtn.addEventListener("click", () => toggleDrawer(flowPanel, toggleFlowBtn));

    if (closeVaultBtn) closeVaultBtn.addEventListener("click", () => closeDrawer(vaultPanel, toggleVaultBtn));
    if (closeFlowBtn) closeFlowBtn.addEventListener("click", () => closeDrawer(flowPanel, toggleFlowBtn));
    if (closeRagBtn) closeRagBtn.addEventListener("click", () => closeDrawer(ragPanel, toggleRagBtn));

    function closeAllDrawersExcept(panelEl) {
        [vaultPanel, flowPanel, ragPanel].forEach(p => {
            if (p && p !== panelEl) p.classList.add("hidden");
        });
        [toggleVaultBtn, toggleFlowBtn, toggleRagBtn, quickVaultBtn, quickFlowBtn].forEach(b => {
            b?.classList.remove("active-toggle");
        });
    }

    function toggleDrawer(panelEl, btnEl) {
        const isHidden = panelEl.classList.contains("hidden");
        closeAllDrawersExcept(isHidden ? panelEl : null);
        if (isHidden) {
            panelEl.classList.remove("hidden");
            btnEl?.classList.add("active-toggle");
        } else {
            panelEl.classList.add("hidden");
            btnEl?.classList.remove("active-toggle");
        }
        updateGridColumns();
    }

    function closeDrawer(panelEl, btnEl) {
        panelEl.classList.add("hidden");
        btnEl?.classList.remove("active-toggle");
        updateGridColumns();
    }

    function updateGridColumns() {
        const isVaultHidden = vaultPanel.classList.contains("hidden");
        const isFlowHidden = flowPanel.classList.contains("hidden");
        const isRagHidden = ragPanel.classList.contains("hidden");

        dashboardGrid.classList.remove("has-one-drawer", "has-two-drawers", "chat-hero-mode");

        const visibleCount = [isVaultHidden, isFlowHidden, isRagHidden].filter(h => !h).length;

        if (visibleCount >= 2) {
            dashboardGrid.classList.add("has-two-drawers");
        } else if (visibleCount === 1) {
            dashboardGrid.classList.add("has-one-drawer");
        } else {
            dashboardGrid.classList.add("chat-hero-mode");
        }
    }

    // RAG Upload
    if (ragDropBox && ragFileInput) {
        ragDropBox.addEventListener("click", () => ragFileInput.click());
        ragFileInput.addEventListener("change", (e) => {
            if (e.target.files && e.target.files.length > 0) {
                Array.from(e.target.files).forEach(uploadRagFile);
            }
        });

        ragDropBox.addEventListener("dragover", (e) => {
            e.preventDefault();
            ragDropBox.classList.add("drag-over");
        });
        ragDropBox.addEventListener("dragleave", (e) => {
            e.preventDefault();
            ragDropBox.classList.remove("drag-over");
        });
        ragDropBox.addEventListener("drop", (e) => {
            e.preventDefault();
            ragDropBox.classList.remove("drag-over");
            if (e.dataTransfer && e.dataTransfer.files && e.dataTransfer.files.length > 0) {
                Array.from(e.dataTransfer.files).forEach(uploadRagFile);
            }
        });
    }

    async function uploadRagFile(file) {
        if (!file) return;
        const formData = new FormData();
        formData.append("file", file);

        try {
            const res = await fetch("/api/rag/upload", {
                method: "POST",
                headers: { "X-User-Id": currentUser ? currentUser.id : "usr_guest" },
                body: formData
            });
            const data = await res.json();
            if (!res.ok) throw new Error(data.detail || "Ingestion failed");

            fetchRagDocuments();
        } catch (err) {
            alert("Upload Error: " + err.message);
        }
    }

    async function fetchRagDocuments() {
        try {
            const res = await fetch("/api/rag/documents", { headers: getAuthHeaders() });
            const data = await res.json();
            renderRagDocuments(data.documents || []);
        } catch (err) {
            console.error("Fetch RAG error:", err);
        }
    }

    function renderRagDocuments(docs) {
        if (!ragDocList) return;
        if (!docs || docs.length === 0) {
            ragDocList.innerHTML = `<div class="empty-state"><p>No documents ingested yet.</p></div>`;
            if (ragBadge) ragBadge.innerText = "0";
            if (ragChunkBadge) ragChunkBadge.innerText = "0 Files";
            return;
        }

        if (ragBadge) ragBadge.innerText = docs.length;
        let totalChunks = 0;
        let html = "";

        docs.forEach(doc => {
            totalChunks += doc.chunk_count;
            const ext = doc.filename.split(".").pop().toLowerCase();
            const icon = ext === "pdf" ? "fa-file-pdf" : (ext === "csv" ? "fa-file-csv" : (ext === "md" || ext === "txt" ? "fa-file-lines" : "fa-file-code"));
            html += `
                <div class="rag-doc-item">
                    <div class="rag-doc-info">
                        <div class="rag-doc-title"><i class="fa-solid ${icon}"></i> <span>${escapeHtml(doc.filename)}</span></div>
                        <div class="rag-doc-meta">${doc.chunk_count} chunks · Ingested ${doc.created_at}</div>
                    </div>
                    <button type="button" class="action-btn btn-delete-rag" data-filename="${escapeHtml(doc.filename)}" title="Delete"><i class="fa-solid fa-trash-can"></i></button>
                </div>
            `;
        });

        if (ragChunkBadge) ragChunkBadge.innerText = `${docs.length} Files (${totalChunks} Chunks)`;
        ragDocList.innerHTML = html;

        document.querySelectorAll(".btn-delete-rag").forEach(btn => {
            btn.addEventListener("click", async () => {
                const filename = btn.getAttribute("data-filename");
                if (!filename) return;
                if (btn.classList.contains("confirm-delete")) {
                    try {
                        await fetch(`/api/rag/documents/${encodeURIComponent(filename)}`, {
                            method: "DELETE",
                            headers: getAuthHeaders()
                        });
                        fetchRagDocuments();
                    } catch (err) {
                        alert("Delete error: " + err.message);
                    }
                } else {
                    btn.classList.add("confirm-delete");
                    btn.innerHTML = `<span style="font-size:0.7rem; font-weight:600;">Confirm?</span>`;
                    setTimeout(() => {
                        if (btn) {
                            btn.classList.remove("confirm-delete");
                            btn.innerHTML = `<i class="fa-solid fa-trash-can"></i>`;
                        }
                    }, 3000);
                }
            });
        });
    }

    // File Upload (Attachment)
    async function uploadSingleFile(file) {
        if (!file) return;
        if (attachBtn) attachBtn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i>';
        const formData = new FormData();
        formData.append("file", file);

        try {
            const res = await fetch("/api/upload-file", {
                method: "POST",
                headers: { "X-User-Id": currentUser ? currentUser.id : "usr_guest" },
                body: formData
            });
            const data = await res.json();
            if (!res.ok) throw new Error(data.detail || "Upload failed");

            currentAttachment = data;
            renderAttachmentPreview();
        } catch (err) {
            alert("File upload error: " + err.message);
        } finally {
            if (attachBtn) attachBtn.innerHTML = '<i class="fa-solid fa-paperclip"></i>';
        }
    }

    if (attachBtn && fileInput) {
        attachBtn.addEventListener("click", () => fileInput.click());
        fileInput.addEventListener("change", (e) => {
            if (e.target.files && e.target.files[0]) {
                uploadSingleFile(e.target.files[0]);
            }
        });
    }

    // Clipboard Paste
    if (userInput) {
        userInput.addEventListener("paste", (e) => {
            const items = e.clipboardData && e.clipboardData.items;
            if (!items) return;
            for (let i = 0; i < items.length; i++) {
                if (items[i].kind === "file") {
                    const file = items[i].getAsFile();
                    if (file) {
                        e.preventDefault();
                        uploadSingleFile(file);
                        break;
                    }
                }
            }
        });
    }

    // Drag & Drop on chat form
    if (chatForm) {
        chatForm.addEventListener("dragover", (e) => {
            e.preventDefault();
            chatForm.classList.add("drag-over");
        });
        chatForm.addEventListener("dragleave", (e) => {
            e.preventDefault();
            chatForm.classList.remove("drag-over");
        });
        chatForm.addEventListener("drop", (e) => {
            e.preventDefault();
            chatForm.classList.remove("drag-over");
            if (e.dataTransfer && e.dataTransfer.files && e.dataTransfer.files[0]) {
                uploadSingleFile(e.dataTransfer.files[0]);
            }
        });
    }

    function renderAttachmentPreview() {
        if (!currentAttachment || !attachmentPreviewBar) return;
        attachmentPreviewBar.classList.remove("hidden");
        const icon = currentAttachment.file_type === "image" ? "fa-image" : (currentAttachment.file_type === "pdf" ? "fa-file-pdf" : "fa-file-lines");
        attachmentPreviewBar.innerHTML = `
            <div class="attachment-chip">
                <i class="fa-solid ${icon}"></i>
                <span>${escapeHtml(currentAttachment.filename)}</span>
                <button type="button" class="btn-remove-attachment" id="removeAttachmentBtn"><i class="fa-solid fa-xmark"></i></button>
            </div>
        `;
        document.getElementById("removeAttachmentBtn")?.addEventListener("click", () => {
            currentAttachment = null;
            if (fileInput) fileInput.value = "";
            attachmentPreviewBar.classList.add("hidden");
            attachmentPreviewBar.innerHTML = "";
        });
    }

    // Chat Submit
    chatForm.addEventListener("submit", (e) => {
        e.preventDefault();
        const text = userInput.value.trim();
        if (text || currentAttachment) {
            sendMessage(text, currentAttachment);
            userInput.value = "";
            userInput.style.height = "auto";
            currentAttachment = null;
            if (fileInput) fileInput.value = "";
            if (attachmentPreviewBar) {
                attachmentPreviewBar.classList.add("hidden");
                attachmentPreviewBar.innerHTML = "";
            }
        }
    });

    // Quick Prompts (general chat) & SkyBot interactive elements (delegated —
    // survives dynamic re-renders). The two assistants never share a handler:
    // general chips go through sendMessage(), SkyBot elements through
    // skySendMessage() — keeping their state completely separate.
    document.addEventListener("click", (e) => {
        const generalPrompt = e.target.closest(".prompt-chip[data-prompt]");
        if (generalPrompt) {
            const prompt = generalPrompt.getAttribute("data-prompt");
            if (prompt) sendMessage(prompt);
            return;
        }

        const skyPrompt = e.target.closest(".sky-action-card[data-prompt], .sky-cta-btn[data-prompt]");
        if (skyPrompt) {
            const prompt = skyPrompt.getAttribute("data-prompt");
            if (prompt) skySendMessage(prompt);
            return;
        }

        const destChip = e.target.closest(".sky-dest-chip[data-dest]");
        if (destChip) {
            window.setRouteChip(destChip.getAttribute("data-orig") || "Delhi", destChip.getAttribute("data-dest"));
            return;
        }

        const recentItem = e.target.closest(".sky-recent-item[data-dest]");
        if (recentItem) {
            window.setRouteChip(recentItem.getAttribute("data-orig") || "Delhi", recentItem.getAttribute("data-dest"));
            return;
        }
    });

    const skySwapBtn = document.getElementById("skySwapBtn");
    if (skySwapBtn) skySwapBtn.addEventListener("click", () => window.swapRouteInputs());

    // Add Memory
    addMemoryBtn.addEventListener("click", async () => {
        const text = customMemoryInput.value.trim();
        if (!text) return;
        try {
            await fetch("/api/memories", {
                method: "POST",
                headers: getAuthHeaders(),
                body: JSON.stringify({ text })
            });
            customMemoryInput.value = "";
            fetchMemories();
            setMascot("learning", "Memory added successfully");
            setTimeout(() => setMascot("idle", "Ready to assist"), 2000);
        } catch (err) {
            console.error("Add memory error:", err);
        }
    });

    // Memory Search
    memorySearchInput.addEventListener("input", (e) => {
        const query = e.target.value.toLowerCase();
        const filtered = allMemories.filter(m => m.text.toLowerCase().includes(query));
        renderMemories(filtered);
    });

    // Session Search
    if (sessionSearchInput) {
        sessionSearchInput.addEventListener("input", (e) => {
            const query = e.target.value.toLowerCase();
            const filtered = allSessions.filter(s => s.title.toLowerCase().includes(query));
            renderSessionsList(filtered);
        });
    }

    // =========================================================================
    // API & SESSION MANAGEMENT
    // =========================================================================

    async function fetchSessions() {
        try {
            const res = await fetch("/api/sessions?assistant_type=general", { headers: getAuthHeaders() });
            const data = await res.json();
            allSessions = data.sessions || [];
            renderSessionsList(allSessions);

            if (!currentSessionId && allSessions.length > 0) {
                selectSession(allSessions[0].id);
            } else if (!currentSessionId) {
                startNewChatSession();
            }
        } catch (err) {
            console.error("Fetch sessions error:", err);
        }
    }

    function renderSessionsList(sessions) {
        itemsToday.innerHTML = "";
        itemsYesterday.innerHTML = "";
        itemsPrevious7.innerHTML = "";
        itemsOlder.innerHTML = "";

        let todayCount = 0, yesterdayCount = 0, prev7Count = 0, olderCount = 0;

        const now = new Date();
        const todayStart = new Date(now.getFullYear(), now.getMonth(), now.getDate()).getTime();
        const yesterdayStart = todayStart - 86400000;
        const prev7Start = todayStart - (7 * 86400000);

        sessions.forEach(s => {
            const date = new Date(s.updated_at || s.created_at).getTime();
            const el = createSessionItemElement(s);

            if (date >= todayStart) {
                itemsToday.appendChild(el);
                todayCount++;
            } else if (date >= yesterdayStart) {
                itemsYesterday.appendChild(el);
                yesterdayCount++;
            } else if (date >= prev7Start) {
                itemsPrevious7.appendChild(el);
                prev7Count++;
            } else {
                itemsOlder.appendChild(el);
                olderCount++;
            }
        });

        document.getElementById("groupToday").style.display = todayCount > 0 ? "block" : "none";
        document.getElementById("groupYesterday").style.display = yesterdayCount > 0 ? "block" : "none";
        document.getElementById("groupPrevious7").style.display = prev7Count > 0 ? "block" : "none";
        document.getElementById("groupOlder").style.display = olderCount > 0 ? "block" : "none";

        if (sessions.length === 0) {
            emptyHistory.classList.remove("hidden");
        } else {
            emptyHistory.classList.add("hidden");
        }
    }

    function createSessionItemElement(session) {
        const item = document.createElement("div");
        item.className = `session-item ${session.id === currentSessionId ? "active" : ""}`;
        item.dataset.id = session.id;

        item.innerHTML = `
            <div class="session-title-wrapper">
                <i class="fa-regular fa-message"></i>
                <span class="session-title">${escapeHtml(session.title || "New Chat")}</span>
            </div>
            <div class="session-actions">
                <button type="button" class="btn-icon-sm btn-rename" title="Rename"><i class="fa-solid fa-pen"></i></button>
                <button type="button" class="btn-icon-sm btn-delete" title="Delete"><i class="fa-solid fa-trash"></i></button>
            </div>
        `;

        item.addEventListener("click", (e) => {
            if (e.target.closest(".btn-rename") || e.target.closest(".btn-delete")) return;
            selectSession(session.id);
        });

        const renameBtn = item.querySelector(".btn-rename");
        const deleteBtn = item.querySelector(".btn-delete");

        if (renameBtn) {
            renameBtn.addEventListener("click", (e) => {
                e.preventDefault();
                e.stopPropagation();

                const titleWrapper = item.querySelector(".session-title-wrapper");
                const currentTitleSpan = item.querySelector(".session-title");
                if (!titleWrapper || !currentTitleSpan) return;
                if (item.querySelector(".inline-title-input")) return;

                const input = document.createElement("input");
                input.type = "text";
                input.className = "inline-title-input";
                input.value = session.title || "New Chat";

                currentTitleSpan.style.display = "none";
                titleWrapper.appendChild(input);
                input.focus();
                input.select();

                let isSaved = false;
                const saveTitle = async () => {
                    if (isSaved) return;
                    isSaved = true;
                    const newTitle = input.value.trim();
                    if (newTitle && newTitle !== session.title) {
                        try {
                            await fetch(`/api/sessions/${session.id}`, {
                                method: "PATCH",
                                headers: getAuthHeaders(),
                                body: JSON.stringify({ title: newTitle })
                            });
                            if (currentSessionId === session.id) {
                                currentChatTitle.innerHTML = `${escapeHtml(newTitle)} <span class="status-dot"></span>`;
                            }
                            fetchSessions();
                        } catch (err) {
                            console.error("Rename session error:", err);
                        }
                    } else {
                        input.remove();
                        currentTitleSpan.style.display = "";
                    }
                };

                input.addEventListener("keydown", (evt) => {
                    if (evt.key === "Enter") {
                        evt.preventDefault();
                        saveTitle();
                    } else if (evt.key === "Escape") {
                        input.remove();
                        currentTitleSpan.style.display = "";
                    }
                });

                input.addEventListener("blur", () => saveTitle());
            });
        }

        if (deleteBtn) {
            deleteBtn.addEventListener("click", async (e) => {
                e.preventDefault();
                e.stopPropagation();

                if (deleteBtn.classList.contains("confirm-delete")) {
                    try {
                        await fetch(`/api/sessions/${session.id}`, {
                            method: "DELETE",
                            headers: getAuthHeaders()
                        });
                        if (currentSessionId === session.id) {
                            currentSessionId = null;
                        }
                        fetchSessions();
                    } catch (err) {
                        console.error("Delete session error:", err);
                    }
                } else {
                    deleteBtn.classList.add("confirm-delete");
                    deleteBtn.innerHTML = '<i class="fa-solid fa-check"></i>';
                    deleteBtn.style.color = 'var(--accent-red)';

                    setTimeout(() => {
                        if (deleteBtn && deleteBtn.classList.contains("confirm-delete")) {
                            deleteBtn.classList.remove("confirm-delete");
                            deleteBtn.innerHTML = '<i class="fa-solid fa-trash"></i>';
                            deleteBtn.style.color = '';
                        }
                    }, 3500);
                }
            });
        }

        return item;
    }

    async function selectSession(sessionId) {
        currentSessionId = sessionId;
        threadIdDisplay.innerText = sessionId;

        document.querySelectorAll(".session-item").forEach(el => {
            el.classList.toggle("active", el.dataset.id === sessionId);
        });

        try {
            const res = await fetch(`/api/sessions/${sessionId}/messages`, { headers: getAuthHeaders() });
            if (!res.ok) throw new Error("Failed to load messages");
            const data = await res.json();

            const session = data.session;
            const messages = data.messages || [];

            currentChatTitle.innerHTML = `${escapeHtml(session.title)} <span class="status-dot"></span>`;
            renderMessageHistory(messages);
        } catch (err) {
            console.error("Select session error:", err);
        }
    }

    function renderMessageHistory(messages) {
        messagesInner.innerHTML = "";

        if (messages.length === 0) {
            messagesInner.innerHTML = `
                <div class="msg bot-msg animate-in">
                    <div class="msg-avatar"><i class="fa-solid fa-robot"></i></div>
                    <div class="msg-bubble">
                        <span class="speaker-name">BOT-O-BRAIN</span>
                        <p>Welcome. I'm ready to assist you. Share facts, ask questions, or upload documents — I'll remember everything.</p>
                        <small class="hint-text"><i class="fa-solid fa-circle-info"></i> Start typing below to begin this conversation.</small>
                    </div>
                </div>
            `;
            return;
        }


        messages.forEach(m => {
            const msgEl = document.createElement("div");
            msgEl.className = `msg ${m.role === "user" ? "user-msg" : "bot-msg"}`;

            const avatarHtml = m.role === "user"
                ? '<i class="fa-solid fa-user"></i>'
                : '<i class="fa-solid fa-robot"></i>';
            const nameHtml = m.role === "user"
                ? (currentUser ? currentUser.full_name || currentUser.username : "You")
                : "BOT-O-BRAIN";

            let pillsHtml = "";
            let toolBadgesHtml = "";

            if (m.role === "bot") {
                const toolsList = m.executed_tools || [];
                const contentText = m.content || "";
                const memoriesList = m.retrieved_memories || [];

                const badges = [];

                // Check explicit executed_tools or infer from content & context
                if (toolsList.some(t => t.tool === "web_search") || contentText.includes("http") || contentText.includes("Search")) {
                    badges.push(`<span class="tool-trace-badge tool-badge-web"><i class="fa-solid fa-magnifying-glass"></i> 🔍 Web Search Executed</span>`);
                }
                if (toolsList.some(t => t.tool === "python_repl") || contentText.includes("```python") || contentText.includes("Calculated") || contentText.includes("def ")) {
                    badges.push(`<span class="tool-trace-badge tool-badge-python"><i class="fa-solid fa-code"></i> 🐍 Python REPL Executed</span>`);
                }
                if (toolsList.some(t => t.tool === "rag_search") || memoriesList.some(mem => typeof mem === "string" && mem.includes("Document"))) {
                    badges.push(`<span class="tool-trace-badge tool-badge-rag"><i class="fa-solid fa-book-bookmark"></i> 📚 Document RAG Search</span>`);
                }
                if (memoriesList.length > 0 && !badges.some(b => b.includes("RAG"))) {
                    badges.push(`<span class="tool-trace-badge tool-badge-web" style="background: rgba(99, 102, 241, 0.12); color: #6366f1; border-color: rgba(99, 102, 241, 0.3);"><i class="fa-solid fa-brain"></i> 🧠 Vector Memory Active</span>`);
                }

                if (badges.length > 0) {
                    toolBadgesHtml = `<div class="tool-traces-wrapper" style="margin-bottom: 8px;">${badges.join(" ")}</div>`;
                }

                if (memoriesList.length > 0) {
                    const cleanList = memoriesList.map(mem => {
                        if (typeof mem === "string" && mem.startsWith("[Document Knowledge '")) {
                            const parts = mem.split("'");
                            return `📄 ${parts[1] || 'Document'}`;
                        }
                        return mem;
                    });
                    const uniqueClean = Array.from(new Set(cleanList));
                    pillsHtml += `<small class="hint-text"><i class="fa-solid fa-brain"></i> Context: ${uniqueClean.map(escapeHtml).join(" · ")}</small>`;
                }
                if (m.new_facts && m.new_facts.length > 0) {
                    pillsHtml += `<small class="hint-text" style="color: var(--color-emerald);"><i class="fa-solid fa-floppy-disk"></i> Saved: ${m.new_facts.map(escapeHtml).join(" · ")}</small>`;
                }
            }

            msgEl.innerHTML = `
                <div class="msg-avatar">${avatarHtml}</div>
                <div class="msg-bubble">
                    <span class="speaker-name">${nameHtml}</span>
                    ${toolBadgesHtml}
                    <p>${formatMessageContent(m.content)}</p>
                    ${pillsHtml}
                </div>
            `;
            messagesInner.appendChild(msgEl);
        });

        scrollToBottom();
    }

    async function startNewChatSession() {
        try {
            const res = await fetch("/api/sessions?assistant_type=general", {
                method: "POST",
                headers: getAuthHeaders()
            });
            const session = await res.json();
            currentSessionId = session.id;
            threadIdDisplay.innerText = session.id;
            currentChatTitle.innerHTML = `New Chat <span class="status-dot"></span>`;

            messagesInner.innerHTML = `
                <div class="msg bot-msg animate-in">
                    <div class="msg-avatar"><i class="fa-solid fa-robot"></i></div>
                    <div class="msg-bubble">
                        <span class="speaker-name">BOT-O-BRAIN</span>
                        <p>New conversation started. How can I help you?</p>
                    </div>
                </div>
            `;

            fetchSessions();
            setMascot("idle", "Ready for a new conversation");
        } catch (err) {
            console.error("New chat error:", err);
        }
    }

    async function sendMessage(userText, attachment = null) {
        appendMessage("user", userText, [], [], attachment);

        setMascot("thinking", attachment ? "Analyzing attachment..." : "Processing your message...");

        activateFlowStep(step1);
        activateFlowStep(step2);

        try {
            const res = await fetch("/api/chat", {
                method: "POST",
                headers: getAuthHeaders(),
                body: JSON.stringify({
                    message: userText,
                    session_id: currentSessionId,
                    chat_mode: currentChatMode,
                    assistant_type: "general",
                    attachment: attachment
                })


            });

            if (!res.ok) {
                throw new Error(`Server returned ${res.status}`);
            }

            const data = await res.json();

            if (data.thread_id) {
                currentSessionId = data.thread_id;
                threadIdDisplay.innerText = data.thread_id;
            }

            if (data.session && data.session.title) {
                currentChatTitle.innerHTML = `${escapeHtml(data.session.title)} <span class="status-dot"></span>`;
            }

            if (data.retrieved_memories && data.retrieved_memories.length > 0) {
                retrievedText.innerText = `${data.retrieved_memories.length} memories retrieved`;
                retrievedPill.classList.remove("hidden");
            } else {
                retrievedText.innerText = "0 memories";
                retrievedPill.classList.add("hidden");
            }

            activateFlowStep(step3);
            appendMessage("bot", data.reply, data.retrieved_memories, data.new_facts, null, data.executed_tools);

            if (data.new_facts && data.new_facts.length > 0) {
                extractedText.innerText = `${data.new_facts.length} facts saved`;
                extractedPill.classList.remove("hidden");
                activateFlowStep(step4);
                setMascot("learning", `${data.new_facts.length} new fact(s) saved to memory`);
                fetchMemories();
            } else {
                setMascot("success", "Response generated");
            }

            fetchStats();
            fetchSessions();

            setTimeout(() => {
                setMascot("idle", "Ready to assist");
                resetFlowSteps();
            }, 4000);

        } catch (err) {
            console.error("Chat error:", err);
            appendMessage("bot", "An error occurred while processing your request. Please try again.");
            setMascot("error", "Error processing request");
            resetFlowSteps();
        }
    }
    window.sendMessage = sendMessage;

    // ---------------------------------------------------------------------------
    // SKYBOT — Typing indicator with a moving plane icon
    // ---------------------------------------------------------------------------
    function showSkyTyping() {
        hideSkyTyping();
        const el = document.createElement("div");
        el.className = "msg bot-msg animate-in";
        el.id = "skyTypingMsg";
        el.innerHTML = `
            <div class="msg-avatar"><i class="fa-solid fa-plane-up"></i></div>
            <div class="msg-bubble">
                <span class="speaker-name">SkyBot — Flight AI Assistant</span>
                <div class="sky-typing">
                    <div class="sky-typing-track"><i class="fa-solid fa-plane"></i></div>
                    <span class="sky-typing-label">Scanning live flight routes…</span>
                </div>
            </div>
        `;
        skyMessagesInnerEl.appendChild(el);
        skyScrollToBottom();
    }

    function hideSkyTyping() {
        document.getElementById("skyTypingMsg")?.remove();
    }

    function skyScrollToBottom() {
        skyChatMessagesEl.scrollTop = skyChatMessagesEl.scrollHeight;
    }

    // ---------------------------------------------------------------------------
    // SKYBOT — Flight search results & booking confirmations rendered as
    // premium airline ticket / boarding-pass cards instead of plain markdown.
    // ---------------------------------------------------------------------------
    function renderSkyTicketCard(f, origin, destination) {
        const initials = (f.airline || "??").split(" ").map(w => w[0]).join("").slice(0, 2).toUpperCase();
        const flightAttr = JSON.stringify(f).replace(/"/g, "&quot;").replace(/'/g, "&#39;");
        const safeOrigin = escapeHtml(origin || "Origin");
        const safeDest = escapeHtml(destination || "Destination");
        return `
            <div class="sky-ticket">
                <div class="sky-ticket-head">
                    <div class="sky-airline">
                        <div class="sky-airline-logo">${escapeHtml(initials)}</div>
                        <span class="sky-airline-name">${escapeHtml(f.airline)}</span>
                        <span class="sky-flight-code">${escapeHtml(f.flight_number)}</span>
                    </div>
                    ${f.seats_available ? `<span class="sky-seats-left"><i class="fa-solid fa-chair"></i> ${f.seats_available} seats left</span>` : ""}
                </div>
                <div class="sky-ticket-route">
                    <div class="sky-route-node">
                        <div class="sky-route-time">${escapeHtml(f.departure_time || "—")}</div>
                        <div class="sky-route-city">${safeOrigin}</div>
                    </div>
                    <div class="sky-route-path">
                        <span class="sky-route-duration">${escapeHtml(f.duration || "")}</span>
                        <div class="sky-route-line"></div>
                        <i class="fa-solid fa-plane"></i>
                    </div>
                    <div class="sky-route-node">
                        <div class="sky-route-time">${escapeHtml(f.arrival_time || "—")}</div>
                        <div class="sky-route-city">${safeDest}</div>
                    </div>
                </div>
                <div class="sky-ticket-foot">
                    <div class="sky-ticket-meta">
                        <span><i class="fa-solid fa-suitcase"></i> 15kg baggage</span>
                        <span><i class="fa-solid fa-chair"></i> Seat select</span>
                    </div>
                    <div style="display:flex;align-items:center;gap:8px;">
                        <div class="sky-price">₹${Number(f.price_inr).toLocaleString()} <small>/person</small></div>
                        <button type="button" class="btn-pin-ticket" onclick='window.togglePinFlight(${flightAttr}, this)' title="Pin flight"><i class="fa-solid fa-thumbtack"></i></button>
                        <button type="button" class="btn-book-ticket" onclick="window.sendMessage('Book flight ${f.flight_number.replace(/'/g, "")} (${f.airline.replace(/'/g, "")}) from ${(origin || "").replace(/'/g, "")} to ${(destination || "").replace(/'/g, "")} for Priyanshu')">Book</button>
                    </div>
                </div>
            </div>
        `;
    }

    function renderSkyBoardingPass(d) {
        const statusHtml = d.status === "confirmed"
            ? `<span class="sky-bp-status sky-bp-confirmed"><i class="fa-solid fa-circle-check"></i> CONFIRMED (PAID)</span>`
            : `<span class="sky-bp-status sky-bp-pending"><i class="fa-solid fa-hourglass-half"></i> PENDING PAYMENT</span>`;

        const fareHtml = d.fare
            ? `<div class="sky-bp-fare">
                    <div><span class="sky-bp-label">TOTAL FARE</span><div class="sky-bp-fare-amount">₹${escapeHtml(d.fare)}</div></div>
                    ${d.payLink ? `<a class="btn-pay-now" href="${escapeHtml(d.payLink)}" target="_blank" rel="noopener"><i class="fa-solid fa-credit-card"></i> Pay Now</a>` : ""}
               </div>`
            : "";

        return `
            <div class="sky-boarding-pass">
                ${statusHtml}
                <div class="sky-bp-grid">
                    <div class="sky-bp-field"><span class="sky-bp-label">PNR CODE</span><span class="sky-bp-value mono">${escapeHtml(d.pnr || "—")}</span></div>
                    <div class="sky-bp-field"><span class="sky-bp-label">PASSENGER</span><span class="sky-bp-value">${escapeHtml(d.passenger || "—")}</span></div>
                    <div class="sky-bp-field"><span class="sky-bp-label">FLIGHT</span><span class="sky-bp-value">${escapeHtml(d.flight || "—")}</span></div>
                    <div class="sky-bp-field"><span class="sky-bp-label">ROUTE</span><span class="sky-bp-value">${escapeHtml(d.origin)} ➔ ${escapeHtml(d.destination)}</span></div>
                    <div class="sky-bp-field"><span class="sky-bp-label">DATE &amp; TIME</span><span class="sky-bp-value">${escapeHtml(d.dateTime || "—")}</span></div>
                    <div class="sky-bp-field"><span class="sky-bp-label">${d.method ? "PAYMENT METHOD" : "STATUS"}</span><span class="sky-bp-value">${escapeHtml(d.method || (d.status === "confirmed" ? "Confirmed" : "Awaiting payment"))}</span></div>
                </div>
                ${fareHtml}
            </div>
        `;
    }

    // The LLM re-narrates raw tool output in its own words rather than
    // relaying it verbatim, so search-result phrasing varies call to call
    // (bullets, numbered lists, inline vs multi-line fields). This scans
    // line-by-line for the invariant tokens (bold "Airline (CODE)", a
    // Departure/Arrival mention, a ₹ price) instead of one rigid template.
    function extractFlightTickets(text) {
        const lines = text.split("\n");
        const flightStartRe = /\*\*(.+?)\s*\(([A-Za-z0-9][A-Za-z0-9\-\s]{1,9})\)\*\*/;
        const depRe = /Departure:\s*([^|,\n]+?)(?:\s*[|,]|$)/i;
        const arrRe = /Arrival:\s*([^|,\n]+?)(?:\s*[|,]|$)/i;
        const durRe = /\((\d+\s*h\s*\d*\s*m?|\d+\s*m)\)/i;
        const priceRe = /(?:Price|Fare)\s*:?\s*₹\s*([\d,]+)/i;
        const seatsRe = /Seats\s*Left:\s*(\d+)/i;

        const tickets = [];
        let current = null;

        const pushCurrent = () => {
            if (current && current.airline && current.price_inr) tickets.push(current);
        };

        for (const line of lines) {
            const startMatch = line.match(flightStartRe);
            if (startMatch) {
                pushCurrent();
                current = {
                    airline: startMatch[1].trim(),
                    flight_number: startMatch[2].trim(),
                    departure_time: "",
                    arrival_time: "",
                    duration: "",
                    price_inr: null,
                    seats_available: null
                };
            }
            if (!current) continue;

            const dep = line.match(depRe);
            if (dep && !current.departure_time) current.departure_time = dep[1].trim();
            const arr = line.match(arrRe);
            if (arr && !current.arrival_time) current.arrival_time = arr[1].trim();
            const dur = line.match(durRe);
            if (dur && !current.duration) current.duration = dur[1].replace(/\s+/g, "");
            const price = line.match(priceRe);
            if (price && !current.price_inr) current.price_inr = parseInt(price[1].replace(/,/g, ""), 10);
            const seats = line.match(seatsRe);
            if (seats && !current.seats_available) current.seats_available = parseInt(seats[1], 10);
        }
        pushCurrent();
        return tickets;
    }

    function extractSkyRoute(text) {
        const m = text.match(/([A-Za-z][A-Za-z ]{2,20}?)\s*(?:➔|->|→)\s*([A-Za-z][A-Za-z ]{2,20}?)[\s,.:\n]/);
        if (m) return { origin: m[1].trim(), destination: m[2].trim() };
        const oInput = document.getElementById("fbOrigin");
        const dInput = document.getElementById("fbDest");
        return { origin: oInput ? oInput.value : "", destination: dInput ? dInput.value : "" };
    }

    function parseSkyFlightContent(text) {
        if (!text) return null;

        // 1. Live flight search results -> airline ticket cards
        const tickets = extractFlightTickets(text);
        if (tickets.length > 0) {
            const { origin, destination } = extractSkyRoute(text);
            const cardsHtml = tickets.map(f => renderSkyTicketCard(f, origin, destination)).join("");
            return `<div class="sky-ticket-grid">${cardsHtml}</div><p class="hint-text"><i class="fa-solid fa-circle-info"></i> Tap "Book" on a ticket, or tell me which flight you'd like to reserve.</p>`;
        }

        // 2. Flight reserved — pending payment boarding pass
        if (text.includes("FLIGHT TICKET RESERVED")) {
            const pnr = (text.match(/PNR Code\*\*:\s*`(.+?)`/) || [])[1];
            if (pnr) {
                const passenger = (text.match(/Passenger\*\*:\s*(.+)/) || [])[1];
                const flight = (text.match(/Flight\*\*:\s*(.+)/) || [])[1];
                const route = text.match(/Route\*\*:\s*(.+?)\s*➔\s*(.+)/) || [];
                const dateTime = (text.match(/Date & Time\*\*:\s*(.+)/) || [])[1];
                const fare = (text.match(/Total Fare\*\*:\s*₹([\d,]+)/) || [])[1];
                const payLink = (text.match(/Quick Link:\s*(\S+)/) || [])[1];
                return renderSkyBoardingPass({
                    pnr, passenger, flight,
                    origin: route[1] || "", destination: route[2] || "",
                    dateTime, fare, payLink, status: "pending"
                });
            }
        }

        // 3. Payment confirmed — confirmed boarding pass
        if (text.includes("PAYMENT SUCCESSFUL")) {
            const pnr = (text.match(/PNR Code\*\*:\s*`(.+?)`/) || [])[1];
            if (pnr) {
                const passenger = (text.match(/Passenger\*\*:\s*(.+)/) || [])[1];
                const flight = (text.match(/Flight\*\*:\s*(.+)/) || [])[1];
                const route = text.match(/Route\*\*:\s*(.+?)\s*➔\s*(.+)/) || [];
                const dateTime = (text.match(/Departure\*\*:\s*(.+)/) || [])[1];
                const method = (text.match(/Payment Method\*\*:\s*(.+)/) || [])[1];
                return renderSkyBoardingPass({
                    pnr, passenger, flight,
                    origin: route[1] || "", destination: route[2] || "",
                    dateTime, method, status: "confirmed"
                });
            }
        }

        return null;
    }

    function appendMessage(role, text, memories = [], newFacts = [], attachment = null, executedTools = []) {
        const msgEl = document.createElement("div");
        msgEl.className = `msg ${role === "user" ? "user-msg" : "bot-msg"} animate-in`;

        const avatarHtml = role === "user" ? '<i class="fa-solid fa-user"></i>' : '<i class="fa-solid fa-robot"></i>';
        const nameHtml = role === "user"
            ? (currentUser ? currentUser.full_name || currentUser.username : "You")
            : "BOT-O-BRAIN";

        let attachmentHtml = "";
        if (attachment) {
            if (attachment.file_type === "image") {
                attachmentHtml = `<img src="${attachment.data}" class="msg-attachment-img" alt="${escapeHtml(attachment.filename)}">`;
            } else {
                const icon = attachment.file_type === "pdf" ? "fa-file-pdf" : "fa-file-lines";
                attachmentHtml = `<div class="msg-attachment-badge"><i class="fa-solid ${icon}"></i> <span>${escapeHtml(attachment.filename)}</span></div>`;
            }
        }

        let toolBadgesHtml = "";
        let pillsHtml = "";

        if (role === "bot") {
            const badges = [];
            const contentText = text || "";

            if ((executedTools && executedTools.some(t => t.tool === "web_search")) || contentText.includes("http") || contentText.includes("Search")) {
                badges.push(`<span class="tool-trace-badge tool-badge-web"><i class="fa-solid fa-magnifying-glass"></i> 🔍 Web Search Executed</span>`);
            }
            if ((executedTools && executedTools.some(t => t.tool === "python_repl")) || contentText.includes("```python") || contentText.includes("Calculated") || contentText.includes("def ")) {
                badges.push(`<span class="tool-trace-badge tool-badge-python"><i class="fa-solid fa-code"></i> 🐍 Python REPL Executed</span>`);
            }
            if ((executedTools && executedTools.some(t => t.tool === "rag_search")) || (memories && memories.some(mem => typeof mem === "string" && mem.includes("Document")))) {
                badges.push(`<span class="tool-trace-badge tool-badge-rag"><i class="fa-solid fa-book-bookmark"></i> 📚 Document RAG Search</span>`);
            }
            if (memories && memories.length > 0 && !badges.some(b => b.includes("RAG"))) {
                badges.push(`<span class="tool-trace-badge tool-badge-web" style="background: rgba(99, 102, 241, 0.12); color: #6366f1; border-color: rgba(99, 102, 241, 0.3);"><i class="fa-solid fa-brain"></i> 🧠 Vector Memory Active</span>`);
            }

            if (badges.length > 0) {
                toolBadgesHtml = `<div class="tool-traces-wrapper" style="margin-bottom: 8px;">${badges.join(" ")}</div>`;
            }

            if (memories && memories.length > 0) {
                pillsHtml += `<small class="hint-text"><i class="fa-solid fa-brain"></i> Context: ${memories.join("; ")}</small>`;
            }
            if (newFacts && newFacts.length > 0) {
                pillsHtml += `<small class="hint-text" style="color: var(--color-emerald);"><i class="fa-solid fa-floppy-disk"></i> Saved: ${newFacts.join("; ")}</small>`;
            }
        }

        msgEl.innerHTML = `
            <div class="msg-avatar">${avatarHtml}</div>
            <div class="msg-bubble">
                <span class="speaker-name">${nameHtml}</span>
                ${toolBadgesHtml}
                <p>${formatMessageContent(text)}</p>
                ${attachmentHtml}
                ${pillsHtml}
            </div>
        `;

        messagesInner.appendChild(msgEl);
        scrollToBottom();
    }

    // =========================================================================
    // SKYBOT ENGINE — fully standalone chat loop, separate session, separate
    // DOM, separate history. This is what makes SkyBot a distinct "service"
    // rather than a mode bolted onto the general chatbot above.
    // =========================================================================
    function appendSkyMessage(role, text, memories = [], newFacts = [], executedTools = []) {
        const msgEl = document.createElement("div");
        msgEl.className = `msg ${role === "user" ? "user-msg" : "bot-msg"} animate-in`;

        const avatarHtml = role === "user" ? '<i class="fa-solid fa-user"></i>' : '<i class="fa-solid fa-plane-up"></i>';
        const nameHtml = role === "user"
            ? (currentUser ? currentUser.full_name || currentUser.username : "You")
            : "SkyBot — Flight AI Assistant";

        const skyCardHtml = role === "bot" ? parseSkyFlightContent(text) : null;
        const bodyHtml = skyCardHtml ? skyCardHtml : `<p>${formatMessageContent(text)}</p>`;

        let pillsHtml = "";
        if (role === "bot" && newFacts && newFacts.length > 0) {
            pillsHtml += `<small class="hint-text" style="color: var(--color-emerald);"><i class="fa-solid fa-floppy-disk"></i> Saved: ${newFacts.map(escapeHtml).join("; ")}</small>`;
        }

        msgEl.innerHTML = `
            <div class="msg-avatar">${avatarHtml}</div>
            <div class="msg-bubble">
                <span class="speaker-name">${nameHtml}</span>
                ${bodyHtml}
                ${pillsHtml}
            </div>
        `;

        skyMessagesInnerEl.appendChild(msgEl);
        skyScrollToBottom();
    }

    async function skySendMessage(userText) {
        if (!userText || !userText.trim()) return;

        if (skyMessagesInnerEl.querySelector(".sky-welcome")) {
            skyMessagesInnerEl.innerHTML = "";
        }
        collapseSkyCockpit();

        appendSkyMessage("user", userText);
        showSkyTyping();
        flashSkyGlow();

        try {
            const res = await fetch("/api/chat", {
                method: "POST",
                headers: getAuthHeaders(),
                body: JSON.stringify({
                    message: userText,
                    session_id: skySessionId,
                    chat_mode: "full",
                    assistant_type: "flight"
                })
            });

            if (!res.ok) {
                throw new Error(`Server returned ${res.status}`);
            }

            const data = await res.json();
            if (data.thread_id) {
                skySessionId = data.thread_id;
            }

            hideSkyTyping();
            flashSkyGlow();
            appendSkyMessage("bot", data.reply, data.retrieved_memories, data.new_facts, data.executed_tools);
        } catch (err) {
            console.error("SkyBot chat error:", err);
            hideSkyTyping();
            appendSkyMessage("bot", "An error occurred while processing your request. Please try again.");
        }
    }
    window.skySendMessage = skySendMessage;

    // Starts a brand-new SkyBot conversation: fresh session, welcome hero back.
    function skyStartNewSearch() {
        skySessionId = null;
        skyMessagesInnerEl.innerHTML = getSkyWelcomeHTML();
        expandSkyCockpit();
    }
    window.skyStartFreshIfEmpty = function() {
        if (!skyMessagesInnerEl.innerHTML.trim()) {
            skyStartNewSearch();
        }
    };

    if (skyChatForm) {
        skyChatForm.addEventListener("submit", (e) => {
            e.preventDefault();
            const text = skyUserInput.value.trim();
            if (!text) return;
            skyUserInput.value = "";
            skyUserInput.style.height = "auto";
            skySendMessage(text);
        });
    }
    if (skyUserInput) {
        skyUserInput.addEventListener("input", () => {
            skyUserInput.style.height = "auto";
            skyUserInput.style.height = `${skyUserInput.scrollHeight}px`;
        });
        skyUserInput.addEventListener("keydown", (e) => {
            if (e.key === "Enter" && !e.shiftKey) {
                e.preventDefault();
                skyChatForm.requestSubmit();
            }
        });
    }
    if (skyNewSearchBtn) {
        skyNewSearchBtn.addEventListener("click", skyStartNewSearch);
    }

    // =========================================================================
    // GRANDSTAY HOTEL CONCIERGE ENGINE
    // =========================================================================
    const hotelChatForm = document.getElementById("hotelChatForm");
    const hotelUserInput = document.getElementById("hotelUserInput");

    function parseHotelContent(text) {
        if (!text) return null;

        // Check if text is a hotel reservation confirmation voucher
        if (text.includes("PNR-HTL") || text.includes("HOTEL ROOM RESERVED") || text.includes("HOTEL PAYMENT CONFIRMED")) {
            const pnrMatch = text.match(/PNR-HTL\d+/i);
            const pnr = pnrMatch ? pnrMatch[0].toUpperCase() : "PNR-HTL";
            const isPaid = text.includes("PAID") || text.includes("CONFIRMED");

            return `
                <div class="hotel-voucher-card animate-in">
                    <div class="hotel-voucher-header">
                        <div class="hotel-brand"><i class="fa-solid fa-hotel" style="color: #f59e0b;"></i> <span>GrandStay Luxury Reservation</span></div>
                        <span class="hotel-pnr-badge">${pnr}</span>
                    </div>
                    <div class="hotel-voucher-body">
                        <div>${formatMessageContent(text)}</div>
                    </div>
                    <div class="hotel-voucher-footer">
                        ${!isPaid ? `
                            <button type="button" class="btn-hotel-card-pay" onclick="window.sendHotelPrompt('Pay for Hotel PNR ${pnr} using UPI')">
                                <i class="fa-solid fa-credit-card"></i> Pay via UPI Now
                            </button>
                        ` : `
                            <span class="hotel-status-confirmed"><i class="fa-solid fa-circle-check"></i> E-Voucher Issued & Paid</span>
                        `}
                    </div>
                </div>
            `;
        }

        // Check if text is hotel search recommendations list
        if (text.includes("Hotel Recommendations") || text.includes("Cheapest & Best Value Hotels")) {
            return `
                <div class="hotel-results-wrapper animate-in">
                    <div class="hotel-results-header"><i class="fa-solid fa-bell-concierge" style="color: #f59e0b;"></i> Live Hotel Search Results</div>
                    <div class="hotel-results-body">${formatMessageContent(text)}</div>
                    <div class="hotel-results-footer" style="margin-top: 10px; padding-top: 8px; border-top: 1px dashed rgba(245, 158, 11, 0.2);">
                        <small style="color: #94a3b8;"><i class="fa-solid fa-shield-halved"></i> Reply <em>"Book the cheapest hotel"</em> or <em>"Book room in Delhi"</em> to reserve instantly!</small>
                    </div>
                </div>
            `;
        }

        return null;
    }

    function appendHotelMessage(role, text) {
        const hotelMessagesInnerEl = document.getElementById("hotelMessagesInner");
        if (!hotelMessagesInnerEl) return;

        const msgEl = document.createElement("div");
        msgEl.className = `msg ${role === "user" ? "user-msg" : "bot-msg"} animate-in`;

        const avatarHtml = role === "user" ? '<i class="fa-solid fa-user"></i>' : '<i class="fa-solid fa-bell-concierge" style="color: #f59e0b;"></i>';
        const nameHtml = role === "user"
            ? (currentUser ? currentUser.full_name || currentUser.username : "You")
            : "GrandStay — Luxury Hotel AI Concierge";

        const hotelCardHtml = role === "bot" ? parseHotelContent(text) : null;
        const bodyHtml = hotelCardHtml ? hotelCardHtml : `<p>${formatMessageContent(text)}</p>`;

        msgEl.innerHTML = `
            <div class="msg-avatar">${avatarHtml}</div>
            <div class="msg-bubble">
                <span class="speaker-name">${nameHtml}</span>
                ${bodyHtml}
            </div>
        `;

        hotelMessagesInnerEl.appendChild(msgEl);
        hotelMessagesInnerEl.scrollTop = hotelMessagesInnerEl.scrollHeight;
    }

    async function hotelSendMessage(userText) {
        const hotelMessagesInnerEl = document.getElementById("hotelMessagesInner");
        if (!userText || !userText.trim()) return;

        appendHotelMessage("user", userText);

        try {
            const res = await fetch("/api/chat", {
                method: "POST",
                headers: getAuthHeaders(),
                body: JSON.stringify({
                    message: userText,
                    session_id: currentSessionId,
                    chat_mode: "full",
                    assistant_type: "general"
                })
            });

            if (!res.ok) throw new Error(`Server returned ${res.status}`);
            const data = await res.json();
            appendHotelMessage("bot", data.reply);
        } catch (err) {
            appendHotelMessage("bot", "⚠️ GrandStay Error: Unable to communicate with hotel booking engine.");
        }
    }
    window.hotelSendMessage = hotelSendMessage;

    if (hotelChatForm) {
        hotelChatForm.addEventListener("submit", (e) => {
            e.preventDefault();
            const text = hotelUserInput.value.trim();
            if (!text) return;
            hotelUserInput.value = "";
            hotelUserInput.style.height = "auto";
            hotelSendMessage(text);
        });
    }
    if (hotelUserInput) {
        hotelUserInput.addEventListener("input", () => {
            hotelUserInput.style.height = "auto";
            hotelUserInput.style.height = `${hotelUserInput.scrollHeight}px`;
        });
        hotelUserInput.addEventListener("keydown", (e) => {
            if (e.key === "Enter" && !e.shiftKey) {
                e.preventDefault();
                hotelChatForm.requestSubmit();
            }
        });
    }

    async function fetchMemories() {
        try {
            const res = await fetch("/api/memories", { headers: getAuthHeaders() });
            const data = await res.json();
            allMemories = data.memories || [];

            vaultBadge.innerText = data.count || 0;
            quickVaultCount.innerText = data.count || 0;
            memoryCountBadge.innerText = `${data.count || 0} Facts`;

            renderMemories(allMemories);
        } catch (err) {
            console.error("Fetch memories error:", err);
        }
    }

    function renderMemories(memories) {
        memoryGrid.innerHTML = "";
        if (!memories || memories.length === 0) {
            memoryGrid.innerHTML = `
                <div class="empty-state">
                    <div class="empty-icon"><i class="fa-solid fa-folder-open"></i></div>
                    <p>No memories stored yet</p>
                    <small>Start chatting to build your memory vault.</small>
                </div>
            `;
            return;
        }

        memories.forEach((mem) => {
            const card = document.createElement("div");
            card.className = "memory-card";

            card.innerHTML = `
                <span>${escapeHtml(mem.text)}</span>
                <button class="delete-mem-btn" data-id="${mem.id}" title="Delete">
                    <i class="fa-solid fa-trash-can"></i>
                </button>
            `;

            card.querySelector(".delete-mem-btn").addEventListener("click", async () => {
                await deleteMemory(mem.id);
            });

            memoryGrid.appendChild(card);
        });
    }

    async function deleteMemory(id) {
        try {
            await fetch(`/api/memories/${id}`, {
                method: "DELETE",
                headers: getAuthHeaders()
            });
            fetchMemories();
            setMascot("reset", "Memory deleted");
            setTimeout(() => setMascot("idle", "Ready to assist"), 2000);
        } catch (err) {
            console.error("Delete memory error:", err);
        }
    }

    async function fetchStats() {
        try {
            const res = await fetch("/api/stats", { headers: getAuthHeaders() });
            const data = await res.json();
            if (data.model) {
                modelName.innerText = data.model;
            }
        } catch (err) {
            console.error("Fetch stats error:", err);
        }
    }

    // Helpers
    function setMascot(state, statusMsg) {
        if (mascotFace) mascotFace.innerHTML = mascotIcons[state] || mascotIcons.idle;
        if (mascotStatus) mascotStatus.innerText = statusMsg;
    }

    function scrollToBottom() {
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    function activateFlowStep(stepEl) {
        if (stepEl) stepEl.classList.add("active-step");
    }

    function resetFlowSteps() {
        [step1, step2, step3, step4].forEach(s => {
            if (s) s.classList.remove("active-step");
        });
    }

    function formatMessageContent(text) {
        let safe = escapeHtml(text);
        safe = safe.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
        safe = safe.replace(/\*(.*?)\*/g, '<em>$1</em>');
        safe = safe.replace(/\n/g, '<br>');
        return safe;
    }

    function escapeHtml(str) {
        return (str || '')
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;")
            .replace(/"/g, "&quot;")
            .replace(/'/g, "&#039;");
    }

    // =========================================================================
    // GLOBAL HERO & NAVIGATION ACTIONS
    // =========================================================================
    // openServicesModal / closeServicesModal / openChatSection / showWelcomeHero
    // are defined once, at the top of this
    // file (module scope) — they also manage #skyBotLayout visibility, so
    // there must be exactly one definition, not a second one here.

    window.openVaultSection = function() {
        window.openChatSection();
        const vaultPanel = document.getElementById("vaultPanel");
        const toggleVaultBtn = document.getElementById("toggleVaultBtn");
        if (vaultPanel) toggleDrawer(vaultPanel, toggleVaultBtn);
    };

    window.openRagSection = function() {
        window.openChatSection();
        const ragPanel = document.getElementById("ragPanel");
        const toggleRagBtn = document.getElementById("toggleRagBtn");
        if (ragPanel) {
            toggleDrawer(ragPanel, toggleRagBtn);
            fetchRagDocuments();
        }
    };

    window.toggleChatMode = function() {
        const modeLabel = document.getElementById("modeLabel");
        const modeIcon = document.getElementById("modeIcon");
        const modeToggleChip = document.getElementById("modeToggleChip");

        if (currentChatMode === "full") {
            currentChatMode = "memory_only";
            if (modeLabel) modeLabel.innerText = "Mode: Pure Memory";
            if (modeIcon) {
                modeIcon.className = "fa-solid fa-brain";
                modeIcon.style.color = "#3b82f6";
            }
            if (modeToggleChip) {
                modeToggleChip.className = "mode-toggle-chip mode-pure-memory";
            }
            setMascot("thinking", "Pure Memory Mode Active (RAG DB Bypassed)");
        } else if (currentChatMode === "memory_only") {
            currentChatMode = "rag_only";
            if (modeLabel) modeLabel.innerText = "Mode: RAG Knowledge";
            if (modeIcon) {
                modeIcon.className = "fa-solid fa-file-contract";
                modeIcon.style.color = "#10b981";
            }
            if (modeToggleChip) {
                modeToggleChip.className = "mode-toggle-chip mode-rag-only";
            }
            setMascot("thinking", "RAG Knowledge Base Active (User Memory Bypassed)");
        } else {
            currentChatMode = "full";
            if (modeLabel) modeLabel.innerText = "Mode: Full Hybrid";
            if (modeIcon) {
                modeIcon.className = "fa-solid fa-brain";
                modeIcon.style.color = "#a855f7";
            }
            if (modeToggleChip) {
                modeToggleChip.className = "mode-toggle-chip";
            }
            setMascot("idle", "Full Hybrid Mode Active (Memory + RAG DB)");
        }
    };

    window.handleEmailSubmit = function(e) {
        e.preventDefault();
        const to = document.getElementById("seTo")?.value;
        const subj = document.getElementById("seSubj")?.value;
        const body = document.getElementById("seBody")?.value;

        window.closeServicesModal();
        window.openChatSection();

        const prompt = `Send an email to ${to} with subject "${subj}" and body: "${body}"`;
        sendMessage(prompt);
    };

    window.handleWhatsAppSubmit = function(e) {
        e.preventDefault();
        const num = document.getElementById("swNum")?.value;
        const msg = document.getElementById("swMsg")?.value;

        window.closeServicesModal();
        window.openChatSection();

        const prompt = `Send a WhatsApp message to ${num} saying "${msg}"`;
        sendMessage(prompt);
    };

    window.handleTelegramSubmit = function(e) {
        e.preventDefault();
        const chat = document.getElementById("stChat")?.value;
        const msg = document.getElementById("stMsg")?.value;

        window.closeServicesModal();
        window.openChatSection();

        const prompt = `Send a Telegram message to ${chat} saying "${msg}"`;
        sendMessage(prompt);
    };

    window.handleMovieSubmit = function(e) {
        e.preventDefault();
        const title = document.getElementById("smTitle")?.value;
        const city = document.getElementById("smCity")?.value;
        const seats = document.getElementById("smSeats")?.value;

        window.closeServicesModal();
        window.openChatSection();

        const prompt = `Search movie showtimes and reserve ${seats} tickets for "${title}" in ${city}`;
        sendMessage(prompt);
    };

    window.handleHotelSubmit = function(e) {
        e.preventDefault();
        const city = document.getElementById("shCity")?.value;
        const date = document.getElementById("shDate")?.value;
        const guests = document.getElementById("shGuests")?.value;
        const room = document.getElementById("shRoom")?.value;

        window.closeServicesModal();
        window.openChatSection();

        const prompt = `Search and reserve a ${room} hotel in ${city} for ${guests} guests check-in on ${date}`;
        sendMessage(prompt);
    };



    document.addEventListener("keydown", (e) => {
        if (e.key === "Escape") {
            const servicesModal = document.getElementById("servicesModal");
            const authModal = document.getElementById("authModal");
            if (servicesModal && !servicesModal.classList.contains("hidden")) {
                window.closeServicesModal();
            }
            if (authModal && !authModal.classList.contains("hidden")) {
                const closeAuthBtn = document.getElementById("closeAuthModal");
                if (closeAuthBtn) closeAuthBtn.click();
            }
        }
    });

});

