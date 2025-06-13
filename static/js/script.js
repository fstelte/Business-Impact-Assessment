<script>
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
document.addEventListener('DOMContentLoaded', function() {
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

    // CIA Impact Overview badges
    const ciaImpactBadges = document.querySelectorAll('.cia-impact-badge');
    ciaImpactBadges.forEach(function(badge) {
        const impact = badge.textContent.trim();
        setCIAImpactBadgeColor(badge, impact);
    });
});