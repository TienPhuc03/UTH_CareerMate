
function checkAuthStatus() {
    const token = localStorage.getItem('access_token');
    const email = localStorage.getItem('user_email');
    const role = localStorage.getItem('user_role');
    // Các phần tử cần thao tác trong Header
    const authButtons = document.getElementById('authButtons');
    const userInfo = document.getElementById('userInfo');
    const dashboardContainer = document.getElementById('roleBasedDashboard');
    const menu1 = document.getElementById('menu-item-1');
    const menu2 = document.getElementById('menu-item-2');
    const menu3 = document.getElementById('menu-item-3');

    
    // Nếu không tìm thấy Header (do đang nạp chậm), thì dừng lại
    if (!authButtons || !userInfo) return;

    if (token && email) {
        // TRẠNG THÁI: ĐÃ ĐĂNG NHẬP
        authButtons.classList.add('hidden');
        userInfo.classList.remove('hidden');
        userInfo.classList.add('flex');

        if (dashboardContainer) {  
            if (role === 'student') {
            // Xóa nội dung cũ (nếu có)
            dashboardContainer.innerHTML = `
                    <a href="../page/Studentdashboard.html" class="flex items-center gap-3 px-4 py-3 text-gray-700 hover:bg-gray-50 hover:text-green-600 transition-colors">
                        <i class="fas fa-user-graduate text-green-600 w-5"></i>
                        <span>Student Dashboard</span>
                    </a>`;
            }else if (role ==='recruiter') {
            dashboardContainer.innerHTML = `
                    <a href="../page/Recruiterdashboard.html" class="flex items-center gap-3 px-4 py-3 text-gray-700 hover:bg-gray-50 hover:text-sky-600 transition-colors">
                        <i class="fas fa-briefcase text-sky-600 w-5"></i>
                        <span>Recruiter Dashboard</span>
                    </a>`;
            }
         }
         if (token && role === 'recruiter') {
        // Thay đổi cho Nhà tuyển dụng
                 if(menu1) menu1.innerHTML = `<a href="../page/Formpostjob.html" class="py-3 block hover:text-green-600 lg:py-0 ">Đăng tin</a>`;
                 if(menu2) menu2.innerHTML = `<a href="../page/Viewcandidate.html" class="py-3 block hover:text-green-600 lg:py-0 ">Danh sách ứng viên</a>`;
                 if(menu3) menu3.style.display = 'none'; // Ẩn AI Coach nếu không cần
         } else {
        // Giữ mặc định cho Student/Khách
                if(menu1) menu1.innerHTML = `<a href="#" class="py-3 block hover:text-green-600 lg:py-0">Mẫu CV</a>`;
                if(menu2) menu2.innerHTML = `<a href="../page/Uploadcv.html" class="py-3 block hover:text-green-600 lg:py-0">Tạo CV</a>`;
                if(menu3) {
                      menu3.style.display = 'block';
                      menu3.innerHTML = `<a href="../page/Careerai.html" class="py-3 block hover:text-green-600 lg:py-0">AI Coach</a>`;
                 }
             }
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

