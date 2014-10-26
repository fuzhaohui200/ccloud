/**
 *   登录页面
 */

var useTermsWindow, privacyStatementWindow, aboutMeWindow;

$(function() {

    $('#login_form').submit(function() {
        var options = {
            url : "/user_auth/",
            beforeSubmit : function(arr, $form, options) {
                if (!(/^http:.*/.test(options.url) || /^https:.*/.test(options.url))) {
                    if ( typeof (options.headers) == "undefined") {
                        options.headers = {
                            'X-CSRFToken' : $.cookie('csrftoken')
                        };
                    } else {
                        options.headers.extend({
                            'X-CSRFToken' : $.cookie('csrftoken')
                        });
                    }
                }
            },
            type : 'post',
            success : function(data) {
                var callback = eval("(" + data + ")");
                if (callback.success) {
                    var params = getUrlParams();
                    if (!params.next) {
                        window.location = '/index/'
                    } else {
                        window.location = params.next
                    }
                } else {
                    alert(callback.msg);
                }
            }
        };
        $(this).ajaxSubmit(options);
        return false;
    });
});

// 使用条款
var viewUseTerms = function() {
    $.ajax({
        type : "GET",
        url : "/useTerms/",
        dataType : "text",
        success : function(data) {
            $("#login_footer").append("<div id='useTermsWindow'> </div>");
            useTermsWindow = $("#useTermsWindow").kendoWindow({
                title : "使用条款",
                modal : true,
                visible : false,
                resizable : true,
                width : 750,
                height : 460
            }).data("kendoWindow");

            var useTermsTemplate = kendo.template(data);

            useTermsWindow.content(useTermsTemplate({}));
            useTermsWindow.center().open();
        }
    });
};

// 隐私声明
var viewPrivacyStatement = function() {
    $.ajax({
        type : "GET",
        url : "/privicyStatement/",
        dataType : "text",
        success : function(data) {
            $("#login_footer").append("<div id='privacyStatementWindow'> </div>");
            privacyStatementWindow = $("#privacyStatementWindow").kendoWindow({
                title : "隐私声明",
                modal : true,
                visible : false,
                resizable : true,
                width : 750,
                height : 460
            }).data("kendoWindow");
        
            var privacyStatementTemplate = kendo.template(data);
            privacyStatementWindow.content(privacyStatementTemplate({}));
            privacyStatementWindow.center().open();
        }
    });
};

// 关于我们
var viewAboutMe = function() {
    $.ajax({
        type : "GET",
        url : "/aboutMe/",
        dataType : "text",
        success : function(data) {
            $("#login_footer").append("<div id='aboutMeWindow'> </div>");
            aboutMeWindow = $("#aboutMeWindow").kendoWindow({
                title : "关于",
                modal : true,
                visible : false,
                resizable : true,
                width : 750,
                height : 390
            }).data("kendoWindow");

            var aboutMeTemplate = kendo.template(data);

            aboutMeWindow.content(aboutMeTemplate({}));
            aboutMeWindow.center().open();
        }
    });
};

// 关闭窗口
var closeWindow = function(flag) {
    if(flag == 1) {
        useTermsWindow.close();
    } else if(flag == 2) {
        privacyStatementWindow.close();
    } else {
        aboutMeWindow.close();
    }
};
