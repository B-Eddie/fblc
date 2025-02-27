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

  document.addEventListener("DOMContentLoaded", () => {
    const healthChartCanvas = document.getElementById('healthChart')
    if (healthChartCanvas) {
      fetch(`/api/health_data?days=7`)
        .then((response) => response.json())
        .then((data) => {
          if (data.length === 0) {
            healthChartCanvas.parentElement.innerHTML = 
              '<p class="text-gray-600">No health data available for this period</p>'
            return
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
          })
        })
        .catch(error => {
          console.error('Error loading health data:', error)
          healthChartCanvas.parentElement.innerHTML = 
            '<p class="text-red-500">Error loading health data</p>'
        })
    }
  })
})
