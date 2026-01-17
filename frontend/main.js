const API_URL = "http://127.0.0.1:8000/api/chat";
const AUTH_URL = "http://127.0.0.1:8000/auth";
const HISTORY_URL = "http://127.0.0.1:8000/history";

// --- DOM Elements ---
const landingView = document.getElementById("landing-view");
const authView = document.getElementById("auth-view");
const appView = document.getElementById("app-view");
const startBtn = document.getElementById("start-btn");

const chatForm = document.getElementById("chat-form");
const chatInput = document.getElementById("chat-input");
const chatMessages = document.getElementById("chat-messages");
const typingIndicator = document.getElementById("typing-indicator");

// Pack Sections
const packSummary = document.getElementById("pack-summary");
const packBrand = document.getElementById("pack-brand");
const brandColorsRow = document.getElementById("brand-colors");
// const packMarket = document.getElementById("pack-market"); // Removed
// const marketList = document.getElementById("market-list"); // Removed
const finList = document.getElementById("fin-list");
const packPitch = document.getElementById("pack-pitch");
const pitchSlidesList = document.getElementById("pitch-slides");
const elevatorText = document.getElementById("elevator-text");

// Brand Logo
const brandLogoImg = document.getElementById("brand-logo");
const logoPlaceholder = document.getElementById("logo-placeholder");
const logoDownloadBtn = document.getElementById("logo-download-btn");

// Nav
const voiceToggleBtn = document.getElementById("voice-toggle");
const historyToggleBtn = document.getElementById("history-toggle");
const logoutBtn = document.getElementById("logout-btn");
const userDisplay = document.getElementById("user-display");
// Mic
const micBtn = document.getElementById("mic-btn");

// Auth Form Elements
const authForm = document.getElementById("auth-form");
const authEmailInput = document.getElementById("auth-email");
const authPasswordInput = document.getElementById("auth-password");
const authSubmitBtn = document.getElementById("auth-submit-btn");
const authSwitchBtn = document.getElementById("auth-switch-btn");
const authToggleText = document.getElementById("auth-toggle-text");
const authTitle = document.getElementById("auth-title");
const authSubtitle = document.getElementById("auth-subtitle");

// Extended Fields
const signupFieldsDiv = document.getElementById("signup-fields");
const confirmPassField = document.getElementById("confirm-password-field");
// authName removed, using direct access in submission
const authDob = document.getElementById("auth-dob");
const authPhone = document.getElementById("auth-phone");
const authConfirmPass = document.getElementById("auth-confirm-password");

// History Sidebar
const historySidebar = document.getElementById("history-sidebar");
const historyCloseBtn = document.getElementById("history-close-btn");
const historyList = document.getElementById("history-list");

// Chart
let marketChartInstance = null;

// --- State ---
let voiceEnabled = true;
let isSignUpMode = false;
let authToken = localStorage.getItem("vm_token");
let userEmail = localStorage.getItem("vm_email");
let userName = localStorage.getItem("vm_name") || "";

// --- Init ---
init();

function init() {
  // If logged in, go straight to App
  if (authToken) {
    landingView.classList.add("hidden");
    authView.classList.add("hidden");
    appView.classList.remove("hidden");
    setupUserUI();
  } else {
    // Show Landing Page first
    landingView.classList.remove("hidden");
    authView.classList.add("hidden");
    appView.classList.add("hidden");
  }
}

// Start Button -> Show Auth (Login Mode default)
if (startBtn) {
  startBtn.addEventListener("click", () => {
    console.log("Start Button Clicked");
    if (landingView) landingView.classList.add("hidden");
    if (authView) authView.classList.remove("hidden");
    console.log("Switched to Auth View");
  });
} else {
  console.error("Start Button NOT found!");
}

function setupUserUI() {
  userDisplay.textContent = userName ? `Welcome, ${userName}` : userEmail;
  userDisplay.classList.remove("hidden");
  logoutBtn.classList.remove("hidden");
  historyToggleBtn.classList.remove("hidden");

  // Auto load history
  fetchHistory();
}

// --- Auth Logic ---

authSwitchBtn.addEventListener("click", (e) => {
  e.preventDefault();
  toggleAuthMode();
});

