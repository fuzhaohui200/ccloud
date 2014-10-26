/**
 *  通用方法 
 */

// 登录页面获取URL
var getUrlParams =  function() {
  var params = {};
  window.location.search.replace(/[?&]+([^=&]+)=([^&]*)/gi, function(str,key,value) {
    params[key] = value;
  });
 
  return params;
};

// KendoUI格式化日期
var formatDate = function(dateStr) {
    //should return (123)456-7890
    //return kendo.format("({0})-{1}-{2}", piece1, piece2, piece3);
    return kendo.format("{0} {1}", dateStr.substring(0, 10), dateStr.substring(11, 19));
};

// 检查在首页菜单里是否已存在此应用
var checkAppExisted = function(array, obj) {
    for(var n = 0; n < array.length; n++) {
        if(array[n].title == obj.title) {
            return true;
        } 
    }
    return false;
};

// 修改页面窗口
var changePassword = function(){    
    $("#header").append("<div id='changePasswordWindow'></div>");
    changePasswordWindow = $("#changePasswordWindow").kendoWindow( {
        width : 320,
        height : 195,
        visible: false,
        modal: true,
        title : "修改密码", 
        actions : [ "Close" ],
        close : function(e){
            changePasswordWindow.destroy();
        }
    }).data("kendoWindow");
    changePasswordWindow.refresh("/change_passwd_page/");
    changePasswordWindow.center().open();
};

// 注销
var logout = function() {
    $.post("/logout/", function(data){
       window.location='/index/';
    });
};

// 首页菜单
var overview = function() {
    
    // 通过ajax判断用户是否已登录
    $.get("/functionContent/", function(data){
        
        $("#pageContent").html(data); // 将主内容页面content.html加载到index.html 相应div里
        showJQDock(); // 显示左侧菜单栏
        
        $.get("/overview/", function(data) {
           $('#functionContent').html(data);
           
           $.ajax({
               type: "GET",
               url:"/api/NoticeResource/?format=json&limit=0&" + Math.random(),
               dataType: "json",
               success: function(data) {
                   //systemNotice
                   //alert(JSON.stringify(data.objects));
                   for(var i in data.objects) {
                     $("#systemNotice").prepend("<tr height='22px'><td width='25px'><img src='/static/images/overview/notice_index.png'>"
                        + "</td><td width='450px'><a href='javascript:void(0);' onclick=viewNotice('" + data.objects[i].resource_uri + "');>" + data.objects[i].title 
                        + "</a></td><td width='155px'>" + formatDate(data.objects[i].pub_date) +" </td></tr>");
                   }
               } 
           });
       });
   });
};

// 查看系统通知
var viewNotice = function(url) {
    $.ajax({
       type: "GET",
       url: url + "?format=json",
       dataType: "json",
       success: function(data) {
            var detailNoticeWindow = $("#detailNoticeWindow").kendoWindow({
                title: "查看公告内容",
                modal: true,
                visible: false,
                resizable: true,
                width: 610
            }).data("kendoWindow");
            
            var detailNoticeTemplate = kendo.template("<div id='notice-container'><table>"
            	+ "<tr><td width='80px' height='25px'>主题：</td><td>#= title #</td></tr>"
            	+ "<tr><td width='80px'>主要内容：</td><td><span>#= content #</span></td></tr>"
                + "<tr><td width='80px' height='25px'>发布时间：</td><td>#= pub_date #</td></tr></table></div>");
           
            var itemDetail = {
                "title": data.title,
                "content": data.content,
                "pub_date": formatDate(data.pub_date)
            };
            detailNoticeWindow.content(detailNoticeTemplate(itemDetail));
            detailNoticeWindow.center().open(); 
           
       }
   });
};

// 用户配额使用情况进度条
var userAixQuotaVal = function() {
    $.ajax({
       type: 'GET',
       url: "/get_user_aix_quota/?format=json&" + Math.random(),
       success: function(data){
          $("#functionButton").html('<table width="100%"><tr><td>'
            + '<div class="div-resource-cpu resource-used" id="divResourceCpu"><div class="progress progress-striped active">'
            + '<div class="bar bar-info" style="width: '+ data.used.aix_cpu_used/data.quota.aix_cpu_quota*100 +'%;"></div><div class="bar bar-success" style="width: '
            + (data.quota.aix_cpu_quota-data.used.aix_cpu_used)/data.quota.aix_cpu_quota*100 +'%;"></div>'
            + '</div><span class="label label-info">CPU已申请：'+ data.used.aix_cpu_used +'</span><span class="label label-success">CPU配额：'+ data.quota.aix_cpu_quota +'</span></div>'
            + '</td><td><div class="div-resource-memory resource-used" id="divResourceMemory"><div class="progress progress-striped active">'
            + '<div class="bar bar-info" style="width: '+ data.used.aix_mem_used/data.quota.aix_mem_quota*100 +'%;"></div><div class="bar bar-success" style="width: '
            + (data.quota.aix_mem_quota-data.used.aix_mem_used)/data.quota.aix_mem_quota*100 +'%;"></div>'
            + '</div><span class="label label-info">内存已申请：'+ data.used.aix_mem_used +'</span><span class="label label-success">内存配额：'+ data.quota.aix_mem_quota +'</span></div>'
            + '</td><td><div class="div-resource-partition resource-used" id="divResourcePartition"><div class="progress progress-striped active">'
            + '<div class="bar bar-info" style="width: '+ data.used.aix_count_used/data.quota.aix_count_quota*100 +'%;"></div><div class="bar bar-success" style="width: '
            + (data.quota.aix_count_quota-data.used.aix_count_used)/data.quota.aix_count_quota*100 +'%;"></div>'
            + '</div><span class="label label-info">分区已申请：'+ data.used.aix_count_used +'</span><span class="label label-success">分区配额：'+ data.quota.aix_count_quota 
            + '</span></div></td></tr></table>');
       }
    });
};

