/**
 *  资源申请模块
 */

// 显示资源申请
var showResourceApply = function() {
    
    // 通过ajax判断用户是否已登录
    $.get("/functionContent/", function(data){
        
        $("#pageContent").html(data); // 将主内容页面content.html加载到index.html 相应div里
        showJQDock(); // 显示左侧菜单栏
        $('#functionContent').html('<div id="functionTitle" class="brand">资源申请</div><div id="functionButton"> </div>'
            + '<div id="functionGrid"> </div>');
        userAixQuotaVal();  // 显示用户当前配额使用情况
        applyPage();  // 显示后面申请页面需要填写内容
    });
};

var cpuSlider, memorySlider, hdiskAmountSlider;

// 显示申请页面需要填写的内容
var applyPage =  function () {
    $("#functionGrid").empty();
    $("#functionGrid").append("<div><table>"
           + "<tr><td width='120px' height='45px'>系统名称:</td><td><input type='text' id='name' name='name' onblur='validateName()'><span id='validateNameSpan'></span></td></tr>"
           + "<tr><td width='120px' height='45px'>操作系统:</td><td><select id='os' name='os' width='200'></select></td></tr>"
           + "<tr><td width='120px' height='45px'>版本:</td><td><select id='version' name='version' width='200'></select></td></tr>"
           + "<tr id='model_tr'><td width='120px' height='45px'>配置:</td><td><input id='commonModel' name='partitionModel' type='radio' checked='checked' value='commonModel' "
           + "onclick='javascript:partitionModel();'>普通模式 &nbsp;&nbsp;&nbsp;&nbsp;<input id='advanceModel' name='partitionModel' type='radio' value='advanceModel' "
           + "onclick='javascript:partitionModel();'>高级模式</tr>"
           + "<tr><td valign='middle' width='120px' height='90px'>硬件配置:</td><td valign='middle'>"
           + "<table><tr><td width='70px' height='45px'>磁盘数:(个)</td><td width='450px'><input id='hdisk_amount' class='temperature' style='width:440px;'/></td>"
           + "<td><input id='hdisk_amount_value' name='hdisk_amount_value' type='text' disabled='disabled' value='1' style='width:35px;'/></td></tr>"
           + "<tr><td width='70px' height='45px'>CPU:(个) </td><td width='450px'><input id='cpu' class='temperature' style='width:440px;'/></td>"
           + "<td><input id='cpu_value' name='cpu_value' type='text' disabled='disabled' value='1' style='width:35px;'/></td></tr>"
           + "<tr><td width='45px' height='70px'>内存：(G) </td><td width='450px'><input id='memory' class='temperature'  style='width:440px;'/></td>"
           + "<td><input id='memory_value' name='memory_value' type='text' disabled='disabled' value='2' style='width:35px;'/></td></tr></table></td></tr>"
           + "<tr><td height='45px'><input id='appleBtn' type='button' value='提交' onclick='saveApply()'/></td><td></td></tr>"
           + "</table></div>");
           
    // CPU 滑块
    cpuSlider = $("#cpu").kendoSlider({
        change: cpuSliderOnChange,
        slide: cpuSliderOnSlide,
        min: 0,
        max: 16,
        smallStep: 1,
        largeStep: 4,
        value: 1
    }).data("kendoSlider");
    
    // 内存 滑块
    memorySlider = $("#memory").kendoSlider({
        change: memorySliderOnChange,
        slide: memorySliderOnSlide,
        min: 0,
        max: 16,
        smallStep: 1,
        largeStep: 2,
        value: 2
    }).data("kendoSlider");
    
    // 磁盘数 滑块
    hdiskAmountSlider = $("#hdisk_amount").kendoSlider({
        change: hdiskAmountSliderOnChange,
        slide: hdiskAmountSliderOnSlide,
        min: 1,
        max: 10,
        smallStep: 1,
        largeStep: 1,
        value: 1
    }).data("kendoSlider");
    
    // 系统下拉
    var osComboBox = $("#os").kendoDropDownList({
        dataTextField: "text",
        dataValueField: "value",
        dataSource: [
            { text: "AIX", value: "AIX" },
            { text: "Linux", value: "Linux" },
            { text: "Windows Server 2003", value: "Windows Server 2003" }
        ],
        select: function(e) {
            var dataItem = this.dataItem(e.item.index());
            if(dataItem.text == "Linux" || dataItem.text == "Windows Server 2003") {
                alert("暂不支持"　+　dataItem.text + "系统");
                osComboBox.index(0);
            }
        },
        filter: "contains",
        suggest: true,
        index: 0
    }).data("kendoDropDownList");
    
    
    // 版本下拉框
    $.ajax({
       type: 'GET',
       url: "/api/aix_version/?format=json",
       success: function(data){
          var dataSource = [];
          $.each(data.objects, function(key, val){
              dataSource.push({text: val.version, value: val.version});
          });
          
          $("#version").kendoDropDownList({
            dataTextField: "text",
            dataValueField: "value",
            dataSource: dataSource,
            filter: "contains",
            suggest: true,
            index: 0
        });
       }
    });
    // 普通模式与高级模式动态切换
    partitionModel();
};

