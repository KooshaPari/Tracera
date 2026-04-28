// Clear authentication and force re-login
// Run this in browser console (Cmd+Option+I) to fix expired token issue

console.log('🔧 Clearing expired authentication...');

// Clear all storage
localStorage.clear();
sessionStorage.clear();

// Clear cookies
document.cookie.split(";").forEach(function(c) {
    document.cookie = c.replace(/^ +/, "").replace(/=.*/, "=;expires=" + new Date().toUTCString() + ";path=/");
});

console.log('✅ Authentication cleared');
console.log('🔄 Reloading page...');

// Reload to trigger login redirect
setTimeout(() => {
    window.location.href = '/';
}, 500);
