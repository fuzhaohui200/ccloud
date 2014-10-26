from django.http import HttpResponse,Http404
import datetime

from django.contrib.auth.models import User
import aix.aix_function
import vmware.vmware_function
import workflow.workflow_function
import aix.aix_init_function
import EUAO.euao_function

import workflow.setting as workflow_setting
import charge.charge_function

def init_aix(request):
    for group_item in request.user.groups.all():
        if group_item.name==workflow_setting.sys_admin_group_name:
            aix.aix_init_function.init()
            return HttpResponse('Initialize aix from aix.setting.py complete!')
    return HttpResponse('User not allowed.')

def clear_vmware(request):
    for group_item in request.user.groups.all():
        if group_item.name==workflow_setting.sys_admin_group_name:
            vmware.vmware_function.test_reset_all()
            return HttpResponse('clear vmware complete!')
    return HttpResponse('User not allowed.')

def clear_workflow(request):
    for group_item in request.user.groups.all():
        if group_item.name==workflow_setting.sys_admin_group_name:
            workflow.workflow_function.reset_all()
            return HttpResponse('Rest workflow complete!')
    return HttpResponse('User not allowed.')

def clear_aix(request):
    for group_item in request.user.groups.all():
        if group_item.name==workflow_setting.sys_admin_group_name:
            aix.aix_init_function.clear_all()
            return HttpResponse('Rest aix complete!')
    return HttpResponse('User not allowed.')

def clear_euao(request):
    for group_item in request.user.groups.all():
        if group_item.name==workflow_setting.sys_admin_group_name:
            EUAO.euao_function.reset_all()
            return HttpResponse('Rest euao complete!')
    return HttpResponse('User not allowed.')


def clear_all(request):
    for group_item in request.user.groups.all():
        if group_item.name==workflow_setting.sys_admin_group_name:
            aix.aix_init_function.clear_all()
            EUAO.euao_function.reset_all()
            workflow.workflow_function.reset_all()
            vmware.vmware_function.test_reset_all()
            charge.charge_function.test_clear_all_vioclient_log()
            return HttpResponse('Rest all complete!')
    return HttpResponse('User not allowed.')

def init_all(request):
    for group_item in request.user.groups.all():
        if group_item.name==workflow_setting.sys_admin_group_name:
            aix.aix_init_function.init()
            return HttpResponse('Initialize aix from aix.setting.py complete!')
    return HttpResponse('User not allowed.')

def add_ip_from_cfg(request):
    for group_item in request.user.groups.all():
        if group_item.name==workflow_setting.sys_admin_group_name:
            aix.aix_init_function.add_ip()
            return HttpResponse('Add aix ip from aix.resource_pool.py complete!')
    return HttpResponse('User not allowed.')

def add_hdisk_from_cfg(request):
    for group_item in request.user.groups.all():
        if group_item.name==workflow_setting.sys_admin_group_name:
            aix.aix_init_function.add_hdisk()
            return HttpResponse('Add aix hdisk from aix.resource_pool.py complete!')
    return HttpResponse('User not allowed.')

def add_aix_service_ip(request):
    for group_item in request.user.groups.all():
        if group_item.name==workflow_setting.sys_admin_group_name:
            count=int(request.GET['count'])
            if count<200:
                aix.aix_init_function.set_test_service_ip(count)
                return HttpResponse('Initialze aix test data: %d' % count)
            else:
                return HttpResponse('Too much, only init 200.')
    return HttpResponse('User not allowed')

def add_aix_manage_ip(request):
    for group_item in request.user.groups.all():
        if group_item.name==workflow_setting.sys_admin_group_name:
            count=int(request.GET['count'])
            if count<200:
                aix.aix_init_function.set_test_manage_ip(count)
                return HttpResponse('Initialze aix test data: %d' % count)
            else:
                return HttpResponse('Too much, only init 200.')
    return HttpResponse('User not allowed')

def init_test_aix_data(request):
    for group_item in request.user.groups.all():
        if group_item.name==workflow_setting.sys_admin_group_name:
            count=int(request.GET['count'])
            if count<200:
                aix.aix_init_function.set_test(count)
                return HttpResponse('Initialze aix test data: %d' % count)
            else:
                aix.aix_init_function.set_test(200)
                return HttpResponse('Too much, only init 200.')
    return HttpResponse('User not allowed')

def init_delete_aix_test(request):
    for group_item in request.user.groups.all():
        if group_item.name==workflow_setting.sys_admin_group_name:
            aix.aix_init_function.delete_test()
            return HttpResponse('delete all aix test data.')
    return HttpResponse('User not allowed')