function toggleAuthMode() {
  isSignUpMode = !isSignUpMode;

  if (isSignUpMode) {
    authTitle.textContent = "Create Account";
    authSubtitle.textContent = "Join VentureMind today";
    authSubmitBtn.textContent = "Sign Up";
    authToggleText.innerHTML = 'Already have an account? <a href="#" id="auth-switch-back">Login</a>';

    signupFieldsDiv.classList.remove("hidden");
    confirmPassField.classList.remove("hidden");
    document.getElementById("privacy-policy-div").classList.remove("hidden");

    document.getElementById("auth-switch-back").addEventListener("click", (e) => {
      e.preventDefault();
      toggleAuthMode();
    });
  } else {
    authTitle.textContent = "Welcome Back";
    authSubtitle.textContent = "Login to access your workspace";
    authSubmitBtn.textContent = "Login";
    authToggleText.innerHTML = 'New here? <a href="#" id="auth-switch-btn">Sign Up</a>';

    signupFieldsDiv.classList.add("hidden");
    confirmPassField.classList.add("hidden");
    document.getElementById("privacy-policy-div").classList.add("hidden");

    // Re-bind original switch button since innerHTML wiped it
    document.getElementById("auth-switch-btn").addEventListener("click", (e) => {
      e.preventDefault();
      toggleAuthMode();
    });
  }
}

// Global scope for the onclick handler in HTML
window.togglePassword = function (inputId, el) {
  const input = document.getElementById(inputId);
  if (input.type === "password") {
    input.type = "text";
    el.textContent = "Hide";
  } else {
    input.type = "password";
    el.textContent = "Show";
  }
};

// --- Toast Logic ---
function showToast(message, type = "info") {
  let container = document.querySelector(".toast-container");
  if (!container) {
    container = document.createElement("div");
    container.className = "toast-container";
    document.body.appendChild(container);
  }

  const toast = document.createElement("div");
  toast.className = `toast ${type}`;
  toast.innerHTML = type === "success" ? `✓ ${message}` : `⚠ ${message}`;

  container.appendChild(toast);

  // Remove after 3s
  setTimeout(() => {
    toast.style.animation = "fadeOut 0.4s forwards";
    setTimeout(() => toast.remove(), 400);
  }, 3000);
}

authForm.addEventListener("submit", async (e) => {
  e.preventDefault();

  const email = authEmailInput.value;
  const password = authPasswordInput.value;
  const endpoint = isSignUpMode ? "/signup" : "/login";

  let bodyData = { email, password };

  // Validation & Extra Fields for Signup
  if (isSignUpMode) {
    const confirm = authConfirmPass.value;
    if (password !== confirm) {
      showToast("Passwords do not match!", "error");
      return;
    }

    const firstName = document.getElementById("auth-first-name").value;
    const lastName = document.getElementById("auth-last-name").value;

    if (!firstName || !lastName) {
      showToast("Please enter your full name", "error");
      return;
    }

    bodyData.full_name = `${firstName} ${lastName}`;
    bodyData.dob = authDob.value;
    bodyData.phone = authPhone.value;
  }

  // Optimize UI feedback
  const originalBtnText = authSubmitBtn.textContent;
  authSubmitBtn.textContent = "Processing...";
  authSubmitBtn.disabled = true;

  try {
    const res = await fetch(AUTH_URL + endpoint, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(bodyData),
    });

    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: "Unknown error" }));
      console.error("Auth Fail:", res.status, err);
      showToast(err.detail || "Authentication failed", "error");
      return;
    }

    const data = await res.json();

    if (isSignUpMode) {
      // Signup Successful -> Show Toast -> Wait -> Switch to Login
      showToast("Signup successful! Redirecting to login...", "success");

      setTimeout(() => {
        toggleAuthMode(); // Switch back to login
        authEmailInput.value = email; // Pre-fill email
        authPasswordInput.value = ""; // Clear password for security
      }, 1500); // 1.5s delay for user to read toast

    } else {
      // Login Successful
      authToken = data.access_token;
      userName = data.user_name;

      localStorage.setItem("vm_token", authToken);
      localStorage.setItem("vm_email", email);
      localStorage.setItem("vm_name", userName);

      showToast(`Welcome back, ${userName || "Founder"}!`, "success");

      // Smooth transition
      setTimeout(() => {
        authView.classList.add("hidden");
        appView.classList.remove("hidden");
        setupUserUI();
      }, 500);
    }

  } catch (err) {
    console.error("Network/Fetch Error:", err);
    showToast("Network error. Please try again.", "error");
  } finally {
    authSubmitBtn.textContent = originalBtnText;
    authSubmitBtn.disabled = false;
  }
});

