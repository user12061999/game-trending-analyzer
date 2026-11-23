/* Page bootstrap (runs after all other scripts) */
document.addEventListener('DOMContentLoaded', () => {
  lucide.createIcons();
  switchCategory('market', 'overview');
  document.getElementById('targetDate').addEventListener('change', () => {
    loadOverview();
    loadPCRankings();
    loadMobileRankings();
  });
});
