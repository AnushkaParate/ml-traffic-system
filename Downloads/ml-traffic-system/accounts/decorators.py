from functools import wraps

from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied


def admin_required(view_func):
    """Restrict a view to users whose Profile.role is 'admin'.

    Use this on any view that should only be reachable by traffic admins,
    e.g. reporting a violation, viewing the admin dashboard stats, managing
    challans. Regular vehicle owners get a 403 if they try to access it
    directly by URL.
    """
    @wraps(view_func)
    @login_required
    def wrapper(request, *args, **kwargs):
        is_admin = hasattr(request.user, 'profile') and request.user.profile.is_admin
        if not is_admin:
            raise PermissionDenied('This page is for traffic admins only.')
        return view_func(request, *args, **kwargs)
    return wrapper