// 显示左侧菜单
var showJQDock = function() {
   $.ajax({
       type: "GET",
       url: "/get_username/?format=json",
       dataType: "text",
       success: function(data) {
           $("#username").append("欢迎您  " + data + " 登录云服务平台");
       } 
    });
    // 根据用户组显示用户相应的模块
    $.ajax({
       type: 'GET',
       url: "/get_user_groups/?format=json",
       dataType: "text",
       success: function(data) {
           var usergroups = eval("(" + data + ")").group_list;  // 用户所在的用户组
           
           var appsDS = []; // 用户显示的菜单项变量
           
           var logAppObj = {title: "首页", html_template: '<li><a class="dockItem" href="javascript:void(0);" onclick="overview();">'
                + '<img src="/static/images/nav/dock/home-sm.png" alt="Home" title="&nbsp;&nbsp;首&nbsp;&nbsp;页" /></a></li>'};
           if(!checkAppExisted(appsDS, logAppObj)) {
               appsDS.push(logAppObj); 
           }
           // 根据用户所在的用户组数据， 显示将需要显示的菜单装载到数组里面
           for(var i = 0; i < usergroups.length; i++) {
               if(usergroups[i] == "VMwareUser" || usergroups[i] == "aix_user") {
                 var applyAppObj = {title: "申请资源", html_template: '<li><a class="dockItem" href="javascript:void(0);" onclick="showResourceApply()">'
                    + '<img src="/static/images/nav/dock/email-sm.png" alt="Contact" title="资源申请" /></a></li>'};
                 if(!checkAppExisted(appsDS, applyAppObj)) {
                    appsDS.push(applyAppObj);
                 }
                 var serviceRequestAppObj = {title: "服务请求", html_template: '<li><a class="dockItem" href="javascript:void(0);" onclick="showResourceServiceRequest()">'
                    + '<img src="/static/images/nav/dock/calendar-sm.png" alt="portfolio" title="服务请求" /></a></li>'};
                 
                 if(!checkAppExisted(appsDS, serviceRequestAppObj)) {
                    appsDS.push(serviceRequestAppObj);
                 }
                 var manageAppObj = {title: "资源管理", html_template: '<li><a class="dockItem" href="javascript:void(0);" onclick="showResourceManage()">'
                     + '<img src="/static/images/nav/dock/music-sm.png" alt="music" title="资源管理" /></a></li>'};
                 if(!checkAppExisted(appsDS, manageAppObj)) {
                    appsDS.push(manageAppObj);
                 }
               } else if(usergroups[i] == "System Administrator" || usergroups[i] == "Common Administrator") {
                  var approvesAppObj = {title: "资源审批", html_template: '<li><a class="dockItem" href="javascript:void(0);" onclick="showResourceApproves()">'
                     + '<img src="/static/images/nav/dock/link-sm.png" alt="video" title="资源审批" /></a></li>'};
                  if(!checkAppExisted(appsDS, approvesAppObj)) {
                    appsDS.push(approvesAppObj); 
                  }
                  if(usergroups[i] == "System Administrator") {
                    var sysManageAppObj = {title: "系统管理", html_template: '<li><a class="dockItem" href="javascript:void(0);" onclick="showSystemManage()">'
                        + '<img src="/static/images/nav/dock/video-sm.png" alt="history" title="系统管理" /></a></li>'};
                    if(!checkAppExisted(appsDS, sysManageAppObj)) {
                        appsDS.push(sysManageAppObj); 
                    }
                    var warnAppObj = {title: "资源警告", html_template: '<li><a class="dockItem" href="javascript:void(0);" onclick="showResourceWarn()">'
                        + '<img src="/static/images/nav/dock/portfolio-sm.png" alt="calendar" title="资源警告" /></a></li>'};
                    if(!checkAppExisted(appsDS, warnAppObj)) {
                        appsDS.push(warnAppObj); 
                    }
                    
                    var logAppObj = {title: "系统记录", html_template: '<li><a class="dockItem" href="javascript:void(0);" onclick="showSystemLog()">' 
                        + '<img src="/static/images/nav/dock/history-sm.png" alt="links" title="系统记录" /></a></li>'};
                    if(!checkAppExisted(appsDS, logAppObj)) {
                        appsDS.push(logAppObj); 
                    }
                  }
               } 
           }
           $("#jqDock").empty(); // 将左侧菜单先清空
           for(var i in appsDS) {
               $("#jqDock").append(appsDS[i].html_template);
           }
           var jqDockOpts = {align: 'left', duration: 250, labels: 'tc', size: 60, distance: 85};
           $('#jqDock').jqDock(jqDockOpts);
       }
   });
};
