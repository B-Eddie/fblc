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

