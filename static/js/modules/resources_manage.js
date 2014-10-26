/**
 * 资源管理模块 
 */

var showResourceManage = function() {
    
    // 通过ajax判断用户是否已登录
    $.get("/functionContent/", function(data){
        
        $("#pageContent").html(data); // 将主内容页面content.html加载到index.html 相应div里
        showJQDock(); // 显示左侧菜单栏
        $('#functionContent').html('<div id="functionTitle" class="brand">资源管理</div><div id="functionButton"> </div>'
             + '<div id="functionGrid"> </div>');
        userAixQuotaVal(); // 显示用户配额使用情况
        managePage();
    });
};

// 显示资源管理
var managePage = function() {
    
    // 查询当前用户
   $.ajax({
       type: "GET",
       url: "/get_username/?format=json&" + Math.random(),
       dataType: "text",
       success: function(data) {
           listUserManages(data);
       } 
    });
};

// 根据用户返回用户所有资源
var listUserManages = function(username){
    $("#functionGrid").empty();
    $("#functionGrid").append('<div class="div-button-group" id="divButtonGroup">'
                    + '<a href="javascript:void(0);" onclick="startServer();" class="btn btn-small btn-info" type="button">'
                    + '<i class="icon-ok"></i>&nbsp;启用'
                    + '</a><a href="javascript:void(0);" onclick="closeServer();" class="btn btn-small btn-info" type="button">'
                    + '<i class="icon-ban-circle"></i>&nbsp;关闭'
                    + '</a><a href="javascript:void(0);" onclick="deleteServer();" class="btn btn-small btn-info" type="button">'
                    + '<i class="icon-trash"></i>&nbsp;回收'
                    + '</a><a href="javascript:void(0);" onclick="restartServer();" class="btn btn-small btn-info" type="button">'
                    + '<i class=" icon-repeat"></i>&nbsp;重启'
                    + '</a>'
                    + '<a href="javascript:void(0);" onclick=listUserManages("'+ username +'"); class="btn btn-small btn-info" type="button">'
                    + '<i class="icon-refresh"></i>&nbsp;刷新'
                    + '</a></div>'
                    + '<div id="manageGrid" class="gridContent"></div>');
    
    var element = $("#manageGrid").kendoGrid({
        dataSource: {
            type: "get",
            dataType: "json",
            transport: {
                read: "/api/vioclient/?belong_to_username=" + username+ "&format=json&limit=0&" + Math.random()
            },
            parameterMap: function (options) {
                return JSON.stringify(options);
            },
            schema: {
                data: function(data) {//设置显示数据
                    for(var i in data.objects) {
                        data.objects[i].service_ip = String((data.objects[i].service_ip).ip);
                        data.objects[i].status = String((data.objects[i].status).status);
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
        pageable: true,
        reorderable: true,
        columnMenu: true,
        resizable: true,
        selectable :"row",
        columns: [
            {
                field: "id",
                title: "编号",
                width: 50
            },
             {
                field: "name",
                title: "系统名",
                width: 150
            },
            {
                field: "service_ip",
                title: "IP地址",
                width: 150
            },                              
            {
                field: "desired_procs",
                title: "CPU",
                width: 100
            },
            {
                field: "desired_mem",
                title: "内存",
                width: 100
            },
            // {
                // field: "resource_uri",
                // title: "资源URI"
            // },
            // {
                // field: "belong_to_username",
                // title: "管理员"
            // }
            {
               field: "status",
               title: "部署状态",
               width: 150 
            }
        ]
    }).data("kendoGrid");
};

// 启动服务器
var startServer = function() {
    var dataItem = selectRowItems();
    if(dataItem != null) {
        var checkServerURL = "/vioclient_operate_available/?vioclient=" + dataItem.name +"&operation=poweron";
        $.ajax({
           type: "GET",
           url: checkServerURL,
           dataType: "text",
           success: function(data) {
               if(data == "allow") {
                   if(confirm("确认要启动服务器吗？")){
                      var model = {"description":"启动AIX分区："+ dataItem.name,
                        "request_type":{"id":"2"},
                        "request_parameter":"{'name':'"+ dataItem.name + "','type':'aix', 'operation':'poweron'}",
                        "request_status":{"id":"1"}
                      };
                      
                      $.ajax({
                         type: "POST",
                         url: "/api/service_request_by_user/?format=json",
                         data: JSON.stringify(model),
                         dataType: "text",
                         processData: false,
                         contentType: 'application/json',
                         success: function(data) {
                            alert("正在启动服务器，请稍候刷新页面查看");
                            setTimeout(managePage, 30000);
                         },
                         timeout:60000
                      }); 
                   }
               } else {
                   alert("当前分区状态不允许此操作！");
               }
           } 
        });
    }
};

// 关闭服务器
var closeServer = function() {
    var dataItem = selectRowItems();
    if(dataItem != null) {
        var checkServerURL = "/vioclient_operate_available/?vioclient=" + dataItem.name + "&operation=poweroff";
        $.ajax({
           type: "GET",
           url: checkServerURL,
           dataType: "text",
           success: function(data) {
               if(data == "allow") {
                    if(confirm("确认要关闭此服务器吗？")){
                      var model = {"description":"关闭AIX分区："+ dataItem.name,
                        "request_type":{"id":"2"},
                        "request_parameter":"{'name':'"+ dataItem.name + "','type':'aix', 'operation':'poweroff'}",
                        "request_status":{"id":"1"}
                      };
                      
                      $.ajax({
                         type: "POST",
                         url: "/api/service_request_by_user/?format=json",
                         data: JSON.stringify(model),
                         dataType: "text",
                         processData: false,
                         contentType: 'application/json',
                         success: function(data) {
                            alert("正在关闭服务器，请稍候刷新页面查看");
                            setTimeout(managePage, 30000);
                         },
                         timeout:60000
                      }); 
                    }
               } else {
                   alert("当前分区状态不允许此操作！");
               }
           } 
        });
        
    }
};

// 删除服务器
var deleteServer = function() {
    var dataItem = selectRowItems();
    if(dataItem != null) {
        var checkServerURL = "/vioclient_operate_available/?vioclient=" + dataItem.name + "&operation=recycle";
        $.ajax({
           type: "GET",
           url: checkServerURL,
           dataType: "text",
           success: function(data) {
               if(data == "allow") {
                    if(confirm("确认要回收" + dataItem.name +"分区吗？")){
                        if(confirm("请再次确认要回收" + dataItem.name +"分区吗？")){
                            if(confirm("请三次确认要回收" + dataItem.name +"分区吗？")){
                              var model = {"description":"回收AIX分区："+ dataItem.name,
                                "request_type":{"id":"3"},
                                "request_parameter":"{'name':'"+ dataItem.name + "','type':'aix'}",
                                "request_status":{"id":"1"}
                              };
                              
                              $.ajax({
                                 type: "POST",
                                 url: "/api/service_request_by_user/?format=json",
                                 data: JSON.stringify(model), 
                                 dataType: "text",
                                 processData: true,
                                 contentType: 'application/json',
                                 success: function(data) {
                                    alert("正在回收服务器，请稍候刷新页面查看");
                                    setTimeout(managePage, 30000);
                                 },
                                 timeout:60000
                              }); 
                          }
                       }
                   }
               } else {
                   alert("当前分区状态不允许此操作！");
               }
           } 
        });
    }
};

// 重启服务器
var restartServer = function() {
    var dataItem = selectRowItems();
    if(dataItem != null) {
        var checkServerURL = "/vioclient_operate_available/?vioclient=" + dataItem.name + "&operation=reset";
        $.ajax({
           type: "GET",
           url: checkServerURL,
           dataType: "text",
           success: function(data) {
               if(data == "allow") {
                  if(confirm("确认要重新启动服务器吗？")){
                      var model = {"description":"重启AIX分区："+ dataItem.name,
                        "request_type":{"id":"2"},
                        "request_parameter":"{'name':'"+ dataItem.name + "','type':'aix', 'operation':'reset'}",
                        "request_status":{"id":"1"}
                      };
                      
                      $.ajax({
                         type: "POST",
                         url: "/api/service_request_by_user/?format=json",
                         data: JSON.stringify(model),
                         dataType: "text",
                         processData: true,
                         contentType: 'application/json',
                         success: function(data) {
                            alert("正在重新启动服务器，请稍候刷新页面查看");
                            setTimeout(managePage, 30000);
                         },
                         timeout:60000
                      }); 
                  }
               } else {
                   alert("当前分区状态不允许此操作！");
               }
           } 
        });
    }
};

// 返回当前表格选择的某一行数据
var selectRowItems = function() {
    var manageGrid = $("#manageGrid").data("kendoGrid");
    var manageGridSelected = manageGrid.select(); 
    if(manageGridSelected != undefined && manageGridSelected.length >0) {
        return manageGrid.dataItem(manageGridSelected[0]);
    } else {
        alert("请选择一条记录！");
        return null;
    }
};
