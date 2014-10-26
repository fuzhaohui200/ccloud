/**
 * 资源警告模块 
 */

var showResourceWarn = function() {
    
    // 通过ajax判断用户是否已登录
    $.get("/functionContent/", function(data){
        $("#pageContent").html(data); // 将主内容页面content.html加载到index.html 相应div里
        showJQDock();  // 显示左侧菜单栏
        $('#functionContent').html('<div id="functionTitle" class="brand">资源警告</div><div id="functionButton"> </div>'
             + '<div id="functionGrid"> </div>');
        showWarnTab(); // 显示资源警告tab
    });
};

// 资源警告选项卡
var showWarnTab = function(){
    $("#functionGrid").append('<div id="warnTab"></div>');
    $("#warnTab").kendoTabStrip({
       animation: {
        close: {
            duration: 100,
            effects: "fadeOut"
        },
        open: {
            duration: 100,
            effects: "fadeIn"
        }
      },
      dataTextField: "Name",
      dataContentField: "Content",
      dataSource: [{'Name': '待处理', Content: '<div class="tabContent"></div>'},
          {'Name': '已处理', Content: '<div class="tabContent"></div>'},
          {'Name': '已撤消', Content: '<div class="tabContent"></div>'}
      ],
      select: function(e){
        var tabName = $(e.item).text();
        listWarn(tabName);  
      }
   }).data("kendoTabStrip").select(0);
};

// 根据选项卡显示不同的表格数据
var listWarn = function(tabName) {
    if(tabName == '已处理') {
       listHandledWarns();
    }else if(tabName == '已撤消') {
       listRestWarns();
    } else {
       listUnHandledWarns();
    }
};

