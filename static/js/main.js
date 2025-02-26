// Add smooth scrolling for anchor links
document.querySelectorAll('a[href^="#"]').forEach((anchor) => {
  anchor.addEventListener("click", function (e) {
    e.preventDefault()
    document.querySelector(this.getAttribute("href")).scrollIntoView({
      behavior: "smooth",
    })
  })
})

// Flash message auto-dismiss
document.addEventListener("DOMContentLoaded", () => {
  const alerts = document.querySelectorAll('[role="alert"]')
  alerts.forEach((alert) => {
    setTimeout(() => {
      alert.style.opacity = "0"
      setTimeout(() => alert.remove(), 300)
    }, 3000)
  })
})

document.querySelectorAll('a[href^="#"]').forEach((anchor) => {
  anchor.addEventListener("click", function (e) {
    e.preventDefault()
    document.querySelector(this.getAttribute("href")).scrollIntoView({
      behavior: "smooth",
    })
  })
})

// Flash message auto-dismiss
document.addEventListener("DOMContentLoaded", () => {
  const alerts = document.querySelectorAll('[role="alert"]')
  alerts.forEach((alert) => {
    setTimeout(() => {
      alert.style.opacity = "0"
      setTimeout(() => alert.remove(), 300)
    }, 3000)
  })

  // Health Chart Initialization - only runs on health tracker page
  const healthChart = document.getElementById('healthChart')
  if (healthChart) {
    fetch("/api/health_data")
      .then((response) => response.json())
      .then((data) => {
        const ctx = healthChart.getContext("2d")
        new Chart(ctx, {
          type: "line",
          data: {
            labels: data.map((item) => item.date),
            datasets: [
              {
                label: "Steps",
                data: data.map((item) => item.steps),
                borderColor: "rgb(255, 99, 132)",
                tension: 0.1,
              },
              {
                label: "Calories",
                data: data.map((item) => item.calories),
                borderColor: "rgb(54, 162, 235)",
                tension: 0.1,
              },
              {
                label: "Sleep Hours",
                data: data.map((item) => item.sleep_hours),
                borderColor: "rgb(75, 192, 192)",
                tension: 0.1,
              },
            ],
          },
          options: {
            responsive: true,
            scales: {
              y: {
                beginAtZero: true,
              },
            },
          },
        })
      })
      .catch((error) => {
        console.error('Error loading health data:', error)
      })
  }
})
