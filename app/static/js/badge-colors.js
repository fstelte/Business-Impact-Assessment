function setBadgeColor(badge, category) {
    switch(category.toLowerCase()) {
        case 'no ai':
        case 'insignificant':
            badge.classList.add('bg-green');
            break;
        case 'unacceptable risk':
        case 'catastrophic':
            badge.classList.add('bg-dark-red');
            break;
        case 'high risk':
        case 'major':
            badge.classList.add('bg-red');
            break;
        case 'limited risk':
        case 'moderate':
            badge.classList.add('bg-orange');
            break;
        case 'minimal risk':
        case 'minor':
            badge.classList.add('bg-yellow');
            break;
        default:
            badge.classList.add('bg-secondary');
    }
}

function applyBadgeColors() {
    // AI Risk badges
    const aiRiskBadges = document.querySelectorAll('.ai-risk-badge');
    aiRiskBadges.forEach(function(badge) {
        const category = badge.textContent.trim();
        setBadgeColor(badge, category);
    });

    // Consequence badges
    const consequenceBadges = document.querySelectorAll('.consequence-badge');
    consequenceBadges.forEach(function(badge) {
        const category = badge.textContent.trim();
        setBadgeColor(badge, category);
    });
}

// Apply colors when the DOM is loaded
document.addEventListener('DOMContentLoaded', applyBadgeColors);

// Expose the function globally so it can be called from specific views
window.applyBadgeColors = applyBadgeColors;