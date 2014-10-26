/**
 * 系统管理模块 
 */

var showSystemManage = function() {
    
    // 通过ajax判断用户是否已登录
    $.get("/functionContent/", function(data){
        
        $("#pageContent").html(data); // 将主内容页面content.html加载到index.html 相应div里
        showJQDock(); // 显示左侧菜单栏
        $('#functionContent').html('<div id="functionTitle" class="brand">系统管理</div><div id="functionButton"> </div>'
             + '<div id="functionGrid"> </div>');
        listSysManages();
    });
};

// 显示系统管理
var listSysManages = function(){
    $("#functionGrid").empty();
    $("#functionGrid").append('<div class="div-button-group" id="divButtonGroup">'
                    + '<a href="javascript:void(0);" onclick="startSystemServer();" class="btn btn-small btn-info" type="button">'
                    + '<i class="icon-ok"></i>&nbsp;启用'
                    + '</a><a href="javascript:void(0);" onclick="closeSystemServer();" class="btn btn-small btn-info" type="button">'
                    + '<i class="icon-ban-circle"></i>&nbsp;关闭'
                    + '</a><a href="javascript:void(0);" onclick="deleteSystemServer();" class="btn btn-small btn-info" type="button">'
                    + '<i class="icon-trash"></i>&nbsp;回收'
                    + '</a><a href="javascript:void(0);" onclick="restartSystemServer();" class="btn btn-small btn-info" type="button">'
                    + '<i class=" icon-repeat"></i>&nbsp;重启'
                    + '</a>'
                    + '<a href="javascript:void(0);" onclick="listSysManages();" class="btn btn-small btn-info" type="button">'
                    + '<i class="icon-refresh"></i>&nbsp;刷新'
                    + '</a></div>'
                    + '<div id="sysManageGrid" class="gridContent"></div>');
    
    var element = $("#sysManageGrid").kendoGrid({
        dataSource: {
            type: "get",
            dataType: "json",
            transport: {
                read: "/api/vioclient/?format=json&limit=0&" + Math.random()
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
                title: "编号"
            },
            {
                field: "belong_to_username",
                title: "所属用户"
            },
             {
                field: "name",
                title: "系统名"
            },
            {
                field: "service_ip",
                title: "IP地址"
            },                              
            {
                field: "desired_procs",
                title: "CPU"
            },
            {
                field: "desired_mem",
                title: "内存"
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
               title: "部署状态" 
            }
        ]
    }).data("kendoGrid");
};

// 启动系统服务器
var startSystemServer = function() {
    var dataItem = selectSysManageRowItems();
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
                            setTimeout(listSysManages, 30000);
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

// 关闭系统服务器
var closeSystemServer = function() {
    var dataItem = selectSysManageRowItems();
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
                            setTimeout(listSysManages, 30000);
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

// 删除系统服务器
var deleteSystemServer = function() {
    var dataItem = selectSysManageRowItems();
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
                                    setTimeout(listSysManages, 30000);
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

// 重启系统服务器
var restartSystemServer = function() {
    var dataItem = selectSysManageRowItems();
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
                            setTimeout(listSysManages, 30000);
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

// 返回当表格前选择数据
var selectSysManageRowItems = function() {
    var sysManageGrid = $("#sysManageGrid").data("kendoGrid");
    var sysManageGridSelected = sysManageGrid.select(); 
    if(sysManageGridSelected != undefined && sysManageGridSelected.length >0) {
        return sysManageGrid.dataItem(sysManageGridSelected[0]);
    } else {
        alert("请选择一条记录！");
        return null;
    }
};