// 显示已处理完的表格
var listHandledWarns = function(){
    $("#warnTab-2").empty();
    $("#warnTab-2").append('<div class="div-button-group" id="divButtonGroup">'
                            + '<a href="javascript:void(0);" onclick="viewWarn();" class="btn btn-small btn-info" type="button">'
                            +   '<i class="icon-align-justify"></i>&nbsp;查看警告条目'
                            + '</a>'
                            + '<a href="javascript:void(0);" onclick="listHandledWarns();" class="btn btn-small btn-info" type="button">'
                            + '<i class="icon-refresh"></i>&nbsp;刷新'
                            + '</a></div><div id="warnGrid2" class="tabGridContent"></div>');

     $("#warnGrid2").kendoGrid({
        dataSource: {
            type: "get",
            dataType: "json",
            sort: { field: "id", dir: "desc"},
            transport: {
                read: "/api/system_alert/?status__status_id=1&format=json&limit=0&" + Math.random()
            },
            parameterMap: function (options) {
                return JSON.stringify(options);
            },
            schema: {
                data: function(data) {//设置显示数据
                    for(var i in data.objects) {
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
                field: "username",
                title: "申请人",
                width: 100
            },
            {
                field: "request_description",
                title: "申请内容",
                width: 200
            },
            {
                field: "submit_time",
                title: "申请时间",
                template: '#= (submit_time) ? formatDate(submit_time) : "none" #',
                width: 150
            },
            {
                field: "service_request_id",
                title: "服务编号",
                width: 60
            },
            {
                field: "status",
                title: "审批状态",
                width: 100
            },
            {
                field: "last_modify_time",
                title: "最后修改时间",
                template: '#= (last_modify_time) ? formatDate(last_modify_time) : "none" #',
                width: 150
            }          
        ]
    });
};

// 显示未处理表格数据
var listUnHandledWarns = function() {
   $("#warnTab-1").empty();
   $("#warnTab-1").append('<div class="div-button-group" id="divButtonGroup">'
                            + '<a href="javascript:void(0);" onclick="viewWarn();" class="btn btn-small btn-info" type="button">'
                            +   '<i class="icon-align-justify"></i>&nbsp;查看警告条目'
                            + '</a>'
                            + '<a href="javascript:void(0);" onclick="listUnHandledWarns();" class="btn btn-small btn-info" type="button">'
                            +   '<i class="icon-refresh"></i>&nbsp;刷新'
                            + '</a>'
                            + '</div><div id="warnGrid1" class="tabGridContent"></div>');

   $("#warnGrid1").kendoGrid({
        dataSource: {
            type: "get",
            dataType: "json",
            transport: {
                read: "/api/system_alert/?status__status_id=0&format=json&limit=0&" + Math.random()
            },
            parameterMap: function (options) {
                return JSON.stringify(options);
            },
            schema: {
                data: function(data) {
                    for(var i in data.objects) {
                        data.objects[i].status = String((data.objects[i].status).status);
                    }
                    return data.objects;
                },
                total:function(data){
                    return data.meta.total_count;
                }
            },
            pageSize: 20
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
                field: "username",
                title: "申请人",
                width: 100
            },
            {
                field: "request_description",
                title: "申请内容",
                width: 180
            },
            {
                field: "submit_time",
                title: "申请时间",
                template: '#= (submit_time) ? formatDate(submit_time) : "none" #',
                width: 150
            },
            {
                field: "service_request_id",
                title: "服务编号",
                width: 60
            },
            {
                field: "status",
                title: "审批状态",
                width: 100
            },
            {
                field: "last_modify_time",
                title: "审批时间",
                template: '#= (last_modify_time) ? formatDate(last_modify_time) : "none" #',
                width: 150
            },
            {
              command: { text: "处理", click: showWarnHandleWindow}, 
              title: "处理", 
              width: 80
            }
        ]
    });
};

// 显示撤消数据表格
var listRestWarns = function() {
   $("#warnTab-3").empty();
   $("#warnTab-3").append('<div class="div-button-group" id="divButtonGroup">'
                            + '<a href="javascript:void(0);" onclick="viewWarn();" class="btn btn-small btn-info" type="button">'
                            +   '<i class="icon-align-justify"></i>&nbsp;查看警告条目'
                            + '</a>'
                            + '<a href="javascript:void(0);" onclick="listRestWarns();" class="btn btn-small btn-info" type="button">'
                            + '<i class="icon-refresh"></i>&nbsp;刷新'
                            + '</a></div><div id="warnGrid3" class="tabGridContent"></div>');

   $("#warnGrid3").kendoGrid({
        dataSource: {
            type: "get",
            dataType: "json",
            transport: {
                read: "/api/system_alert/?status__status_id=2&format=json&limit=0&" + Math.random()
            },
            parameterMap: function (options) {
                return JSON.stringify(options);
            },
            schema: {
                data: function(data) {
                    for(var i in data.objects) {
                        data.objects[i].status = String((data.objects[i].status).status);
                    }
                    return data.objects;
                },
                total:function(data){
                    return data.meta.total_count;
                }
            },
            pageSize: 20
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
                field: "username",
                title: "申请人",
                width: 100
            },
            {
                field: "request_description",
                title: "申请内容",
                width: 180
            },
            {
                field: "submit_time",
                title: "申请时间",
                template: '#= (submit_time) ? formatDate(submit_time) : "none" #',
                width: 150
            },
            {
                field: "service_request_id",
                title: "服务编号",
                width: 60
            },
            {
                field: "status",
                title: "审批状态",
                width: 100
            },
            {
                field: "last_modify_time",
                title: "审批时间",
                template: '#= (last_modify_time) ? formatDate(last_modify_time) : "none" #',
                width: 150
            }
        ]
    });
};

