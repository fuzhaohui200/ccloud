/**
 * 系统日志模块 
 */

var showSystemLog = function() {
    
    // 通过ajax判断用户是否已登录
    $.get("/functionContent/", function(data){
        
        $("#pageContent").html(data); // 将主内容页面content.html加载到index.html 相应div里
        showJQDock();  // 显示左侧菜单栏
        $('#functionContent').html('<div id="functionTitle" class="brand">系统日志</div><div id="functionButton"> </div>'
             + '<div id="functionGrid"> </div>');
        listSystemLog();
    });
};

// 显示系统日志表格
var listSystemLog = function(){
    $("#functionGrid").empty();
    $("#functionGrid").append('<div class="div-button-group" id="divButtonGroup">'
                            + '<a href="javascript:void(0);" onclick="viewSystemLog();" class="btn btn-small btn-info" type="button">'
                            +   '<i class="icon-align-justify"></i>&nbsp;查看记录条目'
                            + '</a>'
                            + '<a href="javascript:void(0);" onclick="listSystemLog();" class="btn btn-small btn-info" type="button">'
                            + '<i class="icon-refresh"></i>&nbsp;刷新'
                            + '</a>'
                            + '</div><div id="systemLogGrid"  class="gridContent"></div>');
    
    $("#systemLogGrid").kendoGrid({
        dataSource: {
            type: "get",
            dataType: "json",
            transport: {
                read: "/api/vioclient_usage_log/?format=json&limit=0&" + Math.random()
            },
            parameterMap: function (options) {
                return JSON.stringify(options);
            },
            schema: {
                data: function(data) {//设置显示数据
                    //for(var i in data.objects) {
                        //data.objects[i].service_ip = String((data.objects[i].service_ip).ip);
                        //data.objects[i].status = String((data.objects[i].status).status);
                    //}
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
                field: "vioclient_user",
                title: "申请用户"
            },
             {
                field: "vioclient_name",
                title: "系统名称"
            },
            {
                field: "vioclient_cpu",
                title: "CPU(个)"
            },                              
            {
                field: "vioclient_mem",
                title: "内存(G)"
            },
            {
                field: "start_date",
                title: "开始时间"
            },
            {
               field: "end_date",
               title: "结束时间" 
            },
            {
               field: "use_days",
               title: "使用天数" 
            }
        ]
    });
};

// 查看系统日志详情
var viewSystemLog = function() {
    var systemLogGrid = $("#systemLogGrid").data("kendoGrid");
    var systemLogGridSelected = systemLogGrid.select(); 
    if(systemLogGridSelected != undefined && systemLogGridSelected.length >0) {
        $("#functionGrid").append("<div id='detailSystemLogWindow'></div>")
        var detailSystemLogWindow = $("#detailSystemLogWindow").kendoWindow({
            title: "查看记录信息",
            modal: true,
            visible: false,
            resizable: true,
            width: 410
        }).data("kendoWindow");
        
        var systemLogTemplate = kendo.template("<div id='systemLog-container'><table><tr><td>编号：</td>"
            + "<td>#= id #</td></tr><tr><td>用户名称：</td><td>#= vioclient_user #</td></tr>"
            + "<tr><td>服务器名称：</td><td>#= vioclient_name #</td></tr>"
            + "<tr><td>CPU(个)：</td><td>#= vioclient_cpu #</td></tr>"
            + "<tr><td>内存(G)：</td><td>#= vioclient_mem #</td></tr>"
            + "<tr><td>开始时间：</td><td>#= start_date #</td></tr>"
            + "<tr><td>结束时间：</td><td>#= end_date #</td></tr>"
            + "<tr><td>使用天数：</td><td>#= use_days #</td></tr></table></div>");
        var dataItem = systemLogGrid.dataItem(systemLogGridSelected[0]);
        detailSystemLogWindow.content(systemLogTemplate(dataItem));
        detailSystemLogWindow.center().open(); 
    } else {
        alert("请选择一条记录！");
        return null;
    }
};


