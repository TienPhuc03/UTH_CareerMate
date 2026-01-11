#hàm lưu file vào ổ cứng/cloud
def normalize_text(text: str) -> str:
    """
    Chuẩn hoá text CV (sau này dùng cho AI / search)
    """
    return text.strip().lower()
