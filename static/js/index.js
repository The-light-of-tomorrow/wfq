function getClientHeight() {
    var clientHeight = 0;
    if (document.body.clientHeight && document.documentElement.clientHeight) {
        var clientHeight = (document.body.clientHeight < document.documentElement.clientHeight) ? document.body.clientHeight : document.documentElement.clientHeight;
    } else {
        var clientHeight = (document.body.clientHeight > document.documentElement.clientHeight) ? document.body.clientHeight : document.documentElement.clientHeight;
    }
    return clientHeight;
}

var initPlane = function () {
    var clientHeight = getClientHeight()
    console.log(clientHeight)
    var tdHeight = clientHeight - 248
    console.log(tdHeight)
    document.getElementById('needModifyTr').setAttribute("style", "height: " + tdHeight + "px;");
    jqu.loadJson('/setting/get', {}, function (result) {
        if (result.status_sender == 1) {
            document.getElementById('SenderRun').setAttribute("class", "btn btn-success disabled");
            document.getElementById('SenderRun').setAttribute("onclick", "");
        }
        if (result.status_router == 1) {
            document.getElementById('RouterRun').setAttribute("class", "btn btn-success disabled");
            document.getElementById('RouterRun').setAttribute("onclick", "");
        }
        if (result.status_receiver == 1) {
            document.getElementById('ReceiverRun').setAttribute("class", "btn btn-success disabled");
            document.getElementById('ReceiverRun').setAttribute("onclick", "");
        }
    });
};

$(initPlane);

var Receiver = echarts.init(document.getElementById('Receiver'));
ReceiverOption = {
    tooltip: {
        trigger: 'axis',
        axisPointer: {
            type: 'cross',
            label: {
                backgroundColor: '#6a7985'
            }
        }
    },
    legend: {
        data: ['FlowID 1', 'FlowID 2', 'FlowID 3']
    },
    grid: {
        left: '3%',
        right: '4%',
        bottom: '3%',
        containLabel: true
    },
    xAxis: [
        {
            type: 'category',
            boundaryGap: false,
            data: ['0s', '2s', '4s', '6s', '8s', '10s', '12s']
        }
    ],
    yAxis: [
        {
            type: 'value',
            axisLabel: {
                formatter: '{value} Bytes'
            }
        }
    ],
    series: [
        {
            name: 'FlowID 1',
            type: 'line',
            areaStyle: {},
            emphasis: {
                focus: 'series'
            },
            itemStyle: {
                normal: {
                    color: '#2196f3'
                }
            },
            areaStyle: {
                color: {
                    colorStops: [{
                        offset: 0, color: '#2196f3'
                    }, {
                        offset: 1, color: '#2196f3'
                    }],
                }
            },
            data: [0, 132, 101, 134, 0, 230, 210]
        },
        {
            name: 'FlowID 2',
            type: 'line',
            areaStyle: {},
            emphasis: {
                focus: 'series'
            },
            itemStyle: {
                normal: {
                    color: '#F39494'
                }
            },
            areaStyle: {
                color: {
                    colorStops: [{
                        offset: 0, color: '#F39494'
                    }, {
                        offset: 1, color: '#F39494'
                    }],
                }
            },
            data: [0, 0, 191, 0, 0, 330, 310]
        },
        {
            name: 'FlowID 3',
            type: 'line',
            areaStyle: {},
            emphasis: {
                focus: 'series'
            },

            itemStyle: {
                normal: {
                    color: '#B2DB9E'
                }
            },
            areaStyle: {
                color: {
                    colorStops: [{
                        offset: 0, color: '#B2DB9E'
                    }, {
                        offset: 1, color: '#B2DB9E'
                    }],
                }
            },
            data: [0, 232, 201, 154, 190, 330, 410]
        }
    ]
};
Receiver.setOption(ReceiverOption);
Receiver.showLoading();


var Sender = echarts.init(document.getElementById('Sender'));
SenderOption = {
    tooltip: {
        trigger: 'axis',
        axisPointer: {
            type: 'cross',
            label: {
                backgroundColor: '#6a7985'
            }
        }
    },
    legend: {
        data: ['FlowID 1', 'FlowID 2', 'FlowID 3']
    },
    grid: {
        left: '3%',
        right: '4%',
        bottom: '3%',
        containLabel: true
    },
    xAxis: [
        {
            type: 'category',
            boundaryGap: false,
            data: ['0s', '2s', '4s', '6s', '8s', '10s', '12s']
        }
    ],
    yAxis: [
        {
            type: 'value',
            axisLabel: {
                formatter: '{value} ms'
            }
        }
    ],
    series: [
        {
            name: 'FlowID 1',
            type: 'line',
            data: [0, 101, 134, 0, 230, 210]
        },
        {
            name: 'FlowID 2',
            type: 'line',
            data: [0, 0, 191, 0, 0, 330, 310]
        },
        {
            name: 'FlowID 3',
            type: 'line',
            data: [0, 232, 201, 154, 190, 330, 410]
        }
    ]

}