logoutBtn.addEventListener("click", () => {
  localStorage.removeItem("vm_token");
  localStorage.removeItem("vm_email");
  localStorage.removeItem("vm_name");
  authToken = null;
  userEmail = null;
  userName = null;
  location.reload();
});


// --- History Logic ---

historyToggleBtn.addEventListener("click", () => {
  historySidebar.classList.add("open");
  historySidebar.classList.remove("hidden");
  fetchHistory();
});

if (historyCloseBtn) {
  historyCloseBtn.addEventListener("click", () => {
    historySidebar.classList.remove("open");
    // setTimeout(() => historySidebar.classList.add("hidden"), 300);
  });
}

// historyCloseBtn removed from markup, no listener needed

async function fetchHistory() {
  if (!authToken) return;
  try {
    const res = await fetch(HISTORY_URL + "/", {
      headers: { "Authorization": `Bearer ${authToken}` }
    });
    if (!res.ok) return;
    const items = await res.json();
    renderHistoryList(items);
  } catch (err) {
    console.error(err);
  }
}

function renderHistoryList(items) {
  historyList.innerHTML = "";
  items.forEach(item => {
    const li = document.createElement("li");
    li.classList.add("history-item");
    const date = new Date(item.created_at).toLocaleDateString();
    li.innerHTML = `
      <div class="summary">${item.idea}</div>
      <div class="date">${date}</div>
    `;
    li.addEventListener("click", () => loadHistoryItem(item.id));
    historyList.appendChild(li);
  });
}

async function loadHistoryItem(id) {
  try {
    const res = await fetch(`${HISTORY_URL}/${id}`, {
      headers: { "Authorization": `Bearer ${authToken}` }
    });
    if (!res.ok) return;
    const data = await res.json();
    updateStartupPack({
      startup_pack: data.full_json,
      domains: [], competitor_matrix: []
    });
    appendMessage({ text: `(History) ${data.idea}`, from: "user" });
    historySidebar.classList.remove("open");
  } catch (err) {
    console.error(err);
  }
}


// --- Main Chat Logic ---

// Loading interval
let typingInterval;
const loadingMessages = [
  "Analyzing your startup idea...",
  "Identifyng market opportunities...",
  "Drafting business model...",
  "Calculating financial projections...",
  "Designing brand identity...",
  "Compiling final strategy pack..."
];

function setTyping(isTyping, dynamic = false) {
  typingIndicator.classList.toggle("hidden", !isTyping);

  if (typingInterval) clearInterval(typingInterval);

  // Ensure structured HTML inside typing indicator
  if (!typingIndicator.querySelector("span")) {
    typingIndicator.innerHTML = '<div class="dots"><div class="dot"></div><div class="dot"></div><div class="dot"></div></div> <span class="typing-text">Thinking...</span>';
  }

  const textSpan = typingIndicator.querySelector(".typing-text");

  if (isTyping && dynamic) {
    let index = 0;
    textSpan.textContent = loadingMessages[0];
    typingInterval = setInterval(() => {
      index = (index + 1) % loadingMessages.length;
      textSpan.textContent = loadingMessages[index];
    }, 2500);
  } else {
    if (textSpan) textSpan.textContent = "Thinking...";
  }
}

