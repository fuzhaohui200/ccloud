# Create your views here.
# coding=utf-8
from django.core.context_processors import csrf
from django.shortcuts import render_to_response
from django.http import HttpResponse
from django.http import HttpRequest
from django.http import HttpResponseRedirect
from django.template import Template,Context
from django.template.loader import get_template
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.models import User

from django.contrib.auth import *

from django.views.decorators.csrf import csrf_protect, csrf_exempt
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import permission_required

from django.utils import simplejson
import aix.aix_function as aixfunction
import workflow.workflow_function as workflowfunction
from workflow.models import ServiceRequest

import UI.setting as UI_setting

common_context_dict={}

ext_js_dir_dict={'static_root':'/static', }

common_context_dict.update(ext_js_dir_dict)

@login_required
@csrf_exempt
def index(request):
    t=get_template('index.html')
    context_dict={}
    context_dict.update(common_context_dict)
    context_dict.update(csrf(request))
    c=Context(context_dict)
    html=t.render(c)
    return HttpResponse(html)

@login_required
def functionContent(request):
    t=get_template('content.html')
    context_dict={}
    context_dict.update(common_context_dict)
    context_dict.update(csrf(request))
    c=Context(context_dict)
    html=t.render(c)
    return HttpResponse(html)

@csrf_protect 
def user_login(request):
    t=get_template('login.html')
    context_dict={}
    context_dict.update(common_context_dict)
    context_dict.update(csrf(request))
    c=Context(context_dict)
    html=t.render(c)
    return HttpResponse(html)

@csrf_protect 
def user_auth(request):
    username=request.POST['username']
    password=request.POST['password']
    user=authenticate(username=username,password=password)
    if user is not None:
        login(request,user)
        return HttpResponse("{success: true, msg: '%s'}" % UI_setting.login_info['success'])
    else:
        return HttpResponse("{success: false, msg: '%s'}" % UI_setting.login_info['fail'])
    
@csrf_exempt        
def user_logout(request):
    logout(request)
    return HttpResponse(UI_setting.logout_info)

@login_required
def get_user_groups(request):
    username=request.user.username
    group_list=request.user.groups.all()
    groupnames=[]
    if len(group_list)>0:
        for group_item in group_list:
            groupnames.append(group_item.name)
    else:
        groupnames=['']
    json_dict={'group_list':groupnames}
    return HttpResponse(simplejson.dumps(json_dict,ensure_ascii=False))

@login_required
def get_username(request):
    return HttpResponse(request.user.username)

@login_required
def get_user_aix_quota(request):
    user=request.user
    user_profile=user.get_profile()
    aix_cpu_quota=user_profile.aix_cpu_quota
    aix_mem_quota=user_profile.aix_mem_quota
    aix_count_quota=user_profile.aix_count_quota
    aix_cpu_used=user_profile.aix_cpu_used
    aix_mem_used=user_profile.aix_mem_used
    aix_count_used=user_profile.aix_count_used
    
    quota={'aix_cpu_quota':aix_cpu_quota,
            'aix_mem_quota':aix_mem_quota,
            'aix_count_quota':aix_count_quota}
    used={'aix_cpu_used':aix_cpu_used,
          'aix_mem_used':aix_mem_used,
          'aix_count_used':aix_count_used}
    result={'quota':quota,'used':used}

    return HttpResponse(simplejson.dumps(result,ensure_ascii=False),content_type='application/json;charset=utf-8')

@login_required
@csrf_protect
def overview(request):
    t=get_template('overview.html')
    context_dict={}
    context_dict.update(common_context_dict)
    context_dict.update(csrf(request))
    c=Context(context_dict)
    html=t.render(c)
    return HttpResponse(html)

@csrf_protect
def useTerms(request):
    t=get_template('useTerms.html')
    context_dict={}
    context_dict.update(common_context_dict)
    context_dict.update(csrf(request))
    c=Context(context_dict)
    html=t.render(c)
    return HttpResponse(html)

@csrf_protect
def privicyStatement(request):
    t=get_template('privacyStatement.html')
    context_dict={}
    context_dict.update(common_context_dict)
    context_dict.update(csrf(request))
    c=Context(context_dict)
    html=t.render(c)
    return HttpResponse(html)

@csrf_protect
def aboutMe(request):
    t=get_template('aboutMe.html')
    context_dict={}
    context_dict.update(common_context_dict)
    context_dict.update(csrf(request))
    c=Context(context_dict)
    html=t.render(c)
    return HttpResponse(html)



@login_required
@csrf_protect
def change_passwd_page(request):
    t=get_template('change_password.html')
    context_dict={}
    context_dict.update(common_context_dict)
    context_dict.update(csrf(request))
    c=Context(context_dict)
    html=t.render(c)
    return HttpResponse(html)

    
@login_required
@csrf_protect
def change_passwd(request):
    username=request.user.username
    old_passwd=request.POST['old_passwd']
    new_passwd=request.POST['new_passwd']
    confirmed_passwd=request.POST['confirmed_passwd']

    if new_passwd==confirmed_passwd:
        user=authenticate(username=username,password=old_passwd)
        if user:
            user.set_password(new_passwd)
            user.save()
            return HttpResponse('{success: true, msg: "重置密码成功。"}')
        else:
            return HttpResponse('{success: false, msg: "原密码不正确。"}')
    else:
        return HttpResponse('{success: false, msg: "两次密码不一致"}')

@login_required
def vioclient_operate_available(request):
    if 'vioclient' in request.GET:
        vioclient_name=request.GET['vioclient']
    else:
        return HttpResponse('no vioclient name')
    if 'operation' in request.GET:
        operation_name=request.GET['operation']
    else:
        return HttpResponse('no operation')
    
    if aixfunction.vioclient_operate_available(vioclient_name,operation_name):
        return HttpResponse('allow')
    else:
        return HttpResponse('deny')

@login_required
def servicerequest_revoke_available(request):
    if 'service_request_id' in request.GET:
        sr_id=request.GET['service_request_id']
    else:
        return HttpResponse('no service request id')

    if workflowfunction.service_request_revoke_available(sr_id):
        return HttpResponse('allow')
    else:
        return HttpResponse('deny')

@login_required
def revoke_service_request(request):
    if 'service_request_id' in request.GET:
        sr_id=request.GET['service_request_id']
    else:
        return HttpResponse('no service request id')
    service_request_item=ServiceRequest.objects.get(id=sr_id)
    if request.user.username != service_request_item.submitter:
        return HttpResponse('deny')
    else:
        if workflowfunction.revoke_service_request(sr_id):
            return HttpResponse('done')
        else:
            return HttpResponse('Error')


@login_required
def read_euao_log(request):
    euao_log_file=open(UI_setting.euao_log_path)
    euao_log_list=euao_log_file.read().split('\n')
    html_str=''
    for line in euao_log_list:
        html_str+='<p>%s</p>' % line
    
    return HttpResponse(html_str)

@login_required
def read_ecms_log(request):
    ecms_log_file=open(UI_setting.ecms_log_path)
    ecms_log_list=ecms_log_file.read().split('\n')
    html_str=''
    for line in ecms_log_list:
        html_str+='<p>%s</p>' % line
    
    return HttpResponse(html_str)