// 普通模式与高级模式动态切换
var partitionModel = function() {
    var partitionModel = $("input[name='partitionModel']:checked").val();
    // 高级模式
    if(partitionModel == "advanceModel") {
        var manageVlanIPTr = $("#manageVlanIP_tr");
        var serviceVlanIPTr = $("#serviceVlanIP_tr");
        var hdiskTypeTr = $("#hdiskType_tr");
        var vioclientTypeTr = $("#vioclient_type_tr");
        if(vioclientTypeTr != undefined) {
            vioclientTypeTr.remove();
        }
        if(manageVlanIPTr != undefined) {
           manageVlanIPTr.remove();
        }
        if(serviceVlanIPTr != undefined) {
            serviceVlanIPTr.remove();
        }
        if(hdiskTypeTr != undefined) {
            hdiskTypeTr.remove();
        }
        
        // 实现在table指定位置动态添加
        $("#model_tr").after("<tr id='manageVlanIP_tr'><td width='120px' height='45px'>管理IP VLAN:</td>"
            + "<td><select id='manageVlanIP' name='manageVlanIP' width='200'></select></td></tr>"
            + "<tr id='serviceVlanIP_tr'><td width='120px' height='45px'>服务IP VLAN:</td>"
            + "<td><select id='serviceVlanIP' name='serviceVlanIP' width='200'></select></td></tr>"
            + "<tr id='hdiskType_tr'><td width='120px' height='45px'>Hdisk类型:</td>"
            + "<td><select id='hdiskType' name='hdiskType' width='200'></select></td></tr>");
        
       // 管理IP VLAN
       $.ajax({
           type: 'GET',
           url: "/api/aix_vlan?type__id=1&format=json",
           success: function(data){
              var dataSource = [];
              $.each(data.objects, function(key, val){
                  dataSource.push({text: val.name, value: val.id});
              });
              
              $("#manageVlanIP").kendoDropDownList({
                  dataTextField: "text",
                  dataValueField: "value",
                  dataSource: dataSource,
                  filter: "contains",
                  suggest: true,
                  index: 0
              });
           }
       }); 
       
       // 服务IP VLAN  
       $.ajax({
           type: 'GET',
           url: "/api/aix_vlan?type__id=2&format=json",
           success: function(data){
              var dataSource = [];
              $.each(data.objects, function(key, val){
                  dataSource.push({text: val.name, value: val.id});
              });
            
              $("#serviceVlanIP").kendoDropDownList({
                  dataTextField: "text",
                  dataValueField: "value",
                  dataSource: dataSource,
                  filter: "contains",
                  suggest: true,
                  index: 0
              });
           }
        }); 
        
        // Hdisk类型数据动态加载
        $.ajax({
           type: 'GET',
           url: "/api/aix_hdisk_type?format=json",
           success: function(data){
              var dataSource = [];
              $.each(data.objects, function(key, val){
                  dataSource.push({text: val.name, value: val.id});
              });
              
              $("#hdiskType").kendoDropDownList({
                dataTextField: "text",
                dataValueField: "value",
                dataSource: dataSource,
                filter: "contains",
                suggest: true,
                index: 0
            });
           }
        }); 
        
    // 普通模式
    } else {
        var manageVlanIPTr = $("#manageVlanIP_tr");
        var serviceVlanIPTr = $("#serviceVlanIP_tr");
        var hdiskTypeTr = $("#hdiskType_tr");
        var vioclientTypeTr = $("#vioclient_type_tr");
        if(vioclientTypeTr != undefined) {
            vioclientTypeTr.remove();
        }
        if(manageVlanIPTr != undefined) {
           manageVlanIPTr.remove();
        }
        if(serviceVlanIPTr != undefined) {
            serviceVlanIPTr.remove();
        }
        if(hdiskTypeTr != undefined) {
            hdiskTypeTr.remove();
        }
        
        // 在选择模式后面动态添加相应参数下接框
        $("#model_tr").after("<tr id='vioclient_type_tr'><td width='120px' height='45px'>系统类型:</td>"
            + "<td><select id='vioclient_type' name='vioclient_type' width='200'></select></td></tr>");
        
        // 系统类型
        $.ajax({
           type: 'GET',
           url: "/api/aix_vioclient_type?format=json",
           success: function(data){
              var dataSource = [];
              $.each(data.objects, function(key, val){
                  dataSource.push({text: val.name, value: val.id});
              });
              //alert(JSON.stringify(dataSource));
              $("#vioclient_type").kendoDropDownList({
                dataTextField: "text",
                dataValueField: "value",
                dataSource: dataSource,
                filter: "contains",
                suggest: true,
                index: 0
            });
           }
        }); 
    }
};

var cpuSliderOnSlide = function(e) {
    //kendoConsole.log("Slide :: new slide value is: " + e.value);
    
};