chatForm.addEventListener("submit", async (e) => {
  e.preventDefault();
  let text = chatInput.value.trim();
  if (!text) return;

  appendMessage({ text, from: "user" });
  chatInput.value = "";

  const headers = { "Content-Type": "application/json" };
  if (authToken) headers["Authorization"] = `Bearer ${authToken}`;

  setTyping(true, true);

  try {
    const res = await fetch(API_URL, {
      method: "POST",
      headers: headers,
      body: JSON.stringify({ message: text }),
    });

    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      appendMessage({ text: err.detail || "Error", from: "ai" });
      return;
    }

    const data = await res.json();
    const html = renderMarkdown(data.reply_markdown || "");
    appendMessage({ html, from: "ai" });
    updateStartupPack(data);

    if (voiceEnabled) {
      const plain = data.reply_markdown.replace(/[#*]/g, "");
      speakText(plain);
    }

  } catch (err) {
    console.error(err);
    appendMessage({ text: "Connection error.", from: "ai" });
  } finally {
    setTyping(false);
  }
});


// --- Reusing Helper Functions (Markdown, UI Updates) ---

function renderMarkdown(md) {
  if (!md) return "";
  let text = md.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
  const lines = text.split("\n");
  let html = "";
  let inList = false;

  function closeList() { if (inList) { html += "</ul>"; inList = false; } }

  for (let raw of lines) {
    const line = raw.trim();
    if (!line) { closeList(); html += "<br/>"; continue; }

    if (line.startsWith("### ")) {
      closeList(); html += `<h3>${line.slice(4)}</h3>`;
    } else if (line.startsWith("## ")) {
      closeList(); html += `<h2>${line.slice(3)}</h2>`;
    } else if (line.startsWith("- ")) {
      if (!inList) { html += "<ul>"; inList = true; }
      html += `<li>${line.slice(2)}</li>`;
    } else {
      closeList();
      const boldProcessed = line.replace(/\*\*(.+?)\*\*/g, "<strong>$1</strong>");
      html += `<p>${boldProcessed}</p>`;
    }
  }
  closeList();
  return html;
}

function appendMessage({ text = "", html = "", from = "ai" }) {
  const bubble = document.createElement("div");
  bubble.classList.add("msg");
  if (from === "user") {
    bubble.classList.add("msg-user");
  } else {
    bubble.classList.add("msg-ai", "glass-bubble");
  }

  if (from === "ai") {
    const label = document.createElement("div");
    label.classList.add("msg-label");
    label.textContent = "VentureMind.AI";
    bubble.appendChild(label);
  }

  const body = document.createElement("div");
  if (html) body.innerHTML = html;
  else body.textContent = text;

  bubble.appendChild(body);
  chatMessages.appendChild(bubble);
  chatMessages.scrollTop = chatMessages.scrollHeight;
}

function updateStartupPack(data) {
  const pack = data.startup_pack;
  if (!pack) return;

  if (pack.startup_summary) {
    packSummary.innerHTML = `<h3>Summary</h3><p>${pack.startup_summary}</p>`;
  }

  /* Market Analysis Removed
  if (pack.market_analysis) {
     ...
  } */

  if (pack.brand) {
    packBrand.querySelector(".brand-block").innerHTML = `
      <p><strong>${pack.brand.name}</strong> (${pack.brand.alt_name})</p>
      <p>“${pack.brand.tagline}”</p>
      <p style="font-size:11px;color:#9ca3af">Tone: ${pack.brand.brand_tone}</p>
    `;

    brandColorsRow.innerHTML = "";
    (pack.brand.colors || []).forEach(hex => {
      const chip = document.createElement("div");
      chip.classList.add("color-chip");
      chip.style.background = hex;
      chip.textContent = hex;
      brandColorsRow.appendChild(chip);
    });

    if (pack.brand.logo_url) {
      brandLogoImg.src = pack.brand.logo_url;
      brandLogoImg.classList.remove("hidden");
      logoPlaceholder.classList.add("hidden");
      logoDownloadBtn.classList.remove("hidden");
    }
  }

  if (pack.financials) {
    const f = pack.financials;
    finList.innerHTML = `
       <li><strong>Total Cost:</strong> ${f.total_cost}</li>
       <li><strong>Revenue:</strong> ${f.projected_revenue}</li>
       <li><strong>ROI:</strong> ${f.roi}</li>
       <li><strong>Burn Rate:</strong> ${f.burn_rate}</li>
       <li><strong>Break-even:</strong> ${f.break_even_month}</li>
       <li><strong>Runway:</strong> ${f.runway}</li>
    `;
  }

  if (pack.pitch) {
    elevatorText.textContent = pack.pitch.elevator_pitch;
    pitchSlidesList.innerHTML = "";
    const s = pack.pitch.slides;
    const items = [
      ["Problem", s.problem],
      ["Solution", s.solution],
      ["Market", s.market],
      ["Model", s.model],
      ["Ask", s.brand_ask]
    ];
    items.forEach(([k, v]) => {
      const li = document.createElement("li");
      li.innerHTML = `<strong>${k}:</strong> ${v}`;
      pitchSlidesList.appendChild(li);
    });
  }
}

// --- Chart.js ---
function renderMarketChart({ tam, sam, som }) {
  const parseVal = (str) => {
    const match = str.match(/[\d,.]+/);
    if (match) return parseFloat(match[0].replace(/,/g, ''));
    return 1;
  };

  const ctx = document.getElementById('marketChart').getContext('2d');
  if (marketChartInstance) marketChartInstance.destroy();

  marketChartInstance = new Chart(ctx, {
    type: 'bar',
    data: {
      labels: ['TAM', 'SAM', 'SOM'],
      datasets: [{
        label: 'Market Size (Estimated)',
        data: [parseVal(tam), parseVal(sam), parseVal(som)],
        backgroundColor: ['rgba(250, 204, 21, 0.7)', 'rgba(34, 211, 238, 0.7)', 'rgba(244, 114, 182, 0.7)'],
        borderWidth: 0
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      scales: {
        y: { beginAtZero: true, grid: { color: 'rgba(255,255,255,0.1)' }, ticks: { color: '#9ca3af' } },
        x: { grid: { display: false }, ticks: { color: '#e5e7eb' } }
      },
      plugins: { legend: { display: false } }
    }
  });
}

// --- Voice ---
function speakText(text) {
  if (!voiceEnabled || !window.speechSynthesis) return;
  window.speechSynthesis.cancel();
  const u = new SpeechSynthesisUtterance(text);
  window.speechSynthesis.speak(u);
}
// --- Audio Input (Speech to Text) ---
const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
if (SpeechRecognition) {
  const recognition = new SpeechRecognition();
  recognition.continuous = false;
  recognition.lang = "en-US";
  recognition.interimResults = false;

  recognition.onstart = () => {
    micBtn.classList.add("recording"); // You can style this class in CSS
    chatInput.placeholder = "Listening...";
  };

  recognition.onend = () => {
    micBtn.classList.remove("recording");
    chatInput.placeholder = "Describe your startup idea…";
  };

  recognition.onresult = (event) => {
    const transcript = event.results[0][0].transcript;
    chatInput.value = transcript;
    // Optional: Focus input
    chatInput.focus();
  };

  recognition.onerror = (event) => {
    console.error("Speech Recognition Error", event.error);
    showToast("Microphone access denied or error.", "error");
  };

  if (micBtn) {
    micBtn.addEventListener("click", () => {
      recognition.start();
    });
  }
} else {
  if (micBtn) micBtn.style.display = "none"; // Hide if not supported
}


// --- Logo Download (Fixed) ---
if (logoDownloadBtn) {
  logoDownloadBtn.addEventListener("click", async () => {
    const src = brandLogoImg.src;
    if (!src) {
      showToast("No logo to download", "error");
      return;
    }

    try {
      logoDownloadBtn.textContent = "Downloading...";
      // Convert base64/url to Blob
      const response = await fetch(src);
      const blob = await response.blob();
      const blobUrl = URL.createObjectURL(blob);

      const link = document.createElement("a");
      link.href = blobUrl;
      link.download = `VentureMind_Logo_${Date.now()}.png`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      URL.revokeObjectURL(blobUrl);

      logoDownloadBtn.textContent = "⬇ Download Logo";
      showToast("Logo downloaded successfully!", "success");
    } catch (e) {
      console.error("Download failed:", e);
      showToast("Failed to download logo", "error");
      logoDownloadBtn.textContent = "⬇ Download Logo";
    }
  });
}

voiceToggleBtn.addEventListener("click", () => {
  voiceEnabled = !voiceEnabled;
  voiceToggleBtn.textContent = voiceEnabled ? "🔊 Voice: On" : "🔇 Voice: Off";
  if (!voiceEnabled) window.speechSynthesis.cancel();
});
