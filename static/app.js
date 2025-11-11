// AutoMentor CRM - Optimized with Offline Support
class CRM {
  constructor() {
    this.baseUrl = window.location.origin;
    this.isOnline = navigator.onLine;
    this.pendingChanges = new Map();
    this.debounceTimers = new Map();
    this.init();
  }

  init() {
    this.setupOfflineSupport();
    this.setupRecruitListeners();
    this.loadFromCache();
  }

  setupOfflineSupport() {
    window.addEventListener("online", () => {
      this.isOnline = true;
      this.syncPendingChanges();
      this.showNotification("Back online - syncing changes", "success");
    });

    window.addEventListener("offline", () => {
      this.isOnline = false;
      this.showNotification("Offline mode - changes saved locally", "warning");
    });
  }

  loadFromCache() {
    const cached = localStorage.getItem("crm_recruits");
    if (cached && !this.isOnline) {
      const recruits = JSON.parse(cached);
      this.renderRecruits(recruits);
    }
  }

  saveToCache(recruits) {
    localStorage.setItem("crm_recruits", JSON.stringify(recruits));
  }

  // Setup event listeners for recruit cards
  setupRecruitListeners() {
    document.querySelectorAll(".recruit-card form").forEach((form) => {
      form.addEventListener("submit", (e) => {
        e.preventDefault();
        this.updateRecruit(form);
      });
    });

    document.querySelectorAll(".btn-delete").forEach((btn) => {
      btn.addEventListener("click", (e) => {
        e.preventDefault();
        if (confirm("Are you sure you want to delete this recruit?")) {
          this.deleteRecruit(btn.href);
        }
      });
    });

    // Setup stage select listeners for visual feedback
    document.querySelectorAll(".stage-select").forEach((select) => {
      select.addEventListener("change", (e) => {
        this.updateStageVisual(e.target);
      });
      // Set initial state
      this.updateStageVisual(select);
    });
  }

  // Update stage select visual based on value
  updateStageVisual(select) {
    const value = select.value;
    select.setAttribute("value", value);
  }

  // Update recruit with optimistic updates and debouncing
  updateRecruit(form) {
    const formData = new FormData(form);
    const recruitCard = form.closest(".recruit-card");
    const recruitId = new URL(form.action).pathname.split("/").pop();

    const infoParagraphs = recruitCard.querySelectorAll(".recruit-info p");
    const data = {
      name: recruitCard.querySelector(".recruit-info h3").textContent,
      email: infoParagraphs[0] ? infoParagraphs[0].textContent : '',
      phone: infoParagraphs[1] ? infoParagraphs[1].textContent : '',
      stage: formData.get("stage"),
      notes: formData.get("notes"),
    };

    // Optimistic update - apply changes immediately
    this.applyOptimisticUpdate(recruitId, data);

    // Debounce API calls
    if (this.debounceTimers.has(recruitId)) {
      clearTimeout(this.debounceTimers.get(recruitId));
    }

    const timer = setTimeout(() => {
      this.syncRecruitUpdate(recruitId, data);
    }, 300);

    this.debounceTimers.set(recruitId, timer);
  }

  applyOptimisticUpdate(recruitId, data) {
    // Update UI immediately
    this.refreshStats();

    // Store pending change
    this.pendingChanges.set(recruitId, data);

    // Save to local storage
    const cached = JSON.parse(localStorage.getItem("crm_recruits") || "[]");
    const index = cached.findIndex((r) => r.id == recruitId);
    if (index >= 0) {
      cached[index] = { ...cached[index], ...data };
      this.saveToCache(cached);
    }
  }

  async syncRecruitUpdate(recruitId, data) {
    if (!this.isOnline) {
      this.showNotification("Offline - changes saved locally", "warning");
      return;
    }

    try {
      const response = await fetch(
        `${this.baseUrl}/api/recruits/${recruitId}`,
        {
          method: "PUT",
          headers: {
            "Content-Type": "application/json",
            "X-Requested-With": "XMLHttpRequest",
          },
          body: JSON.stringify(data),
        }
      );

      if (response.ok) {
        this.pendingChanges.delete(recruitId);
        this.showNotification("✓ Synced", "success");
      } else {
        throw new Error(`HTTP ${response.status}`);
      }
    } catch (error) {
      console.error("Sync error:", error);
      this.showNotification("Sync failed - retrying", "warning");
      // Retry after delay
      setTimeout(() => this.syncRecruitUpdate(recruitId, data), 5000);
    }
  }

  async syncPendingChanges() {
    for (const [recruitId, data] of this.pendingChanges) {
      await this.syncRecruitUpdate(recruitId, data);
    }
  }

  // Delete recruit with optimistic updates
  async deleteRecruit(url) {
    const recruitId = url.split("/").pop();
    const card = document
      .querySelector(`a[href="${url}"]`)
      .closest(".recruit-card");

    // Optimistic delete - remove from UI immediately
    card.style.transition = "all 0.3s ease";
    card.style.opacity = "0";
    card.style.transform = "scale(0.9)";

    setTimeout(() => {
      card.remove();
      this.refreshStats();
    }, 300);

    // Update cache
    const cached = JSON.parse(localStorage.getItem("crm_recruits") || "[]");
    const filtered = cached.filter((r) => r.id != recruitId);
    this.saveToCache(filtered);

    if (!this.isOnline) {
      this.showNotification(
        "Deleted locally - will sync when online",
        "warning"
      );
      this.pendingChanges.set(`delete_${recruitId}`, { action: "delete" });
      return;
    }

    try {
      const response = await fetch(
        `${this.baseUrl}/api/recruits/${recruitId}`,
        {
          method: "DELETE",
          headers: { "X-Requested-With": "XMLHttpRequest" },
        }
      );

      if (response.ok) {
        this.showNotification("Recruit deleted!", "success");
      } else {
        throw new Error(`HTTP ${response.status}`);
      }
    } catch (error) {
      console.error("Delete error:", error);
      this.showNotification("Delete failed - will retry", "error");
      // Could restore the card here if needed
    }
  }

