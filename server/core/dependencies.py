

# Docker đang tìm hàm này, ông phải có nó ở đây
def get_current_user():
    """
    Hàm giả lập trả về user admin để ông test được API Admin/Recruiter.
    Sau này ông sẽ viết logic giải mã JWT token ở đây.
    """
    # Tạo object giả lập có thuộc tính .role để không bị lỗi ở middleware
    class MockUser:
        def __init__(self):
            self.id = 1
            self.role = "admin" # Để "admin" để test module Admin
            
    return MockUser()