from stackcite.users import models


def create_user(email, password, groups=(), save=False):
    user = models.User()
    user.email = email
    user.set_password(password)
    for g in groups:
        user.add_group(g)
    if save:
        user.save()
    return user


def create_auth_token(user, clean=True, save=False):
    token = models.AuthToken(_user=user)
    if save:
        token.save()
    return token


def create_conf_token(user, clean=True, save=False):
    token = models.ConfirmToken(_user=user)
    if save:
        token.save()
    return token