Sender.setOption(SenderOption);
Sender.showLoading();

setInterval(function () {
    $.get('/data/sender_data_result', function (res) {
        Sender.hideLoading();
        console.log("Sender: ", res);
        Sender.setOption({
            xAxis: {
                type: 'category',
                boundaryGap: false,
                data: res.time_line
            },
            series: [
                {
                    name: 'FlowID 1',
                    type: 'line',
                    data: res.flow_id_1
                },
                {
                    name: 'FlowID 2',
                    type: 'line',
                    data: res.flow_id_2
                },
                {
                    name: 'FlowID 3',
                    type: 'line',
                    data: res.flow_id_3
                }
            ]
        });
    });
    $.get('/data/receiver_data', function (res) {
        Receiver.hideLoading();
        console.log("Receiver: ", res);
        Receiver.setOption({
            xAxis: {
                type: 'category',
                boundaryGap: false,
                data: res.time_line
            },
            series: [
                {
                    name: 'FlowID 1',
                    type: 'line',
                    areaStyle: {},
                    emphasis: {
                        focus: 'series'
                    },
                    itemStyle: {
                        normal: {
                            color: '#2196f3'
                        }
                    },
                    areaStyle: {
                        color: {
                            colorStops: [{
                                offset: 0, color: '#2196f3'
                            }, {
                                offset: 1, color: '#2196f3'
                            }],
                        }
                    },
                    data: res.flow_id_1
                },
                {
                    name: 'FlowID 2',
                    type: 'line',
                    areaStyle: {},
                    emphasis: {
                        focus: 'series'
                    },
                    itemStyle: {
                        normal: {
                            color: '#F39494'
                        }
                    },
                    areaStyle: {
                        color: {
                            colorStops: [{
                                offset: 0, color: '#F39494'
                            }, {
                                offset: 1, color: '#F39494'
                            }],
                        }
                    },
                    data: res.flow_id_2
                },
                {
                    name: 'FlowID 3',
                    type: 'line',
                    areaStyle: {},
                    emphasis: {
                        focus: 'series'
                    },

                    itemStyle: {
                        normal: {
                            color: '#B2DB9E'
                        }
                    },
                    areaStyle: {
                        color: {
                            colorStops: [{
                                offset: 0, color: '#B2DB9E'
                            }, {
                                offset: 1, color: '#B2DB9E'
                            }],
                        }
                    },
                    data: res.flow_id_3
                }
            ]
        });
    });
}, 1000)


var updateSetting = function () {
    var data = jqu.formData('form_setting');
    console.log(data)
    jqu.loadJson('/setting/set', data, function (result) {
        if (result.code != 200) {
            alert(result.code);
            return;
        }
        alert('修改成功!');
        $('#setting').modal('hide');

    });
};

var senderStart = function () {
    jqu.loadJson('/run', {'role': 'Sender'}, function (result) {
        if (result.code == 0) {
            console.log('Sender Start Running!')
        } else {
            alert('Error Code: ' + result.code + ', Msg: ' + result.msg);
            return;
        }
        document.getElementById('SenderRun').setAttribute("class", "btn btn-success disabled");
        document.getElementById('SenderRun').setAttribute("onclick", "");
    });
};

var routerStart = function () {
    console.log('Router Start Running!')
    jqu.loadJson('/run', {'role': 'Router'}, function (result) {
        if (result.code == 0) {
            alert('Router Start Running!');
        } else {
            alert('Error Code: ' + result.code + ', Msg: ' + result.msg);
            return;
        }
        document.getElementById('RouterRun').setAttribute("class", "btn btn-success disabled");
        document.getElementById('RouterRun').setAttribute("onclick", "");
    });
};

var receiverStart = function () {
    console.log('Receiver Start Running!')
    jqu.loadJson('/run', {'role': 'Receiver'}, function (result) {
        if (result.code == 0) {
            alert('Receiver Start Running!');
        } else {
            alert('Error Code: ' + result.code + ', Msg: ' + result.msg);
            return;
        }
        document.getElementById('ReceiverRun').setAttribute("class", "btn btn-success disabled");
        document.getElementById('ReceiverRun').setAttribute("onclick", "");
    });
};

var systemReset = function () {
    console.log('System Rest!')
    jqu.loadJson('/reset', {}, function (result) {
        if (result.code == 0) {
            alert('System Reset!');
            location.reload()
        } else {
            alert('Error Code: ' + result.code + ', Msg: ' + result.msg);
            return;
        }
    });
};
