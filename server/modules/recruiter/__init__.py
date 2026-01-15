# server/modules/recruiter/           🆕 TẠO FOLDER MỚI (BE #2 làm)
# │
# ├── 📄 __init__.py                  🆕 TẠO MỚI
# │   └── Empty file
# │
# ├── 📄 router.py                    🆕 TẠO MỚI (BE #2 làm)
# │   └── Nhiệm vụ: API endpoints cho Recruiters
# │   └── Endpoints:
# │       
# │       💼 QUẢN LÝ JOBS CỦA MÌNH
# │       • GET /api/recruiter/jobs
# │         ├─ Nhiệm vụ: Lấy danh sách jobs mình đã đăng
# │         ├─ Filter: WHERE recruiter_email = current_user.email
# │         └─ Response: Chỉ thấy jobs của mình
# │       
# │       • POST /api/recruiter/jobs
# │         ├─ Nhiệm vụ: Đăng job mới
# │         ├─ Body: {title, description, salary_range, job_type, location}
# │         └─ Auto set: recruiter_email = current_user.email
# │       
# │       • PUT /api/recruiter/jobs/{job_id}
# │         ├─ Nhiệm vụ: Sửa job của mình
# │         ├─ Check: Chỉ sửa được nếu job.recruiter_email == current_user.email
# │         └─ Return 403 nếu không phải job của mình
# │       
# │       • DELETE /api/recruiter/jobs/{job_id}
# │         └─ Nhiệm vụ: Xóa job của mình (nếu chưa có ứng viên)
# │       
# │       📋 XEM ỨNG VIÊN
# │       • GET /api/recruiter/jobs/{job_id}/applications
# │         ├─ Nhiệm vụ: Xem tất cả ứng viên cho job của mình
# │         ├─ Check ownership: job.recruiter_email == current_user.email
# │         └─ Response: List applications với CV info và matching_score
# │       
# │       • PUT /api/recruiter/applications/{app_id}/status
# │         ├─ Nhiệm vụ: Cập nhật trạng thái ứng tuyển
# │         ├─ Body: {"new_status": "REVIEWING", "notes": "..."}
# │         ├─ Validate: Status transition hợp lệ (dùng workflow.py)
# │         └─ Side effect: Gửi notification cho candidate
# │       
# │       • GET /api/recruiter/applications/{app_id}/cv
# │         ├─ Nhiệm vụ: Xem CV chi tiết của candidate
# │         └─ Return: Full CV data + AI analysis
# │       
# │       🔍 TÌM ỨNG VIÊN
# │       • GET /api/recruiter/candidates/search
# │         ├─ Nhiệm vụ: Tìm candidates theo skills
# │         ├─ Params: skills=python,react&experience_years=2
# │         └─ Response: List CVs matching criteria
# │       
# │       • GET /api/recruiter/candidates/{cv_id}
# │         ├─ Nhiệm vụ: Xem profile candidate
# │         └─ Response: CV info + past applications
# │       
# │       • POST /api/recruiter/candidates/{cv_id}/invite
# │         ├─ Nhiệm vụ: Mời candidate ứng tuyển vào job của mình
# │         └─ Side effect: Gửi notification/email cho candidate
# │       
# │       📊 THỐNG KÊ
# │       • GET /api/recruiter/stats
# │         ├─ Nhiệm vụ: Thống kê tuyển dụng của mình
# │         └─ Response:
# │             {
# │               "total_jobs_posted": 15,
# │               "total_applications": 120,
# │               "by_status": {
# │                 "pending": 30,
# │                 "reviewing": 40,
# │                 "interviewed": 20,
# │                 "accepted": 15,
# │                 "rejected": 15
# │               },
# │               "avg_time_to_hire": "14 days",
# │               "acceptance_rate": "12.5%"
# │             }
# │
# └── 📄 analytics.py                 🆕 TẠO MỚI (BE #2 làm)
#     └── Nhiệm vụ: Tính toán stats cho recruiter
#     └── Functions:
#         • get_recruiter_stats(recruiter_email, db) - Thống kê tổng quan
#         • calculate_time_to_hire(recruiter_email, db) - Thời gian trung bình tuyển được người
#         • get_application_funnel(job_id, db) - Phễu ứng tuyển (bao nhiêu % qua mỗi stage)