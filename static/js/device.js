var initDate = function () {
    jqu.formItem('start_time', 'form_search').datetimepicker({
        format: 'yyyy-mm-dd',
        autoclose: 1,
        todayHighlight: 1,
        todayBtn: true,
        language: 'zh-CN',
        minView: 2
    });
    jqu.formItem('end_time', 'form_search').datetimepicker({
        format: 'yyyy-mm-dd',
        autoclose: 1,
        todayHighlight: 1,
        todayBtn: true,
        language: 'zh-CN',
        minView: 2
    });
};

$(initDate);

var search = function () {
    $('#form_search').get(0).submit();
};

var addDevice = function () {
    var data = jqu.formData('form_addDevice');
    if (data.device_id == '') {
        alert('请输入传感器ID');
        return;
    }
    if (data.device_location == '') {
        alert('请输入传感器位置');
        return;
    }
    if (!confirm('确定注册传感器 ' + data.device_id + ' 到 ' + data.device_location + ' ?'))
        return;
    // alert(jqu.obj2json(data));
    jqu.loadJson('/api/device/insert_device', data, function (result) {
        if (!result.succ) {
            alert(result.stmt);
            return;
        }
        alert('注册传感器成功!');
        $('#form_search').get(0).submit();
    });
};

var deleteDevice = function (device_id) {
    if (!confirm('确定要删除传感器 ' + device_id + ' 吗？'))
        return;
    jqu.loadJson('/api/device/delete_device_by_id', {device_id: device_id}, function (result) {
        if (!result.succ) {
            alert(result.stmt);
            return;
        }
        alert('传感器' + device_id + '删除成功!');
        $('#form_search').get(0).submit();
    });
};

var selectDevice = function (device_id) {
    jqu.loadJson('/api/device/get_device_by_id', {device_id: device_id}, function (result) {
        // alert(jqu.obj2json(result))
        jqu.formLoad('form_updateDevice', result);
        $('#updateDevice').modal('show');
    });
};

var updateDevice = function () {
    var data = jqu.formData('form_updateDevice');
    if (data.update_device_location == '') {
        alert('请输入传感器位置');
        return;
    }
    if (!confirm('确定修改传感器 ' + data.update_device_id + ' 的位置为 ' + data.update_device_location + ' ?'))
        return;
    // alert(jqu.obj2json(data));
    jqu.loadJson('/api/device/update_device_by_id', data, function (result) {
        if (!result.succ) {
            alert(result.stmt);
            return;
        }
        alert('修改成功!');
        $('#form_search').get(0).submit();
    });
};
var light_on = function () {
    var form = new FormData();
    form.append("ip", "192.168.199.241");
    form.append("token", "2617ab888f955e4d8abd651294a7d273");
    form.append("active", "True");

    var settings = {
      "url": "https://things.abu.pub/api/device/active",
      "method": "POST",
      "timeout": 0,
      "processData": false,
      "mimeType": "multipart/form-data",
      "contentType": false,
      "data": form
    };
    alert('显示器挂灯【SN300001】启动指令已发出！');
    $.ajax(settings).done(function (response) {
      console.log(response);
    });
};

var light_off = function () {
    var form = new FormData();
    form.append("ip", "192.168.199.241");
    form.append("token", "2617ab888f955e4d8abd651294a7d273");
    form.append("active", "False");

    var settings = {
      "url": "https://things.abu.pub/api/device/active",
      "method": "POST",
      "timeout": 0,
      "processData": false,
      "mimeType": "multipart/form-data",
      "contentType": false,
      "data": form
    };
    alert('显示器挂灯【SN300001】关闭指令已发出！');
    $.ajax(settings).done(function (response) {
      console.log(response);
    });
};


var humitidy_on = function () {
    var form = new FormData();
    form.append("ip", "192.168.199.147");
    form.append("token", "1dee6e754113ff745cd0785e011fbf24");
    form.append("active", "True");

    var settings = {
      "url": "https://things.abu.pub/api/device/active",
      "method": "POST",
      "timeout": 0,
      "processData": false,
      "mimeType": "multipart/form-data",
      "contentType": false,
      "data": form
    };
    alert('加湿器【SN200001】启动指令已发出！');
    $.ajax(settings).done(function (response) {
      console.log(response);
    });
};

var humitidy_off = function () {
    var form = new FormData();
    form.append("ip", "192.168.199.147");
    form.append("token", "1dee6e754113ff745cd0785e011fbf24");
    form.append("active", "False");

    var settings = {
      "url": "https://things.abu.pub/api/device/active",
      "method": "POST",
      "timeout": 0,
      "processData": false,
      "mimeType": "multipart/form-data",
      "contentType": false,
      "data": form
    };
    alert('加湿器【SN200001】关闭指令已发出！'); 
    $.ajax(settings).done(function (response) {
      console.log(response);
    });
};

