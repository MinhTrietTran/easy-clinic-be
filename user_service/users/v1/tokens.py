from rest_framework_simplejwt.tokens import RefreshToken # type: ignore

class CustomRefreshToken(RefreshToken):
    @classmethod
    def for_user(cls, user):
        token = super().for_user(user)
        token['role'] = user.role
        return token
    