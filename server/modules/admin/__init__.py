# server/modules/admin/               🆕 TẠO FOLDER MỚI (BE #2 làm)
# │
# ├── 📄 __init__.py                  🆕 TẠO MỚI
# │   └── Empty file để Python recognize folder này là module
# │
# ├── 📄 router.py                    🆕 TẠO MỚI (BE #2 làm)
# │   └── Nhiệm vụ: API endpoints cho Admin
# │   └── Endpoints:
# │       
# │       📊 QUẢN LÝ USERS
# │       • GET /api/admin/users
# │         ├─ Nhiệm vụ: List tất cả users (có pagination, filters)
# │         ├─ Params: page, limit, role, is_active, search
# │         └─ Response: List users với thông tin chi tiết
# │       
# │       • GET /api/admin/users/{user_id}
# │         ├─ Nhiệm vụ: Xem chi tiết 1 user
# │         └─ Response: User info + số CVs + số applications
# │       
# │       • PUT /api/admin/users/{user_id}/status
# │         ├─ Nhiệm vụ: Kích hoạt/Vô hiệu hóa tài khoản
# │         ├─ Body: {"is_active": true/false, "reason": "..."}
# │         └─ Side effect: Log hành động admin
# │       
# │       • DELETE /api/admin/users/{user_id}
# │         ├─ Nhiệm vụ: Xóa user (cascade delete CVs, applications)
# │         └─ Warning: Cẩn thận với cascade deletes!
# │       
# │       • GET /api/admin/users/stats
# │         ├─ Nhiệm vụ: Thống kê users
# │         └─ Response: Total, active, by_role, new_this_month
# │       
# │       📋 QUẢN LÝ JOBS
# │       • GET /api/admin/jobs
# │         ├─ Nhiệm vụ: List tất cả jobs (có filters)
# │         └─ Params: status, company, date_from, date_to
# │       
# │       • PUT /api/admin/jobs/{job_id}/approve
# │         ├─ Nhiệm vụ: Duyệt job (nếu có approval workflow)
# │         └─ Body: {"approved": true, "notes": "..."}
# │       
# │       • DELETE /api/admin/jobs/{job_id}
# │         └─ Nhiệm vụ: Xóa job vi phạm policy
# │       
# │       📄 QUẢN LÝ CVs
# │       • GET /api/admin/cvs
# │         ├─ Nhiệm vụ: List tất cả CVs
# │         └─ Params: page, limit, email, skills
# │       
# │       • DELETE /api/admin/cvs/{cv_id}
# │         └─ Nhiệm vụ: Xóa CV spam/fake
# │       
# │       📝 QUẢN LÝ APPLICATIONS
# │       • GET /api/admin/applications
# │         ├─ Nhiệm vụ: Xem tất cả applications
# │         └─ Params: status, job_id, date_from, date_to
# │       
# │       • GET /api/admin/applications/stats
# │         └─ Nhiệm vụ: Thống kê applications
# │       
# │       📈 DASHBOARD STATS
# │       • GET /api/admin/dashboard/stats
# │         ├─ Nhiệm vụ: Tổng quan hệ thống (cho admin dashboard)
# │         └─ Response: 
# │             {
# │               "users": {total, active, new_this_month, by_role},
# │               "jobs": {total, active, by_type},
# │               "cvs": {total, uploaded_this_month, avg_ats_score},
# │               "applications": {total, by_status, acceptance_rate},
# │               "trends": {top_skills, hot_companies}
# │             }
# │
# ├── 📄 analytics.py                 🆕 TẠO MỚI (BE #2 làm)
# │   └── Nhiệm vụ: Tính toán statistics cho dashboard
# │   └── Functions:
# │       • calculate_user_stats(db) - Thống kê users
# │       • calculate_job_stats(db) - Thống kê jobs
# │       • calculate_application_stats(db) - Thống kê applications
# │       • get_trending_skills(db) - Top skills đang hot
# │       • get_top_companies(db) - Companies đăng nhiều job nhất
# │       • export_users_to_csv(db) - Export users ra CSV (bonus)
# │
# └── 📄 middleware.py                🆕 TẠO MỚI (BE #2 làm)
#     └── Nhiệm vụ: Kiểm tra quyền admin
#     └── Functions:
#         • require_admin() - Decorator để protect admin routes
#         • log_admin_action() - Ghi log mọi hành động của admin


# Phần này note cho ông check phần user role admin
# server/modules/users/
# │
# ├── 📄 model.py                     🔄 CẬP NHẬT (BE #2 làm)
# │   └── Nhiệm vụ: Thêm field `role`
# │   └── Code cần thêm:
# │       class User(Base):
# │           # ... existing fields
# │           role = Column(String, default="candidate")
# │           # Giá trị: "candidate", "recruiter", "admin"
# │
# ├── 📄 schemas.py                   ✅ ĐÃ CÓ
# │   └── UserCreate, UserOut, Token
# │
# ├── 📄 router.py                    ✅ ĐÃ CÓ
# │   └── POST /api/Auth/register
# │   └── POST /api/Auth/login
# │
# └── 📄 curd.py                      ✅ ĐÃ CÓ
#     └── get_user_by_email()
#     └── create_user()