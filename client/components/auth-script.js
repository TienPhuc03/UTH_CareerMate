// function checkAuthStatus() {
//     const token = localStorage.getItem('access_token');
//     const email = localStorage.getItem('user_email');
    
//     if (token && email) {
//         document.getElementById('authButtons').classList.add('hidden');
//         document.getElementById('userInfo').classList.remove('hidden');
//         document.getElementById('userInfo').classList.add('flex');
        
//         const nameParts = email.split('@')[0];
//         const displayName = nameParts.charAt(0).toUpperCase() + nameParts.slice(1);
//         const initials = displayName.substring(0, 2).toUpperCase();
        
//         document.getElementById('userNameDisplay').textContent = displayName;
//         document.getElementById('userEmailDisplay').textContent = email;
//         document.getElementById('dropdownUserName').textContent = displayName;
//         document.getElementById('dropdownUserEmail').textContent = email;
//         document.getElementById('userAvatar').textContent = initials;
//     } else {
//         document.getElementById('authButtons').classList.remove('hidden');
//         document.getElementById('userInfo').classList.add('hidden');
//     }
// }

// function logout() {
//     localStorage.removeItem('access_token');
//     localStorage.removeItem('user_email');
//     alert('Đăng xuất thành công!');
//     window.location.href = 'Homepage.html';
// }

// document.addEventListener('DOMContentLoaded', function() {
//     checkAuthStatus();
    
//     const userMenuToggle = document.getElementById('userMenuToggle');
//     const userDropdown = document.getElementById('userDropdown');
    
//     if (userMenuToggle) {
//         userMenuToggle.addEventListener('click', function(e) {
//             e.stopPropagation();
//             userDropdown.classList.toggle('hidden');
//         });
//     }
    
//     document.addEventListener('click', function(e) {
//         if (userDropdown && !userDropdown.contains(e.target) && !userMenuToggle.contains(e.target)) {
//             userDropdown.classList.add('hidden');
//         }
//     });
    
//     const dropdownItems = document.querySelectorAll('#userDropdown a, #userDropdown button');
//     dropdownItems.forEach(item => {
//         item.addEventListener('click', function() {
//             userDropdown.classList.add('hidden');
//         });
//     });
// });

// Hàm kiểm tra trạng thái đăng nhập
function checkAuthStatus() {
    const token = localStorage.getItem('access_token');
    const email = localStorage.getItem('user_email');
    
    // Các phần tử cần thao tác trong Header
    const authButtons = document.getElementById('authButtons');
    const userInfo = document.getElementById('userInfo');
    
    // Nếu không tìm thấy Header (do đang nạp chậm), thì dừng lại
    if (!authButtons || !userInfo) return;

    if (token && email) {
        // TRẠNG THÁI: ĐÃ ĐĂNG NHẬP
        authButtons.classList.add('hidden');
        userInfo.classList.remove('hidden');
        userInfo.classList.add('flex');
        
        // Cập nhật tên/avatar
        const nameParts = email.split('@')[0];
        const displayName = nameParts.charAt(0).toUpperCase() + nameParts.slice(1);
        const initials = displayName.substring(0, 2).toUpperCase();
        
        // Điền thông tin vào các thẻ
        const ids = ['userNameDisplay', 'dropdownUserName'];
        ids.forEach(id => {
            const el = document.getElementById(id);
            if(el) el.textContent = displayName;
        });

        const emails = ['userEmailDisplay', 'dropdownUserEmail'];
        emails.forEach(id => {
            const el = document.getElementById(id);
            if(el) el.textContent = email;
        });

        const avatar = document.getElementById('userAvatar');
        if(avatar) avatar.textContent = initials;

    } else {
        // TRẠNG THÁI: CHƯA ĐĂNG NHẬP
        authButtons.classList.remove('hidden');
        userInfo.classList.add('hidden');
        userInfo.classList.remove('flex');
    }
}

// Hàm đăng xuất
function logout() {
    localStorage.removeItem('access_token');
    localStorage.removeItem('user_email');
    localStorage.removeItem('user_role');
    alert('Đăng xuất thành công!');
    window.location.href = 'Homepage.html';
}

// Hàm khởi tạo sự kiện (Dropdown menu)
function initEvents() {
    checkAuthStatus(); // Chạy ngay logic kiểm tra

    const userMenuToggle = document.getElementById('userMenuToggle');
    const userDropdown = document.getElementById('userDropdown');
    
    if (userMenuToggle && userDropdown) {
        // Xóa sự kiện cũ để tránh bị duplicate nếu chạy 2 lần
        const newToggle = userMenuToggle.cloneNode(true);
        userMenuToggle.parentNode.replaceChild(newToggle, userMenuToggle);

        newToggle.addEventListener('click', function(e) {
            e.stopPropagation();
            userDropdown.classList.toggle('hidden');
        });

        // Click ra ngoài thì đóng menu
        document.addEventListener('click', function(e) {
            if (!userDropdown.contains(e.target) && !newToggle.contains(e.target)) {
                userDropdown.classList.add('hidden');
            }
        });
    }
}

// --- PHẦN QUAN TRỌNG NHẤT: TỰ ĐỘNG CHẠY ---
// Kiểm tra xem trang đã tải xong chưa?
if (document.readyState === 'loading') {
    // Nếu chưa xong: Đợi tải xong rồi chạy
    document.addEventListener('DOMContentLoaded', initEvents);
} else {
    // Nếu ĐÃ xong rồi (trường hợp Homepage nạp động): CHẠY NGAY LẬP TỨC
    initEvents();
}