// 显示资源警告处理窗口
var showWarnHandleWindow = function(e){
    $("#functionContent").append('<div id="operatorWarnWindow"></div>')
    var operatorWarnWindow = $("#operatorWarnWindow").kendoWindow({
        title: "审批服务器申请",
        modal: true,
        visible: false,
        resizable: true,
        width: 450
    }).data("kendoWindow");
    
    var warnTemplate = kendo.template("<div id='warn-container'><table><tr><td>ID：</td><td>#= id #</td></tr><tr>"
        + "<td>申请内容：</td><td><textarea cols='35' rows='5' disabled='disabled'>#= request_description #</textarea></td></tr>"
        + "<tr><td colspan='2'><a class='k-button' href='javascript:void(0);' onclick=handleWarn('#= resource_uri #')>已解决</a>"
        + "<a class='k-button' href='javascript:void(0);' "
        + "onclick=cancelHandleWarn('#= resource_uri #')>取消</a></td></tr></table></div>");
    e.preventDefault();

    var dataItem = this.dataItem($(e.currentTarget).closest("tr"));
    operatorWarnWindow.content(warnTemplate(dataItem));
    operatorWarnWindow.center().open();
};

// 处理资源警告
var handleWarn = function(resource_uri){
    var model = {
        "status": {
            "id": 2, 
            "resource_uri": "/api/system_alert_status/2/", 
            "status_id": 1
        }
    };
    
    $.ajax({
       type: 'PUT',
          url: resource_uri + "?format=json",
          data: JSON.stringify(model), // '{"name":"' + model.name + '"}',
          dataType: 'text',
          processData: false,
          contentType: 'application/json',
          success: function(req, status, ex){
              $("#operatorWarnWindow").data("kendoWindow").destroy(); 
              listUnHandledWarns();
          },
          error: function(req, status, ex) {
              alert("保存失败！");
          },
          timeout:60000
    }); 
};

// 取消处理
var cancelHandleWarn = function(resource_uri){
    $("#operatorWarnWindow").data("kendoWindow").close();
};

// 查看资源警告详情
var viewWarn = function () {
    var tabIndex = $("#warnTab").data("kendoTabStrip").select().index(); 
    var warnGrid;
    if(tabIndex == 0) { // 待处理
        warnGrid = $("#warnGrid1").data("kendoGrid");
    } else if(tabIndex == 1) { // 已处理
       warnGrid =  $("#warnGrid2").data("kendoGrid"); 
    } else { // 已撤消
       warnGrid =  $("#warnGrid3").data("kendoGrid"); 
    }
    var warnGridSelected = warnGrid.select();
    
    // 判断Grid是否选择了数据 
    if (warnGridSelected != undefined && warnGridSelected.length >0) {
        $("#warnTab").append("<div id='detailWarnWindow'></div>")
        var operatorWarnWindow = $("#detailWarnWindow").kendoWindow({
            title: "查看警告信息",
            modal: true,
            visible: false,
            resizable: true,
            width: 450
        }).data("kendoWindow");
        
        var warnTemplate = kendo.template("<div id='warn-container'><table>"
            + "<tr><td>编号：</td><td>#= id #</td></tr>"
            + "<tr><td>服务器名称：</td><td>#= name #</td></tr>"
            + "<tr><td>申请内容：</td><td><textarea cols='35' rows='3' disabled='disabled'>#= request_description #</textarea></td></tr>"
            + "<tr><td>申请时间：</td><td>#= submit_time #</td></tr>"
            + "<tr><td>服务编号：</td><td>#= service_request_id #</td></tr>"
            + "<tr><td>处理状态：</td><td>#= status #</td></tr>"
            + "<tr><td>审批时间：</td><td>#= last_modify_time #</td></tr></table></div>");
        var dataItem = warnGrid.dataItem(warnGridSelected[0]);
        var request_description = eval("(" + dataItem.request_description + ")");
        var itemDetail = {
            "id": dataItem.id,
            "name": request_description.name,
            "request_description": dataItem.request_description,
            "service_request_id": dataItem.service_request_id,
            "status": dataItem.status,
            "submit_time": formatDate(dataItem.submit_time),
            "last_modify_time": formatDate(dataItem.last_modify_time)
        };
        operatorWarnWindow.content(warnTemplate(itemDetail));
        operatorWarnWindow.center().open(); 
    } else   {
        alert("请选择一条记录！");
        return false;
    }
};
