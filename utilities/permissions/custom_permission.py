# from rest_framework.permissions import BasePermission


# class HasKannaPermission(BasePermission):
#     def has_permission(self, request, view):
#         if not bool(
#             request.user and request.user.is_authenticated and request.user.kanna_user
#         ):
#             return False

#         return True
