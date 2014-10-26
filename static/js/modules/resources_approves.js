/**
 * 资源审批模块 
 */

var approvesTab, operatorApproverWindow, pendingApproverWindow; // 资源审批选项卡变量 待审批时审批窗口  延迟审批时审批窗口

// 显示资源审批数据
var showResourceApproves = function() {
    // 通过ajax判断用户是否已登录
   $.get("/functionContent/", function(data){
       
        $("#pageContent").html(data);  // 将主内容页面content.html加载到index.html 相应div里
        showJQDock();  // 显示左侧菜单栏
        $('#functionContent').html('<div id="functionTitle" class="brand">资源审批</div><div id="functionButton"> </div>'
             + '<div id="functionGrid"> </div>');
        showApprovesTab(); // 显示审批选项卡
   });
};

// 显示资源审批选项卡
var showApprovesTab = function(){
   $("#functionGrid").append('<div id="approvesTab"></div>')
   approvesTab = $("#approvesTab").kendoTabStrip({
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
      dataSource: [{'Name': '待审批', Content: '<div class="tabContent"></div>'},
          {'Name': '通过', Content: '<div class="tabContent"></div>'},
          {'Name': '拒绝', Content: '<div class="tabContent"></div>'},
          {'Name': '待定', Content: '<div class="tabContent"></div>'}
      ],
      select: function(e) {
            var tabName = $(e.item).text();
            listApproves(tabName);  
      }
   }).data("kendoTabStrip");
   approvesTab.select(0);
};

// 所有不同选项卡审批数据Grid
var listApproves = function(tabName) {
    if(tabName == '通过') {
       listApproved();       
    } else if(tabName == '待审批'){
       listUnApproves();
    } else if(tabName == "拒绝") {
       listRefuseApprovers();
    } else {
        listPendingApproves();
    }
};

