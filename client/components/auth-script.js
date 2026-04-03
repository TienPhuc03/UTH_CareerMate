function normalizeRole(role) {
  return role === "student" ? "candidate" : role;
}

function checkAuthStatus() {
  const token = sessionStorage.getItem("access_token"); // ← đổi sang sessionStorage
  const email = localStorage.getItem("user_email");
  const rawRole = localStorage.getItem("user_role");
  const role = normalizeRole(rawRole);

  if (rawRole !== role && role) {
    localStorage.setItem("user_role", role);
  }

  const authButtons = document.getElementById("authButtons");
  const userInfo = document.getElementById("userInfo");
  const dashboardContainer = document.getElementById("roleBasedDashboard");
  const menu1 = document.getElementById("menu-item-1");
  const menu2 = document.getElementById("menu-item-2");
  const menu3 = document.getElementById("menu-item-3");

  if (!authButtons || !userInfo) return;

  if (token && email) {
    authButtons.classList.add("hidden");
    userInfo.classList.remove("hidden");
    userInfo.classList.add("flex");

    if (dashboardContainer) {
      if (role === "candidate") {
        dashboardContainer.innerHTML = `
                    <a href="../page/Studentdashboard.html" class="flex items-center gap-3 px-4 py-3 text-gray-700 transition-colors hover:bg-gray-50 hover:text-green-600">
                        <i class="fas fa-user-graduate w-5 text-green-600"></i>
                        <span>Candidate Dashboard</span>
                    </a>`;
      } else if (role === "recruiter") {
        dashboardContainer.innerHTML = `
                    <a href="../page/Recruiterdashboard.html" class="flex items-center gap-3 px-4 py-3 text-gray-700 transition-colors hover:bg-gray-50 hover:text-sky-600">
                        <i class="fas fa-briefcase w-5 text-sky-600"></i>
                        <span>Recruiter Dashboard</span>
                    </a>`;
      } else {
        dashboardContainer.innerHTML = "";
      }
    }

    if (role === "recruiter") {
      if (menu1)
        menu1.innerHTML = `<a href="../page/Formpostjob.html" class="block py-3 hover:text-green-600 lg:py-0">Đăng tin</a>`;
      if (menu2)
        menu2.innerHTML = `<a href="../page/Viewcandidate.html" class="block py-3 hover:text-green-600 lg:py-0">Danh sách ứng viên</a>`;
      if (menu3) menu3.style.display = "none";
    } else {
      if (menu1)
        menu1.innerHTML = `<a href="../page/Printcv.html" class="block py-3 hover:text-green-600 lg:py-0">Mẫu CV</a>`;
      if (menu2)
        menu2.innerHTML = `<a href="../page/Uploadcv.html" class="block py-3 hover:text-green-600 lg:py-0">Tạo CV</a>`;
      if (menu3) {
        menu3.style.display = "block";
        menu3.innerHTML = `<a href="../page/Careerai.html" class="block py-3 hover:text-green-600 lg:py-0">AI Coach</a>`;
      }
    }

    const nameParts = email.split("@")[0];
    const displayName = nameParts.charAt(0).toUpperCase() + nameParts.slice(1);
    const initials = displayName.substring(0, 2).toUpperCase();

    ["userNameDisplay", "dropdownUserName"].forEach((id) => {
      const element = document.getElementById(id);
      if (element) element.textContent = displayName;
    });

    ["userEmailDisplay", "dropdownUserEmail"].forEach((id) => {
      const element = document.getElementById(id);
      if (element) element.textContent = email;
    });

    const avatar = document.getElementById("userAvatar");
    if (avatar) avatar.textContent = initials;
  } else {
    authButtons.classList.remove("hidden");
    userInfo.classList.add("hidden");
    userInfo.classList.remove("flex");
  }
}

function logout() {
  sessionStorage.removeItem("access_token"); // ← đổi
  localStorage.removeItem("access_token"); // ← thêm dòng này để dọn dẹp cả hai nơi
  localStorage.removeItem("user_email");
  localStorage.removeItem("user_role");
  localStorage.removeItem("full_name");
  window.location.href = "../page/Homepage.html";
}

function initEvents() {
  checkAuthStatus();

  const userMenuToggle = document.getElementById("userMenuToggle");
  const userDropdown = document.getElementById("userDropdown");

  if (userMenuToggle && userDropdown) {
    const newToggle = userMenuToggle.cloneNode(true);
    userMenuToggle.parentNode.replaceChild(newToggle, userMenuToggle);

    newToggle.addEventListener("click", (event) => {
      event.stopPropagation();
      userDropdown.classList.toggle("hidden");
    });

    document.addEventListener("click", (event) => {
      if (
        !userDropdown.contains(event.target) &&
        !newToggle.contains(event.target)
      ) {
        userDropdown.classList.add("hidden");
      }
    });
  }
}

if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", initEvents);
} else {
  initEvents();
}
