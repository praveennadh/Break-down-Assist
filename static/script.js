
function showuserLogin() {
    person="user"
    document.getElementById("user-login-form").style.display = "block";
    document.getElementById("user-register-form").style.display = "none";
    document.getElementById("mech-register-form").style.display = "none";
    document.getElementById("mech-login-form").style.display = "none";
}

function showuserRegister() {
    document.getElementById("user-login-form").style.display = "none";
    document.getElementById("user-register-form").style.display = "block";
    document.getElementById("mech-register-form").style.display = "none";
    document.getElementById("mech-login-form").style.display = "none";
}

function showmechRegister() {
    document.getElementById("user-login-form").style.display = "none";
    document.getElementById("user-register-form").style.display = "none";
    document.getElementById("mech-register-form").style.display = "block";
    document.getElementById("mech-login-form").style.display = "none";
}

function showmechLogin() {
    document.getElementById("user-login-form").style.display = "none";
    document.getElementById("user-register-form").style.display = "none";
    document.getElementById("mech-register-form").style.display = "none";
    document.getElementById("mech-login-form").style.display = "block";
}