// 已通过审批选项卡数据表格
var listApproved = function() {
    $("#approvesTab-2").empty();
    $("#approvesTab-2").append('<div class="div-button-group" id="divButtonGroup">'
                            + '<a href="javascript:void(0);" onclick="viewApproves();" class="btn btn-small btn-info" type="button">'
                            +   '<i class="icon-align-justify"></i>&nbsp;查看资源审批条目'
                            + '</a>'
                            + '<a href="javascript:void(0);" onclick="listApproved();" class="btn btn-small btn-info" type="button">'
                            + '<i class="icon-refresh"></i>&nbsp;刷新'
                            + '</a>'
                            + '</div><div id="approvesGrid2" class="tabGridContent"></div>');
    
    var approvedGrid = $("#approvesGrid2").kendoGrid({
        dataSource: {
            type: "get",
            dataType: "json",
            sort: { field: "id", dir: "desc"},
            transport: {
                read: "/api/approve/?approve_status__approve_status_id=1&format=json&limit=0&" + Math.random()
            },
            parameterMap: function (options) {
                return JSON.stringify(options);
            },
            schema: {
                data: function(data) {//设置显示数据
                    for(var i in data.objects) {
                        data.objects[i].approve_status = String((data.objects[i].approve_status).approve_status_caption);
                        //data.objects[i].request_type = String((data.objects[i].request_type).request_type_caption);
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
                field: "submitter",
                title: "申请人",
                width: 80
            },
            {
                field: "request_description",
                title: "申请描述",
                wdith: 500
            },
            {
                field: "service_request_id",
                title: "服务编号",
                wdith: 50
            },
            {
                field: "submit_time",
                title: "提交时间",
                template: '#= (submit_time) ? formatDate(submit_time) : "none" #',
                width: 150
            },
            {
                field: "approve_status",
                title: "审批状态",
                width: 80
            },                              
            {
                field: "last_modify_time",
                title: "最后修改时间",
                template: '#= (last_modify_time) ? formatDate(last_modify_time) : "none" #',
                width: 150
            },
            {
                field: "approver",
                title: "审批人",
                width: 60
            }
        ]
    }).data("kendoGrid");
};

// 待审批选项卡数据表格显示
var listUnApproves = function() {
    $("#approvesTab-1").empty();
    $("#approvesTab-1").append('<div class="div-button-group" id="divButtonGroup">'
                            + '<a href="javascript:void(0);" onclick="viewApproves();" class="btn btn-small btn-info" type="button">'
                            + '<i class="icon-align-justify"></i>&nbsp;查看资源审批条目'
                            + '</a>'
                            + '<a href="javascript:void(0);" onclick="listUnApproves();" class="btn btn-small btn-info" type="button">'
                            + '<i class="icon-refresh"></i>&nbsp;刷新'
                            + '</a>'
                            + '</div><div id="approvesGrid1" class="tabGridContent" ></div>');
    
    var unApprovesGrid = $("#approvesGrid1").kendoGrid({
        dataSource: {
            type: "get",
            dataType: "json",
            transport: {
                read: "/api/approve/?approve_status__approve_status_id=0&format=json&limit=0&" + Math.random()
            },
            parameterMap: function (options) {
                return JSON.stringify(options);
            },
            schema: {
                data: function(data) {//设置显示数据
                    for(var i in data.objects) {
                        data.objects[i].approve_status = String((data.objects[i].approve_status).approve_status_caption);
                        //data.objects[i].request_type = String((data.objects[i].request_type).request_type_caption);
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
                field: "submitter",
                title: "申请人",
                width: 80
            },
            {
                field: "request_description",
                title: "申请描述",
                wdith: 500
            },
            {
                field: "service_request_id",
                title: "服务编号",
                wdith: 50
            },
            {
                field: "submit_time",
                title: "提交时间",
                template: '#= (submit_time) ? formatDate(submit_time) : "none" #',
                width: 150
            },
            {
                field: "approve_status",
                title: "审批状态",
                width: 80
            },                              
            {
                field: "last_modify_time",
                title: "最后修改时间",
                template: '#= (last_modify_time) ? formatDate(last_modify_time) : "none" #',
                width: 150
            },
            {
                field: "approver",
                title: "审批人",
                width: 60
            },
            {
              command: { text: "审批", click: showApproverWindow}, title: "审批", width: "150px" 
            }
        ]
    }).data("kendoGrid");
};

// 推迟审批选项卡数据表格显示
var listPendingApproves = function() {
    $("#approvesTab-4").empty();
    $("#approvesTab-4").append('<div class="div-button-group" id="divButtonGroup">'
                            + '<a href="javascript:void(0);" onclick="viewApproves();" class="btn btn-small btn-info" type="button">'
                            + '<i class="icon-align-justify"></i>&nbsp;查看资源审批条目'
                            + '</a>'
                            + '<a href="javascript:void(0);" onclick="listPendingApproves();" class="btn btn-small btn-info" type="button">'
                            + '<i class="icon-refresh"></i>&nbsp;刷新'
                            + '</a>'
                            + '</div><div id="approvesGrid4" class="tabGridContent"></div>');
    
    var pendingApprovesGrid = $("#approvesGrid4").kendoGrid({
        dataSource: {
            type: "get",
            dataType: "json",
            transport: {
                read: "/api/approve/?approve_status__approve_status_id=3&format=json&limit=0&" + Math.random()
            },
            parameterMap: function (options) {
                return JSON.stringify(options);
            },
            schema: {
                data: function(data) {//设置显示数据
                    for(var i in data.objects) {
                        data.objects[i].approve_status = String((data.objects[i].approve_status).approve_status_caption);
                        //data.objects[i].request_type = String((data.objects[i].request_type).request_type_caption);
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
                field: "submitter",
                title: "申请人",
                width: 80
            },
            {
                field: "request_description",
                title: "申请描述",
                wdith: 500
            },
            {
                field: "service_request_id",
                title: "服务请求编号",
                wdith: 50
            },
            {
                field: "submit_time",
                title: "提交时间",
                width: 120,
                template: '#= (submit_time) ? formatDate(submit_time) : "none" #'
            },
            {
                field: "approve_status",
                title: "审批状态",
                width: 80
            },                              
            {
                field: "last_modify_time",
                title: "最后修改时间",
                width: 120,
                template: '#= (last_modify_time) ? formatDate(last_modify_time) : "none" #'
            },
            // {
                // field: "resource_uri",
                // title: "资源URI",
                // width: 80
            // },
            {
                field: "approver",
                title: "审批人",
                width: 60
            },
            {
              command: { text: "审批", click: showPendingApproverWindow}, title: "审批", width: "150px" 
            }
        ]
    }).data("kendoGrid");
};

// 审批拒绝选择卡数据表格显示
var listRefuseApprovers = function() {
    $("#approvesTab-3").empty();
    $("#approvesTab-3").append('<div class="div-button-group" id="divButtonGroup">'
                            + '<a href="javascript:void(0);" onclick="viewApproves();" class="btn btn-small btn-info" type="button">'
                            +   '<i class="icon-align-justify"></i>&nbsp;查看资源审批条目'
                            + '</a>'
                            + '<a href="javascript:void(0);" onclick="listRefuseApprovers();" class="btn btn-small btn-info" type="button">'
                            + '<i class="icon-refresh"></i>&nbsp;刷新'
                            + '</a>'
                            + '</div><div id="approvesGrid3" class="tabGridContent"></div>');
    
    var refuseApprovesGrid = $("#approvesGrid3").kendoGrid({
        dataSource: {
            type: "get",
            dataType: "json",
            sort: { field: "id", dir: "desc"},
            transport: {
                read: "/api/approve/?approve_status__approve_status_id=2&format=json&limit=0&" + + Math.random()
            },
            parameterMap: function (options) {
                return JSON.stringify(options);
            },
            schema: {
                data: function(data) {//设置显示数据
                    for(var i in data.objects) {
                        data.objects[i].approve_status = String((data.objects[i].approve_status).approve_status_caption);
                        //data.objects[i].request_type = String((data.objects[i].request_type).request_type_caption);
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
                field: "submitter",
                title: "申请人",
                width: 80
            },
            {
                field: "request_description",
                title: "申请描述",
                wdith: 500
            },
            {
                field: "service_request_id",
                title: "服务请求编号",
                wdith: 50
            },
            {
                field: "submit_time",
                title: "提交时间",
                template: '#= (submit_time) ? formatDate(submit_time) : "none" #',
                width: 120
            },
            {
                field: "approve_status",
                title: "审批状态",
                width: 80
            },                              
            {
                field: "last_modify_time",
                title: "最后修改时间",
                template: '#= (last_modify_time) ? formatDate(last_modify_time) : "none" #',
                width: 120,
            },
            // {
                // field: "resource_uri",
                // title: "资源URI",
                // width: 80
            // },
            //{
              //  field: "service_request_id",
                //title: "服务编号",
                //width: 60
            //},
            {
                field: "approver",
                title: "审批人",
                width: 60
            }
        ]
    }).data("kendoGrid");
};

// 待审批操作窗口
var showApproverWindow = function(e) {
    $("#functionGrid").append('<div id="operatorApproverWindow"></div>');
    operatorApproverWindow = $("#operatorApproverWindow").kendoWindow({
        title: "审批服务器申请",
        modal: true,
        visible: false,
        resizable: true,
        width: 450
    }).data("kendoWindow");
    
    var approverTemplate = kendo.template("<div id='approves-container'><table>"
        +"<tr><td>申请人：</td><td>#= submitter #</td></tr>"
        + "<tr><td>申请内容：</td><td><textarea cols='35' rows='5' disabled='disabled'>#= request_description #</textarea></td></tr>"
        + "<tr><td colspan='2'>"
        + "<a class='k-button' href='javascript:void(0);' onclick=acceptApprover('#= resource_uri #')>同意</a>"
        + "<a class='k-button' href='javascript:void(0);' onclick=refuseApprover('#= resource_uri #')>拒绝</a>"
        + "<a class='k-button' href='javascript:void(0);' onclick=suspendApprover('#= resource_uri #')>挂起</a>"
        + "</td></tr></table></div>");
    e.preventDefault();

    var dataItem = this.dataItem($(e.currentTarget).closest("tr"));
    operatorApproverWindow.content(approverTemplate(dataItem));
    operatorApproverWindow.center().open();
};

// 推迟审批操作窗口
var showPendingApproverWindow = function(e) {
    $("#functionGrid").append('<div id="pendingApproverWindow"></div>');
    pendingApproverWindow = $("#pendingApproverWindow").kendoWindow({
        title: "审批服务器申请",
        modal: true,
        visible: false,
        resizable: true,
        width: 450
    }).data("kendoWindow");
    
    var pendingApproverTemplate = kendo.template("<div id='approves-container'><table>"
        + "<tr><td>申请人：</td><td>#= submitter #</td></tr>"
        + "<tr><td>申请内容：</td><td><textarea cols='35' rows='5' disabled='disabled'>#= request_description #</textarea></td></tr>"
        + "<tr><td colspan='2'>"
        + "<a class='k-button' href='javascript:void(0);' onclick=acceptApprover('#= resource_uri #')>同意</a>"
        + "<a class='k-button' href='javascript:void(0);' onclick=refuseApprover('#= resource_uri #')>拒绝</a>"
        + "</td></tr></table></div>");
    e.preventDefault();

    var dataItem = this.dataItem($(e.currentTarget).closest("tr"));
    pendingApproverWindow.content(pendingApproverTemplate(dataItem));
    pendingApproverWindow.center().open();
};


/*
 *  接受审批通过操作
 */
var acceptApprover = function(resource_uri){
    var model = {
       "approve_status":
       {
           "id": 2,
           "resource_uri": "/api/ApproveStatus/2/"
       }
    }
    
    $.ajax({
       type: 'PUT',
          url: resource_uri + "?format=json",
          data: JSON.stringify(model), // '{"name":"' + model.name + '"}',
          dataType: 'text',
          processData: false,
          contentType: 'application/json',
          success: function(req, status, ex){
              var tabIndex = approvesTab.select().index();
              if(tabIndex == 0) {
                  operatorApproverWindow.destroy();
                  listUnApproves();
              } else {
                  pendingApproverWindow.destroy(); 
                  listPendingApproves();
              }
          },
          error: function(req, status, ex) {
              alert("保存失败！");
          },
          timeout:60000
    });
};


/*
 * 拒绝审批不通过操作
 */
var refuseApprover = function(resource_uri) {
    var model = {
       "approve_status":
       {
           "id": 3,
           "resource_uri": "/api/ApproveStatus/3/"
       }
    }
    
    $.ajax({
       type: 'PUT',
          url: resource_uri + "?format=json",
          data: JSON.stringify(model), // '{"name":"' + model.name + '"}',
          dataType: 'text',
          processData: false,
          contentType: 'application/json',
          success: function(req, status, ex){
             var tabIndex = approvesTab.select().index();
             if(tabIndex == 0) {
                operatorApproverWindow.destroy();
                listUnApproves();
             } else {
                pendingApproverWindow.destroy(); 
                listPendingApproves();
             }
          },
          error: function(req, status, ex) {
              alert("保存失败！");
          },
          timeout:60000
    });
};


/*
 * 挂起审批不通过操作
 */
var suspendApprover = function(resource_uri) {
    var model = {
       "approve_status":
       {
           "id": 4,
           "resource_uri": "/api/ApproveStatus/4/"
       }
    }
    
    $.ajax({
       type: 'PUT',
          url: resource_uri + "?format=json",
          data: JSON.stringify(model), // '{"name":"' + model.name + '"}',
          dataType: 'text',
          processData: false,
          contentType: 'application/json',
          success: function(req, status, ex){
             var tabIndex = approvesTab.select().index();
             if(tabIndex == 0) {
                operatorApproverWindow.destroy();
                listUnApproves();
             } else {
                pendingApproverWindow.destroy(); 
                listPendingApproves();
             }
          },
          error: function(req, status, ex) {
              alert("保存失败！");
          },
          timeout:60000
    });
};

// 查看审批详细信息
var viewApproves = function () {
    var tabIndex = approvesTab.select().index(); // 获取当前选择的tab
    var approvesGridSelected, operatorApprovesWindow, approvesGrid;
    // 当前选择的选项卡是待审批
    if(tabIndex == 0) {
        $("#functionGrid").append("<div id='detailUnApprovesWindow'></div>");
        approvesGrid = $("#approvesGrid1").data("kendoGrid");
        approvesGridSelected = approvesGrid.select();
        operatorApprovesWindow = $("#detailUnApprovesWindow").kendoWindow({
            title: "查看审批信息",
            modal: true,
            visible: false,
            resizable: true,
            width: 450
        }).data("kendoWindow");
        
    } else if(tabIndex == 1) {  // 已通过审批选择卡
        
        $("#functionGrid").append("<div id='detailApprovedWindow'></div>");
        approvesGrid = $("#approvesGrid2").data("kendoGrid");
        approvesGridSelected = approvesGrid.select();
        operatorApprovesWindow = $("#detailApprovedWindow").kendoWindow({
            title: "查看审批信息",
            modal: true,
            visible: false,
            resizable: true,
            width: 450
        }).data("kendoWindow"); 
        
    } else if(tabIndex == 2) { // 拒绝审批选项卡
        
        $("#functionGrid").append("<div id='detailRefuseApprovesWindow'></div>");
        approvesGrid = $("#approvesGrid3").data("kendoGrid");
        approvesGridSelected = approvesGrid.select();
        operatorApprovesWindow = $("#detailRefuseApprovesWindow").kendoWindow({
            title: "查看审批信息",
            modal: true,
            visible: false,
            resizable: true,
            width: 450
        }).data("kendoWindow"); 
        
    } else { // 推迟审批选项卡
        
       $("#functionGrid").append("<div id='detailPendingApprovesWindow'></div>");
       approvesGrid = $("#approvesGrid4").data("kendoGrid");
       approvesGridSelected = approvesGrid.select();
       operatorApprovesWindow = $("#detailPendingApprovesWindow").kendoWindow({
            title: "查看审批信息",
            modal: true,
            visible: false,
            resizable: true,
            width: 450
        }).data("kendoWindow");  
    }
    
    // 判断是否选择表的某条数据
    if (approvesGridSelected != undefined && approvesGridSelected.length >0) {
        
        var approvesTemplate = kendo.template("<div id='approves-container'><table>"
            + "<tr><td>编号：</td><td>#= id #</td></tr>"
            + "<tr><td>申请人：</td><td>#= submitter #</td></tr>"
            + "<tr><td>申请内容：</td><td><textarea cols='35' rows='3' disabled='disabled'>#= request_description #</textarea></td></tr>"
            + "<tr><td>申请时间：</td><td>#= submit_time #</td></tr>"
            + "<tr><td>服务编号：</td><td>#= service_request_id #</td></tr>"
            + "<tr><td>审批状态：</td><td>#= approve_status #</td></tr>"
            + "<tr><td>审批人：</td><td>#= approver #</td></tr>"
            + "<tr><td>最后修改时间：</td><td>#= last_modify_time #</td></tr></table></div>");
        var dataItem = approvesGrid.dataItem(approvesGridSelected[0]);
        if(dataItem.approver == null) {
            dataItem.approver = "无";
        }
        var itemDetail = {
            "id": dataItem.id,
            "submitter": dataItem.submitter,
            "request_description": dataItem.request_description,
            "submit_time": formatDate(dataItem.submit_time),
            "service_request_id": dataItem.service_request_id,
            "approve_status": dataItem.approve_status,
            "approver": dataItem.approver,
            "last_modify_time": formatDate(dataItem.last_modify_time)
        };
        operatorApprovesWindow.content(approvesTemplate(itemDetail));
        operatorApprovesWindow.center().open(); 
    } else   {
        alert("请选择一条记录！");
        return false;
    }
};