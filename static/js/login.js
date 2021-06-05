var login = function () {
    var data = jqu.formData('form_login');
    if (data.username == '') {
        alert('请输入用户名');
        return;
    }
    if (data.password == '') {
        alert('请输入密码');
        return;
    }
    jqu.loadJson('/api/user/login', data, function (result) {
        if (!result.succ) {
            alert(result.stmt);
            return;
        }
        alert('欢迎 ' + result.name + ' 同学登录 温室环境检测与管理系统 ！');
        window.location.href = "/device"
    });
};
