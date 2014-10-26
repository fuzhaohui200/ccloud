/**
 * 服务请求模块 
 */

var showResourceServiceRequest = function() {
    
    // 通过ajax判断用户是否已登录
    $.get("/functionContent/", function(data){
        $("#pageContent").html(data); // 将主内容页面content.html加载到index.html 相应div里
        showJQDock();  // 显示左侧菜单栏
        $('#functionContent').html('<div id="functionTitle" class="brand">服务请求</div><div id="functionButton"> </div>'
             + '<div id="functionGrid"> </div>');
        
        listServiceRequest();
    });
};

// 查看服务请求详情
var viewServiceRequest = function () {
    var serviceRequestGrid = $("#serviceRequestGrid").data("kendoGrid");
    var serviceRequestGridSelected =  serviceRequestGrid.select();
    if (serviceRequestGridSelected != undefined && serviceRequestGridSelected.length >0) {
       $("#functionGrid").append('<div id="detailServiceRequestWindow"></div>');
       var operatorServiceRequestWindow = $("#detailServiceRequestWindow").kendoWindow({
            title: "查看服务申请",
            modal: true,
            visible: false,
            resizable: true,
            width: 450
        }).data("kendoWindow");
        
        var serviceRequestTemplate = kendo.template("<div id='approves-container'><table>"
            + "<tr><td>系统名称：</td><td>#= systemName #</td></tr>"
            + "<tr><td>申请内容：</td><td><textarea cols='35' rows='2'disabled='disabled'>#= description #</textarea></td></tr>"
            + "<tr><td>申请时间：</td><td>#= submit_time #</td></tr>"
            + "<tr><td>申请状态：</td><td>#= status_message #</td></tr>"
            + "<tr><td>审批人：</td><td>#= approver #</td></tr>"
            + "<tr><td>最后修改时间：</td><td>#= last_modify_time #</td></tr></table></div>");
        
        var dataItem = serviceRequestGrid.dataItem(serviceRequestGridSelected[0]);
        var request_params = eval("(" + dataItem.request_parameter + ")");
        if(dataItem.approver == null) {
            dataItem.approver = "无";
        }
        var itemDetail = {
            "systemName": request_params.name,
            "type": request_params.type,
            "cpu": request_params.cpu,
            "mem": request_params.mem,
            "os_type": request_params.os_type,
            "description": dataItem.description,
            "submit_time": formatDate(dataItem.submit_time),
            "request_status": dataItem.request_type,
            "request_type": dataItem.request_type,
            "state":dataItem.state,
            "status_message": dataItem.status_message,
            "approver": dataItem.approver,
            "last_modify_time": formatDate(dataItem.last_modify_time)
        };
        operatorServiceRequestWindow.content(serviceRequestTemplate(itemDetail));
        operatorServiceRequestWindow.center().open(); 
        
        
    } else   {
        alert("请选择一条记录！");
        return false;
    }
};

// 撤消服务请求
var restServiceRequest = function() {
    var serviceRequestGrid = $("#serviceRequestGrid").data("kendoGrid");
    var serviceRequestGridSelected =  serviceRequestGrid.select();
    if (serviceRequestGridSelected != undefined && serviceRequestGridSelected.length >0) {
        var dataItem = serviceRequestGrid.dataItem(serviceRequestGridSelected[0]);
        $.ajax({
           url:  "/service_request_revoke_available/?service_request_id=" + dataItem.id,
           type: "GET",
           dataType: "json",
           complete: function(data) {
               if(data.responseText == "allow") {
                   if(confirm("确认要撤销服务请求吗？")){
                      $.ajax({
                         type: "GET",
                         url: "/revoke_service_request/?service_request_id=" + dataItem.id,
                         dataType: "text",
                         processData: false,
                         contentType: 'application/json',
                         complete: function(data1) {
                             if(data1.responseText == "done") {
                                alert("服务请求撤消成功！");
                                listServiceRequest();
                             } else {
                                alert("服务请求撤消失败！");
                             }
                         },
                         timeout:60000
                      }); 
                   }
               } else {
                  alert("当前服务申请不允许此操作！");
               }
           }
        });
    } else   {
        alert("请选择一条记录！");
        return false;
    }
};

// 显示服务请求表格
var listServiceRequest = function() {
    
    $("#functionGrid").empty();
    $("#functionGrid").append('<div class="div-button-group" id="divButtonGroup">'
                            + '<a href="javascript:void(0);" onclick="viewServiceRequest();" class="btn btn-small btn-info" type="button">'
                            + '<i class="icon-align-justify"></i>&nbsp;查看申请资源条目'
                            + '</a>'
                            + '</a><a href="javascript:void(0);" onclick="restServiceRequest();" class="btn btn-small btn-info" type="button">'
                            + '<i class="icon-trash"></i>&nbsp;回收'
                            + '</a>'
                            + '<a href="javascript:void(0);" onclick="listServiceRequest();" class="btn btn-small btn-info" type="button">'
                            + '<i class="icon-refresh"></i>&nbsp;刷新'
                            + '</a>'
                            + '</div><div id="serviceRequestGrid" class="gridContent"></div>');
    
    var element = $("#serviceRequestGrid").kendoGrid({
        dataSource: {
            type: "get",
            dataType: "json",
            transport: {
                read: "/api/service_request_by_user/?format=json&limit=0&" + Math.random()
            },
            parameterMap: function (options) {
                return JSON.stringify(options);
            },
            fields: {
                id: {}, resource_uri: {}, description: {}, approver: {}, last_modify_time: {},  request_parameter: {},
                request_status: {},  request_type: {}, state: {}, status_message: {}, submit_time: {}, submitter: {}
            },
            schema: {
                data: function(data) {//设置显示数据
                    for(var i in data.objects) {
                        data.objects[i].request_status = String((data.objects[i].request_status).request_status_caption);
                        data.objects[i].request_type = String((data.objects[i].request_type).request_type_caption);
                    }
                    return data.objects;
                },
                total:function(data){//设置总数
                    return data.meta.total_count;
                }
            },
            pageSize: 20 //分页每页显示数
        },
        sortable: true,
        reorderable: true,
        columnMenu: true,
        resizable: true,
        pageable: true,
        selectable :"row",
        columns: [
            {
                field: "id",
                title: "编号",
                width: 40
            },
            {
                field: "request_type",
                title: "申请类型",
                width: 80
            },
            {
                field: "description",
                title: "申请描述",
                width: 320
            },
            {
                field: "submit_time",
                title: "申请时间",
                width: 80,
                template: '#= (submit_time) ? formatDate(submit_time) : "none" #'
            },
            {
                field: "request_parameter",
                title: "请求参数",
                width: 320
            },
            {
                field: "status_message",
                title: "状态描述",
                width: 120
            },
            {
                field: "last_modify_time",
                title: "最后修改时间",
                width: 80,
                template: '#= (last_modify_time) ? formatDate(last_modify_time) : "none" #'
            },
            {
                field: "approver",
                title: "审批人",
                width: 60
            }          
        ]
    }).data("kendoGrid");
};
