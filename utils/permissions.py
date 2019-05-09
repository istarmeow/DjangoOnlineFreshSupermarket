from rest_framework import permissions


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    对象级权限，只允许对象的所有者编辑它。
    模型实例有一个 user 属性，指向用户的外键。
    """

    def has_object_permission(self, request, view, obj):
        # 读取权限允许任何请求，所以我们总是允许GET、HEAD或OPTIONS请求。
        if request.method in permissions.SAFE_METHODS:
            return True

        # 实例必须有一个名为user的属性。
        return obj.user == request.user
