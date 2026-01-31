function checkAuthStatus() {
    const token = localStorage.getItem('access_token');
    const email = localStorage.getItem('user_email');
    
    if (token && email) {
        document.getElementById('authButtons').classList.add('hidden');
        document.getElementById('userInfo').classList.remove('hidden');
        document.getElementById('userInfo').classList.add('flex');
        
        const nameParts = email.split('@')[0];
        const displayName = nameParts.charAt(0).toUpperCase() + nameParts.slice(1);
        const initials = displayName.substring(0, 2).toUpperCase();
        
        document.getElementById('userNameDisplay').textContent = displayName;
        document.getElementById('userEmailDisplay').textContent = email;
        document.getElementById('dropdownUserName').textContent = displayName;
        document.getElementById('dropdownUserEmail').textContent = email;
        document.getElementById('userAvatar').textContent = initials;
    } else {
        document.getElementById('authButtons').classList.remove('hidden');
        document.getElementById('userInfo').classList.add('hidden');
    }
}

function logout() {
    localStorage.removeItem('access_token');
    localStorage.removeItem('user_email');
    alert('Đăng xuất thành công!');
    window.location.href = 'Homepage.html';
}

document.addEventListener('DOMContentLoaded', function() {
    checkAuthStatus();
    
    const userMenuToggle = document.getElementById('userMenuToggle');
    const userDropdown = document.getElementById('userDropdown');
    
    if (userMenuToggle) {
        userMenuToggle.addEventListener('click', function(e) {
            e.stopPropagation();
            userDropdown.classList.toggle('hidden');
        });
    }
    
    document.addEventListener('click', function(e) {
        if (userDropdown && !userDropdown.contains(e.target) && !userMenuToggle.contains(e.target)) {
            userDropdown.classList.add('hidden');
        }
    });
    
    const dropdownItems = document.querySelectorAll('#userDropdown a, #userDropdown button');
    dropdownItems.forEach(item => {
        item.addEventListener('click', function() {
            userDropdown.classList.add('hidden');
        });
    });
});
