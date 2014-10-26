# -*- coding: utf-8 -*-
"""
ServiceRequestStatusMessage={'planimplement':'Plan to be implemented',
                             'underapproval':'Request over quota. Under approval.',
                             'resourcenotavailable':'Request resource not available. System administrator is going to work on it.',
                             'resourceconflict':'Request resouce name conflict with the name of resouce that is already running',
                             'errordeploy':'Error in deploy. System administrator is alerted.',
                             'failapproval':'Fail Approval.',
                             'running':'Your Request is carrying out!',
                             'errorcreateeuao':'Error in creating EUAO task.',
                             'resourcefixed':'fix Resource not enough problem.',
                             'succeed':'Succeed! Please check your resource.'}

"""

ServiceRequestStatusMessage={'planimplement':'计划部署中',
                             'underapproval':'请求资源超过配额，等待审批。',
                             'resourcenotavailable':'资源不可用，等待系统管理员处理。',
                             'resourceconflict':'申请的资源与现有资源重名',
                             'errordeploy':'部署出错，请联系系统管理员。',
                             'failapproval':'审核不通过。',
                             'running':'您的请求正在执行中。',
                             'errorcreateeuao':'创建EUAO任务出错，请联系系统管理员。',
                             'resourcefixed':'管理员已修复资源不足问题。',
                             'succeed':'操作完成！请到资源管理页面查看。',
                             'revoked':'请求已撤销，请重新提交服务请求。'}