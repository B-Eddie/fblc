// Declare global variables at the top - DO NOT REDEFINE these in DOMContentLoaded
let map = null;
let providers = [];
let providerList = null;

// Add smooth scrolling for anchor links
document.querySelectorAll('a[href^="#"]').forEach((anchor) => {
  anchor.addEventListener("click", function (e) {
    e.preventDefault();
    document.querySelector(this.getAttribute("href")).scrollIntoView({
      behavior: "smooth",
    });
  });
});

// Only define these functions if they're NOT defined in the template
if (typeof fetchProviders !== "function") {
  function fetchProviders(specialty) {
    console.log("Using main.js fetchProviders with specialty:", specialty);

    let url = "/api/providers";
    if (specialty && specialty !== "All") {
      url += `?specialty=${encodeURIComponent(specialty)}`;
    }

    fetch(url)
      .then((response) => {
        if (!response.ok) {
          throw new Error(`HTTP error! Status: ${response.status}`);
        }
        return response.json();
      })
      .then((data) => {
        console.log(`Received ${data.length} providers`);
        providers = data;
        updateProviderList();
        if (map) updateMapMarkers();
      })
      .catch((error) => {
        console.error("Error fetching providers:", error);
        if (providerList) {
          providerList.innerHTML =
            '<p class="text-red-500">Error loading providers</p>';
        }
      });
  }
}

function updateProviderList() {
  providerList.innerHTML = "";
  if (providers.length === 0) {
    providerList.innerHTML = '<p class="text-gray-600">No providers found</p>';
    return;
  }
  providers.forEach((provider) => {
    const providerElement = document.createElement("div");
    providerElement.textContent = provider.name || "Unnamed Provider";
    providerElement.className = "provider-item";
    providerList.appendChild(providerElement);
  });
}

function updateMapMarkers() {
  console.log("Map markers update not implemented yet");
}

// Simplified DOMContentLoaded handler that won't conflict with the template
document.addEventListener("DOMContentLoaded", function () {
  console.log("main.js DOMContentLoaded event fired");

  // Let the specific page's JavaScript handle its own functionality
  // but initialize common UI elements here

  // Flash message auto-dismiss
  const alerts = document.querySelectorAll('[role="alert"]');
  alerts.forEach((alert) => {
    setTimeout(() => {
      alert.style.opacity = "0";
      setTimeout(() => alert.remove(), 300);
    }, 3000);
  });

  // Health chart initialization if present
  const healthChartCanvas = document.getElementById("healthChart");
  if (healthChartCanvas) {
    console.log("Initializing health chart");
    // Health chart initialization code...
  }
});
