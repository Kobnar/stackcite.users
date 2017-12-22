from stackcite.users import models


def create_user(email, password=None, groups=(), save=False):
    user = models.User(email=email)
    if password:
        user.set_password(password)
    for g in groups:
        user.add_group(g)
    if save:
        user.save()
    return user


def create_auth_token(user, clean=True, save=False):
    token = models.AuthToken.new(user=user)
    if save:
        token.save()
    return token


def create_conf_token(user, clean=True, save=False):
    token = models.ConfirmToken.new(user=user)
    if save:
        token.save()
    return token
