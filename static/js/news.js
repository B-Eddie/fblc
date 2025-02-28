// Replace 'your_api_key_here' with your actual NewsAPI key from https://newsapi.org/
const API_KEY = 'df67b3ee33de4753a1b3ee18fe45f2b7';
const NEWS_API_URL = `https://newsapi.org/v2/top-headlines?category=health&apiKey=${API_KEY}`;

// Function to fetch news articles
async function fetchNews() {
  try {
    const response = await fetch(NEWS_API_URL);
    if (!response.ok) throw new Error('Network response was not ok');
    const data = await response.json();
    return data.articles.slice(0, 2); // Limit to 2 articles to match HTML
  } catch (error) {
    console.error('Error fetching news:', error);
    return [];
  }
}

// Function to render news articles
function renderNews(articles) {
  const newsSection = document.querySelector('.health-tip-card').parentElement;
  if (!newsSection) return;

  // Clear existing health tip cards
  newsSection.querySelectorAll('.health-tip-card').forEach(card => card.remove());

  // Render new articles
  articles.forEach(article => {
    const articleElement = document.createElement('div');
    articleElement.classList.add('health-tip-card', 'p-4', 'bg-white', 'rounded-lg', 'shadow', 'cursor-pointer');
    articleElement.innerHTML = `
      <h3 class="font-semibold text-gray-800 mb-2">${article.title}</h3>
      <p class="tip-content text-sm text-gray-600 line-clamp-3">${article.description || 'No description available.'}</p>
    `;
    articleElement.addEventListener('click', () => window.open(article.url, '_blank'));
    newsSection.insertBefore(articleElement, newsSection.querySelector('a')); // Insert before "View More Articles" link
  });
}

// Sample recent health activities (unchanged from HTML)
const recentActivities = [
  { title: 'Annual Physical Checkup', date: '2024-05-15', status: 'Completed' },
  { title: 'Blood Work Results', date: '2024-05-10', status: 'Reviewed' },
  { title: '10,000 Steps Goal', date: '2024-05-18', status: 'Achieved' }
];

// Function to render recent health activities
function renderActivities() {
  const activityList = document.querySelector('.recent-activity-item').parentElement;
  if (!activityList) return;

  // Clear existing activities
  activityList.innerHTML = '';

  // Render activities
  recentActivities.forEach(activity => {
    const activityElement = document.createElement('li');
    activityElement.classList.add('recent-activity-item', 'p-3', 'bg-white', 'rounded-lg', 'shadow');
    activityElement.innerHTML = `
      <div class="flex justify-between items-start">
        <div>
          <p class="text-sm font-medium text-gray-800">${activity.title}</p>
          <p class="text-xs text-gray-500 activity-time" data-time="${activity.date}">${new Date(activity.date).toLocaleDateString()}</p>
        </div>
        <span class="px-2 py-1 bg-orange-100 text-orange-700 rounded-full text-xs">${activity.status}</span>
      </div>
    `;
    activityList.appendChild(activityElement);
  });
}

// Initialize the page
async function init() {
  const articles = await fetchNews();
  renderNews(articles);
  renderActivities();
}

// Call init function when the page loads
document.addEventListener('DOMContentLoaded', init);