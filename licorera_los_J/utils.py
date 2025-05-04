import base64
import hashlib
import secrets
from django.shortcuts import redirect, render
from django.contrib import messages
from django.contrib.auth.decorators import login_required

ALGORITHM = "pbkdf2_sha256"


def hash_password(password, salt=None, iterations=260000):
    if salt is None:
        salt = secrets.token_hex(16)
    assert salt and isinstance(salt, str) and "$" not in salt
    assert isinstance(password, str)
    pw_hash = hashlib.pbkdf2_hmac(
        "sha256", password.encode("utf-8"), salt.encode("utf-8"), iterations
    )
    b64_hash = base64.b64encode(pw_hash).decode("ascii").strip()
    return "{}${}${}${}".format(ALGORITHM, iterations, salt, b64_hash)


def verify_password(password, password_hash):
    if (password_hash or "").count("$") != 3:
        return False
    algorithm, iterations, salt, b64_hash = password_hash.split("$", 3)
    iterations = int(iterations)
    assert algorithm == ALGORITHM
    compare_hash = hash_password(password, salt, iterations)
    return secrets.compare_digest(password_hash, compare_hash)


def validar_administrador(view_func):
    def wrapper(request, *args, **kwargs):
        sesion = request.session.get("sesion", None)
        if not sesion or sesion.get("cuenta") != "1":  # Verifica si el usuario es administrador
            messages.error(request, "No tienes permisos para acceder.")
            return redirect("index")  # Redirige al inicio si no es administrador
        return view_func(request, *args, **kwargs)
    return wrapper