// CPU滑块变化时将值赋到后面输入框里
var cpuSliderOnChange = function (e) {
    //kendoConsole.log("Change :: new value is: " + e.value);
    if(e.value == 0) {
        alert("CPU最小个数不能小于1");
        setTimeout(setCpuValue, 300);
        $("#cpu_value").val(1);
    } else {
        $("#cpu_value").val(e.value);
    }
};

// 设置CPU滑块默认值为1
var setCpuValue = function() {
    cpuSlider.value(1);
};


var memorySliderOnSlide = function(e) {
    //kendoConsole.log("Slide :: new slide value is: " + e.value);
    
};

// 内存滑块变化时将值赋到后面输入框里
var memorySliderOnChange = function (e) {
    //kendoConsole.log("Change :: new value is: " + e.value);
    if(e.value == 0) {
        alert("内存最小数量不能小于1");
        setTimeout(setMemoryValue, 300);
        $("#memory_value").val(1);
    } else {
        $("#memory_value").val(e.value);
    }
    
};

// 设置内存滑块默认值为1
var setMemoryValue = function() {
    memorySlider.value(1);
};

var hdiskAmountSliderOnSlide = function(e) {
    //kendoConsole.log("Slide :: new slide value is: " + e.value);
    
};

// 磁盘数滑块变化时将值赋到后面输入框里
var hdiskAmountSliderOnChange = function (e) {
    //kendoConsole.log("Change :: new value is: " + e.value);
    $("#hdisk_amount_value").val(e.value);
    
};

// 验证输入的系统名
var validateName = function() {
    var name = $("#name").val();
    if(name != "" && (/^[_!\n\w]{4,8}$/.test(name))  && name.indexOf(" ") == -1) {
        $("#validateNameSpan").html("<font color='green'>输入系统名称正确</font>");
        return true;
    } else if (name==""){
        $("#validateNameSpan").html("<font color='red'>系统名称不能为空，请重新输入！输入格式：4-8位[字母、下划线、数字组成]</font>");
        return false;
    } else {
        $("#validateNameSpan").html("<font color='red'>系统名称不符合规范，请重新输入！输入格式：4-8位[字母、下划线、数字组成]</font>");
        return false;
    }
};

// 保存提交资源申请
var saveApply = function() {
    
    $("#appleBtn").attr('disabled',"true"); // 禁止再次提交按钮
    
    var name = $("#name").val(); // 系统名
    var os = $("#os").val(); // 系统类型
    var os_version = $("#version").val(); // 系统版本
    var cpu = $("#cpu_value").val(); // CPU数量
    var memory = $("#memory_value").val(); // 内存数量
    var hdisk_amount = $("#hdisk_amount_value").val();  // 磁盘数量
    
    var request_parameter; // 组合资源申请需要提交参数变量 
    
    var partitionModel = $("input[name='partitionModel']:checked").val(); //获取模式类型
    
    // 如果是高级模式
    if(partitionModel == "advanceModel") {
        var manageVlanIP = $("#manageVlanIP").val(); // 管理Vlan IP
        var serviceVlanIP = $("#serviceVlanIP").val(); // 服务Vlan IP
        var hdiskType = $("#hdiskType").val(); // 磁盘数
        request_parameter = "{'mode':'expert', 'name':'"+ name +"','type':'aix','cpu':" + cpu +",'mem':" + memory 
            + ",'os_type':'" + os_version + "', 'hdisk_amount':'"+ hdisk_amount + "','manage_vlan_item_id':'" + manageVlanIP 
            + "','service_vlan_item_id':'" + serviceVlanIP + "','hdisk_type_id':'" + hdiskType +"'}";
    
    } else {
        // 普通模式
        
        var vioclient_type = $("#vioclient_type").val(); // 系统类型
        request_parameter = "{'mode':'common', 'name':'"+ name +"','type':'aix','cpu':" + cpu +",'mem':" + memory 
            + ",'os_type':'" + os_version + "', 'vioclient_type':'" + vioclient_type + "', 'hdisk_amount':'" + hdisk_amount + "'}"; 
    }
    
    var model = {
	   "description": '申请'+os+'分区:'+name+',cpu:'+cpu+',内存:'+memory+'G,版本:'+os_version,
       "request_type": {"id": "1"},
       "request_parameter": request_parameter,
       "request_status": {"id": "1"}
    };
    
    // 验证系统名是否正确
    if(validateName()) {
        $.ajax({
              type: 'POST',
              url: "/api/service_request_by_user/?format=json",
              data: JSON.stringify(model), // '{"name":"' + model.name + '"}',
              dataType: 'text',
              processData: false,
              contentType: 'application/json',
              success: function(req, status, ex){
                  alert("申请成功");
                  showResourceServiceRequest();
              },
              error: function(req, status, ex) {
                alert("保存失败！");
                $("#appleBtn").removeAttr("disabled");
              },
              timeout:60000
        });
    } else {
        alert("数据存在不合法数据，请检查!");
        $("#appleBtn").removeAttr("disabled");
    }
};