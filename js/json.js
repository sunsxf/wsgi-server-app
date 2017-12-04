function ajax() {
    if (window.XMLHttpRequest) {
        // IE7+, Firefox, Chrome, Opera, Safari 浏览器执行代码
        var xmlhttp = new XMLHttpRequest();
    }
    xmlhttp.onreadystatechange = function () {
        if (xmlhttp.readyState == 4 && xmlhttp.status == 200) {
            var resObj = xmlhttp.responseText;
            document.getElementById("tips").innerHTML = resObj;
        }
    };
    var username = document.getElementById("username").value;
    var password = document.getElementById("password").value;
    xmlhttp.open("POST", "/login_confirm", true);
    xmlhttp.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
    xmlhttp.send("username=" + username + "&password=" + password);
}

function valid_test() {
    var username_len = document.getElementById("username").value.length;
    var password_len = document.getElementById("password").value.length;
    if (username_len > 6 || password_len > 6) {
        document.getElementById("tips").innerHTML = "username or password too long";
    }
}