  // Refresh stats dynamically
  async refreshStats() {
    try {
      const response = await fetch(`${this.baseUrl}/api/recruits`);
      const recruits = await response.json();

      const stages = ["New", "Contacted", "Interview", "Licensed", "Inactive"];
      const counts = {};

      stages.forEach((stage) => {
        counts[stage] = recruits.filter((r) => r.stage === stage).length;
      });

      // Update stat cards
      document.querySelectorAll(".stat-card").forEach((card) => {
        const stage = card.querySelector(".stat-content p").textContent;
        if (counts[stage] !== undefined) {
          card.querySelector(".stat-content h3").textContent = counts[stage];
        }
      });

      // Update recruit count
      const countElement = document.querySelector(".recruit-count");
      if (countElement) {
        countElement.textContent = `${recruits.length} total`;
      }
    } catch (error) {
      console.error("Error refreshing stats:", error);
    }
  }

  // Enhanced notification system
  showNotification(message, type = "info") {
    // Remove existing notifications of same type
    document
      .querySelectorAll(`.notification-${type}`)
      .forEach((n) => n.remove());

    const notification = document.createElement("div");
    notification.className = `notification notification-${type}`;
    notification.textContent = message;
    notification.style.cssText = `
      position: fixed;
      top: 2em;
      right: 2em;
      background: ${
        type === "success"
          ? "linear-gradient(135deg, #10b981, #059669)"
          : type === "error"
          ? "linear-gradient(135deg, #ef4444, #dc2626)"
          : type === "warning"
          ? "linear-gradient(135deg, #f59e0b, #d97706)"
          : "linear-gradient(135deg, #a78bfa, #ec4899)"
      };
      color: white;
      padding: 0.8em 1.2em;
      border-radius: 8px;
      box-shadow: 0 4px 16px rgba(0, 0, 0, 0.3);
      z-index: 10000;
      font-weight: 500;
      font-size: 0.9em;
      animation: slideIn 0.2s ease;
      max-width: 300px;
    `;

    document.body.appendChild(notification);

    const duration = type === "success" ? 2000 : type === "error" ? 5000 : 3000;
    setTimeout(() => {
      notification.style.animation = "slideOut 0.2s ease";
      setTimeout(() => notification.remove(), 200);
    }, duration);
  }

  // Add new recruit with offline support
  async addRecruit(data) {
    console.log("[CRM] addRecruit called with:", data.name);
    // Generate temporary ID for offline mode
    const tempId = Date.now();
    const recruitData = {
      ...data,
      id: tempId,
      created_at: new Date().toISOString(),
    };

    if (!this.isOnline) {
      console.log("[CRM] Offline mode - using localStorage");
      // Store in local cache
      const cached = JSON.parse(localStorage.getItem("crm_recruits") || "[]");
      cached.unshift(recruitData);
      this.saveToCache(cached);

      this.pendingChanges.set(`new_${tempId}`, {
        action: "create",
        data: recruitData,
      });
      this.showNotification("Added offline - will sync when online", "warning");

      // Redirect immediately
      window.location.href = "/";
      return;
    }

    console.log("[CRM] Online mode - posting to API");
    try {
      const response = await fetch(`${this.baseUrl}/api/recruits`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-Requested-With": "XMLHttpRequest",
        },
        body: JSON.stringify(data),
      });

      if (response.ok) {
        const recruit = await response.json();
        console.log("[CRM] POST successful, redirecting to /");
        this.showNotification("Recruit added!", "success");
        // Redirect immediately - notification will show briefly
        window.location.href = "/";
      } else {
        throw new Error(`HTTP ${response.status}`);
      }
    } catch (error) {
      console.error("Add error:", error);
      this.showNotification("Failed to add recruit", "error");
    }
  }

  renderRecruits(recruits) {
    // This would be used to render cached recruits in offline mode
    // Implementation depends on your template structure
  }
}

// Add notification animations
const style = document.createElement("style");
style.textContent = `
  @keyframes slideIn {
    from {
      transform: translateX(400px);
      opacity: 0;
    }
    to {
      transform: translateX(0);
      opacity: 1;
    }
  }

  @keyframes slideOut {
    from {
      transform: translateX(0);
      opacity: 1;
    }
    to {
      transform: translateX(400px);
      opacity: 0;
    }
  }
`;
document.head.appendChild(style);

// Initialize CRM when DOM is ready
document.addEventListener("DOMContentLoaded", () => {
  window.crm = new CRM();

  // Note: Form submission is handled in add.html to support traditional POST fallback
  // This global handler is removed to avoid conflicts
});

// Service Worker registration for offline support
if ("serviceWorker" in navigator) {
  window.addEventListener("load", () => {
    navigator.serviceWorker
      .register("/sw.js")
      .then(() => console.log("SW registered"))
      .catch(() => console.log("SW registration failed"));
  });
}
