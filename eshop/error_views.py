from django.shortcuts import render


ERROR_INFO = {
    400: {
        'title': 'Yêu Cầu Không Hợp Lệ',
        'icon': 'fas fa-exclamation-triangle',
        'color': '#f5365c',
        'message': 'Yêu cầu của bạn có cú pháp không hợp lệ. Vui lòng kiểm tra lại.',
    },
    401: {
        'title': 'Chưa Xác Thực',
        'icon': 'fas fa-lock',
        'color': '#fb6340',
        'message': 'Bạn cần đăng nhập để truy cập trang này.',
    },
    403: {
        'title': 'Không Có Quyền Truy Cập',
        'icon': 'fas fa-ban',
        'color': '#f5365c',
        'message': 'Bạn không có quyền truy cập vào tài nguyên này.',
    },
    404: {
        'title': 'Không Tìm Thấy Trang',
        'icon': 'fas fa-search',
        'color': '#667eea',
        'message': 'Trang bạn tìm kiếm không tồn tại hoặc đã bị xóa.',
    },
    405: {
        'title': 'Phương Thức Không Hợp Lệ',
        'icon': 'fas fa-exchange-alt',
        'color': '#fb6340',
        'message': 'Phương thức HTTP không được phép cho trang này.',
    },
    408: {
        'title': 'Hết Thời Gian Chờ',
        'icon': 'fas fa-clock',
        'color': '#fb6340',
        'message': 'Yêu cầu mất quá nhiều thời gian. Vui lòng thử lại.',
    },
    409: {
        'title': 'Xung Đột Dữ Liệu',
        'icon': 'fas fa-exclamation-circle',
        'color': '#fb6340',
        'message': 'Dữ liệu bị xung đột. Vui lòng làm mới và thử lại.',
    },
    410: {
        'title': 'Trang Đã Bị Xóa',
        'icon': 'fas fa-trash-alt',
        'color': '#f5365c',
        'message': 'Trang này đã bị xóa vĩnh viễn và không còn tồn tại.',
    },
    413: {
        'title': 'Dữ Liệu Quá Lớn',
        'icon': 'fas fa-weight-hanging',
        'color': '#fb6340',
        'message': 'Dữ liệu gửi lên quá lớn. Vui lòng giảm kích thước.',
    },
    414: {
        'title': 'URL Quá Dài',
        'icon': 'fas fa-link',
        'color': '#fb6340',
        'message': 'Địa chỉ URL quá dài. Vui lòng sử dụng URL ngắn hơn.',
    },
    415: {
        'title': 'Định Dạng Không Hỗ Trợ',
        'icon': 'fas fa-file',
        'color': '#fb6340',
        'message': 'Định dạng file không được hỗ trợ.',
    },
    422: {
        'title': 'Dữ Liệu Không Hợp Lệ',
        'icon': 'fas fa-clipboard-check',
        'color': '#fb6340',
        'message': 'Dữ liệu gửi lên không hợp lệ. Vui lòng kiểm tra lại.',
    },
    429: {
        'title': 'Gửi Quá Nhiều Yêu Cầu',
        'icon': 'fas fa-tachometer-alt',
        'color': '#f5365c',
        'message': 'Bạn đã gửi quá nhiều yêu cầu. Vui lòng thử lại sau.',
    },
    500: {
        'title': 'Lỗi Máy Chủ',
        'icon': 'fas fa-server',
        'color': '#f5365c',
        'message': 'Máy chủ đang gặp sự cố. Chúng tôi đang khắc phục, vui lòng thử lại sau.',
    },
    501: {
        'title': 'Chưa Hỗ Trợ',
        'icon': 'fas fa-tools',
        'color': '#fb6340',
        'message': 'Máy chủ chưa hỗ trợ tính năng này.',
    },
    502: {
        'title': 'Lỗi Cổng Kết Nối',
        'icon': 'fas fa-network-wired',
        'color': '#f5365c',
        'message': 'Máy chủ trung gian nhận phản hồi lỗi. Vui lòng thử lại sau.',
    },
    503: {
        'title': 'Dịch Vụ Không Khả Dụng',
        'icon': 'fas fa-exclamation-triangle',
        'color': '#f5365c',
        'message': 'Máy chủ đang quá tải hoặc bảo trì. Vui lòng quay lại sau.',
    },
    504: {
        'title': 'Hết Thời Gian Kết Nối',
        'icon': 'fas fa-hourglass-end',
        'color': '#f5365c',
        'message': 'Máy chủ không phản hồi kịp thời. Vui lòng thử lại.',
    },
    505: {
        'title': 'Phiên Bản Không Hỗ Trợ',
        'icon': 'fas fa-code-branch',
        'color': '#fb6340',
        'message': 'Phiên bản HTTP không được hỗ trợ.',
    },
}

DEFAULT_ERROR = {
    'title': 'Đã Xảy Ra Lỗi',
    'icon': 'fas fa-bug',
    'color': '#f5365c',
    'message': 'Đã xảy ra lỗi không xác định. Vui lòng thử lại.',
}


def error_view(request, status_code):
    info = ERROR_INFO.get(status_code, DEFAULT_ERROR)
    context = {
        'status_code': status_code,
        **info,
    }
    return render(request, 'errors/error.html', context, status=status_code)


# Django handler overrides
def bad_request(request, exception=None):
    return error_view(request, 400)


def permission_denied(request, exception=None):
    return error_view(request, 403)


def page_not_found(request, exception=None):
    return error_view(request, 404)


def server_error(request):
    return error_view(request, 500)
