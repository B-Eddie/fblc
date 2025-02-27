// Add smooth scrolling for anchor links
document.querySelectorAll('a[href^="#"]').forEach((anchor) => {
  anchor.addEventListener("click", function (e) {
    e.preventDefault();
    document.querySelector(this.getAttribute("href")).scrollIntoView({
      behavior: "smooth",
    });
  });
});

// Define helper functions
function fetchProviders(specialty) {
  let url = '/api/providers';
  if (specialty && specialty !== 'All') {
    url += `?specialty=${encodeURIComponent(specialty)}`;
  }
  fetch(url)
    .then(response => {
      if (!response.ok) {
        throw new Error(`HTTP error! Status: ${response.status}`);
      }
      return response.json();
    })
    .then(data => {
      providers = data;
      updateProviderList();
      if (map) updateMapMarkers();
    })
    .catch(error => {
      console.error('Error fetching providers:', error);
      providerList.innerHTML = '<p class="text-red-500">Error loading providers</p>';
    });
}

function updateProviderList() {
  providerList.innerHTML = '';
  if (providers.length === 0) {
    providerList.innerHTML = '<p class="text-gray-600">No providers found</p>';
    return;
  }
  providers.forEach(provider => {
    const providerElement = document.createElement('div');
    providerElement.textContent = provider.name || 'Unnamed Provider';
    providerElement.className = 'provider-item';
    providerList.appendChild(providerElement);
  });
}

function updateMapMarkers() {
  console.log('Map markers update not implemented yet');
}

// Main DOMContentLoaded event listener
document.addEventListener("DOMContentLoaded", function () {
  // DOM element references
  const providerList = document.getElementById("providerList");
  const filterButtons = document.querySelectorAll('[id^="filter"]');
  const sortDistance = document.getElementById("sortDistance");
  const modal = document.getElementById("bookingModal");
  const closeModal = document.getElementById("closeModal");
  const bookingForm = document.getElementById("bookingForm");
  let map = null;

  // HERE Maps platform initialization
  const platform = new H.service.Platform({
    apikey: "lUFTE1skWuIcrj_s0wCZbbM2KWcgT2JnJcKGWHFi4WA",
  });

  // Global variables
  let providers = [];
  let userLocation = { lat: 37.7749, lng: -122.4194 };

  // Set up filter button event listeners
  filterButtons.forEach((button) => {
    button.addEventListener("click", () => {
      const specialty = button.id.replace("filter", "");
      fetchProviders(specialty === "All" ? null : specialty);

      // Set all buttons to inactive state
      filterButtons.forEach((btn) => {
        btn.classList.remove("text-black", "bg-orange-500", "hover:bg-orange-600");
        btn.classList.add("text-orange-800", "bg-orange-100", "hover:bg-orange-200");
      });

      // Set the clicked button to active state
      button.classList.remove("text-orange-800", "bg-orange-100", "hover:bg-orange-200");
      button.classList.add("text-black", "bg-orange-500", "hover:bg-orange-600");
    });
  });

  // Flash message auto-dismiss
  const alerts = document.querySelectorAll('[role="alert"]');
  alerts.forEach((alert) => {
    setTimeout(() => {
      alert.style.opacity = "0";
      setTimeout(() => alert.remove(), 300);
    }, 3000);
  });

  // Health chart initialization
  const healthChartCanvas = document.getElementById('healthChart');
  if (healthChartCanvas) {
    fetch(`/api/health_data?days=7`)
      .then((response) => response.json())
      .then((data) => {
        if (data.length === 0) {
          healthChartCanvas.parentElement.innerHTML = 
            '<p class="text-gray-600">No health data available for this period</p>';
          return;
        }

        new Chart(healthChartCanvas.getContext('2d'), {
          type: 'line',
          data: {
            labels: data.map(item => item.date),
            datasets: [
              {
                label: 'Steps',
                data: data.map(item => item.steps),
                borderColor: '#FF6384',
                backgroundColor: 'rgba(255, 99, 132, 0.2)',
                tension: 0.4,
                yAxisID: 'y'
              },
              {
                label: 'Calories',
                data: data.map(item => item.calories),
                borderColor: '#36A2EB',
                backgroundColor: 'rgba(54, 162, 235, 0.2)',
                tension: 0.4,
                yAxisID: 'y1'
              },
              {
                label: 'Sleep Hours',
                data: data.map(item => item.sleep_hours),
                borderColor: '#4BC0C0',
                backgroundColor: 'rgba(75, 192, 192, 0.2)',
                tension: 0.4,
                yAxisID: 'y2'
              }
            ]
          },
          options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
              y: {
                type: 'linear',
                display: true,
                position: 'left',
                title: { text: 'Steps', display: true }
              },
              y1: {
                type: 'linear',
                display: true,
                position: 'right',
                title: { text: 'Calories', display: true },
                grid: { drawOnChartArea: false }
              },
              y2: {
                type: 'linear',
                display: false,
                title: { text: 'Sleep Hours', display: true }
              }
            },
            plugins: {
              tooltip: {
                mode: 'index',
                intersect: false
              },
              legend: {
                position: 'top'
              }
            }
          }
        });
      })
      .catch(error => {
        console.error('Error loading health data:', error);
        healthChartCanvas.parentElement.innerHTML = 
          '<p class="text-red-500">Error loading health data</p>';
      });
  }
});