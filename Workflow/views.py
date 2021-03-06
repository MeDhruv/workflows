from django.shortcuts import render,render_to_response,get_object_or_404
from .models import *
from .form import *
from django.views.generic import TemplateView
from rest_framework import viewsets
from django.views.decorators import csrf
#from django.core.context_processors import csrf
from django.views.decorators.csrf import csrf_protect
from django.http.response import HttpResponseRedirect,JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib import auth
from django.contrib.auth.models import Group,User,Permission,ContentType
from django.contrib.auth.views import logout
from django.http import HttpResponse
import json
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializer import *
from django.contrib.auth.decorators import login_required
import re
from django.core import serializers

# Create your views here.

class TaskSet(viewsets.ModelViewSet):   
 #   queryset = Task.objects.all()
    queryset = Task.objects.all()
    serializer_class = Taskserializer

    

"""    def get(self,request):
        queryset = Task.objects.all()
        serializer = UserSerializer(queryset, many=True)
        #serializer_class = Taskserializer
        return Response(serializer.data)    


    def post(self, request, pk):
        #queryset = Task.objects.all()
        serializer = Taskserializer(data=request.data,partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)"""


"""    def get_serializer_class(request):
        query = Task.objects.all()
        serializer = Taskserializer(query, many=True)
        return (serializer)

    def post(self, request, format=None):
        serializer = Taskserializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST) """   

class ProjectSet(viewsets.ModelViewSet):
    queryset = Project.objects.all()
    serializer_class = ProjectSeralizer
    def post(self, request,format=None):
        serializer = Taskserializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ContentTypeSet(viewsets.ModelViewSet):
    queryset = ContentType.objects.all()
    serializer_class = ContentTypeSerialzier


class UserSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def get(self,request,pk):
        queryset = User.objects.all()
        serializer = UserSerializer(queryset, many=True)
        #serializer_class = Taskserializer
        return Response(serializer.data)



class DepartmentSet(viewsets.ModelViewSet):
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer


class InboxSet(viewsets.ModelViewSet):
    queryset = Inbox.objects.all()
    serializer_class = InboxSerializer


class GroupSet(viewsets.ModelViewSet):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer


class PermissionSet(viewsets.ModelViewSet):
    queryset = Permission.objects.all()
    serializer_class = PermissionSerializer

class SentItemset(viewsets.ModelViewSet):
    queryset = Sent_item.objects.all()
    serializer_class = SentItemSerializer

#line_chart = TemplateView.as_view(template_name='reports.html')
#line_chart_json = LineChartJSONView.as_view()


    



@login_required(login_url='/accounts/login')
def Logout(request):
    logout(request)
    return render_to_response('registration/logout.html')
#    request.user.logout()


def prj_by_dpt(request,name):
    #option = [i.name for i in l]
    d=Department.objects.get(name=name)
    project_name=[i.name  for i in d.project_set.all()]
    dataset={}
    for i in project_name:
        #data=serializers.serialize('json',d.project_set.all())
        data=serializers.serialize('json',Project.objects.get(name=i).task_set.all())
        dataset.update({i:json.loads(data)})
    js={
        'option':project_name,
        'label':dataset
    }
    return JsonResponse(js)
    #return render_to_response('home.html')


def Alert(request):
    return render_to_response('alert.html')


def task_by_emp(request,name):
    option = [i[0] for i in Task.objects.all()[0].choices]
    dataset={}
    for i in option:
        l=Task.objects.filter(assign_id=User.objects.get(username=name.lower()).id,status=i)
        dataset.update({i:json.loads(serializers.serialize('json',l))})    
    js={
        'option':option,
        'label':dataset
    }
    return JsonResponse(js)


@login_required(login_url='/accounts/login')
def Single(request,project):
    f=Task.objects.filter()
    option = [i[0] for i in Task.objects.all()[0].choices]
    dataset={}
    for i in option:
        l=Task.objects.filter(project_id=Project.objects.get(name=project).id,status=i)
        dataset.update({i:json.loads(serializers.serialize('json',l))})
    js={
        'option':option,
        'label':dataset
    }

    return JsonResponse(js)

@login_required(login_url='/accounts/login')
def profile(request):
    email=request.user.email
    #group=Group.objects.get(user=request.user.id)
    #Blog=request.user.objects.get(id=1)
    nn=request.user.date_joined
    argus={'user':request.user,
           'email':email,
           #'group':group,
           'join':nn,
           }
    return render_to_response('registration/profile.html',argus)    



from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

@login_required(login_url='/accounts/login')
def Home(request):
    p=Project.objects.all()
    #t=Task.objects.all()
    user = request.user
    t=Task.objects.filter(assign_id=user.id)
    #t=Task.objects.all()
    pform=ProjectForm()
    form = TaskEditForm()

    return render(request,'rest_home.html',{'pform':pform,'taskform':form,'project':p,'task':t,'pid':'home','user':user})

def Home_rest(request):
    p=Project.objects.all()
    #t=Task.objects.all()
    user = request.user
    #t=Task.objects.filter(assign_id=user.id)
    t=Task.objects.all()
    pform=ProjectForm()
    form = TaskEditForm()

    page = request.GET.get('page', 1)
    paginator = Paginator(t, 10)

    try:
        task_page = paginator.page(page)
    except PageNotAnInteger:
        task_page = paginator.page(1)
    except EmptyPage:
        task_page = paginator.page(paginator.num_pages)        

    #return render(request,'rest_home.html',{'pform':pform,'taskform':form,'project':p,'task':t,'pid':'home','user':user})
    return render(request,'home.html',{'taskform':form,'project':p,'task':t,'pid':'home','user':user,'task_page':task_page})



@login_required(login_url='/accounts/login')
def TaskDetail(request,pk):
    p = Project.objects.all()
    #p = Project.objects.get(id=pid)
    t=Task.objects.get(id=pk)
    user = request.user
    return render_to_response('home.html',{'task':t,'project':p,'work':'edit','user':user})


@login_required(login_url='/accounts/login')
def prj_data(request,what):
    model = globals()[what]
    pp=model._meta.related_objects[0].name
    #d._meta.get_all_related_objects()[0].name
    #print(what)
    #l=what.objects.all()
    d=model.objects.all()
    p=serializers.serialize('json',d)
    c=[]
    #sets=str(re.search('Workflow.(.*?)>',str(pp)).group(1))+'_set'
    sets=(str(pp)+'_set')

    if(what=='Department'):
        for i in d:
            l=i.serializable_value(sets).values()
            c.append(l.count())
            

        js={
            'label':json.loads(p),
            'count':c
        }            
    else:    
        s_m=globals()[pp.capitalize()]
        option=[i[0] for i in s_m.objects.all()[0].choices]
        status=[]
        for i in d:
            l=i.serializable_value(sets).values()
            c.append(l.count())
            #[ i['status'] for i in range(l)]
            temp=[]
            for j in option:
                cn=[k['status'] for k in l]
                #cn.count(j)
                temp.append(cn.count(j))
            status.append(temp)    

            js={
            'label':json.loads(p),
            'count':c,
            'option':option,
            'status':status


            }    
    return JsonResponse(js)

@login_required(login_url='/accounts/login')
def emp_data(request):
    user=User.objects.all()
    related=User._meta.get_all_related_objects()[1:]
    c=[]
    p=serializers.serialize('json',user[1:])
    for i in user[1:]:
        c.append(i.serializable_value('task_set').values().count())

    js={
        'label':json.loads(p),
        'count':c
    }    
    return JsonResponse(js)    

    if what == 'priority':
        l_count=Task.objects.filter(priority='Low').count()
        h_count=Task.objects.filter(priority='High').count()
        n_count=Task.objects.filter(priority='Normal').count()
        
        label=['Hight','Low','Normal']
        count=[h_count,l_count,n_count]
        data={
            'label':label,
            'count':count
        }
        return JsonResponse(data)

    elif what == 'department': 
        t=Department.objects.all()
        count=[i.project_set.all().count() for i in t]
        label=[i.name for i in t]
        data={

        'label' : label,
        #'label' : str(label).replace('[','').replace(']',''),
        'count' : count
        }
        return JsonResponse(data)



    elif what == 'status':
        c_count=Task.objects.filter(status='Complete').count()
        i_count=Task.objects.filter(status='In Process').count()
        n_count=Task.objects.filter(status='New').count()
        label=['Complete','In Process','New']
        count=[c_count,i_count,n_count]
        data={
            'label':label,
            'count':count
        }
        return JsonResponse(data)

    #p=Project.objects.filter()
@login_required(login_url='/accounts/login')
def project_data(request):
    p=Project.objects.all()
    project=[i.name for i in p]
    print(project)
    count=[p[0].task_set.count(),p[1].task_set.count(),p[2].task_set.count()]
    data={
        'project':project,
        'count':count
    }
    return JsonResponse(data)

@login_required(login_url='/accounts/login')
def Reports(request):
    
    #p=Project.objects.all()
    #project=[i.name for i in p]
    #print(project)
    #count=[p[0].task_set.count(),p[1].task_set.count(),p[2].task_set.count()]
    #['CMS', 'Scraping', 'Audit']
    #data = ModelDataSource(p,fields=['name'])
    #chart=flot.LineChart(data)
    return render_to_response('reports.html',{'user':request.user})
 #   line_chart = TemplateView.as_view(template_name='reports.html')
 #   line_chart_json = LineChartJSONView.as_view()
#    return HttpResponse(line_chart_json)




def login(request):
    if request.user.is_authenticated():
        return HttpResponseRedirect('/')
    else:
        form=LoginForm()
        c={'form':form}
        c.update((request))
        return render(request,'registration/login.html',c)
@login_required(login_url='/accounts/login')
def logout(request):
    auth.logout(request)
    return render_to_response('registration/logged_out.html')

def auth_view(request):
    if request.method=='POST':
        response_data={}
        username = request.POST.get('username', '')
        password = request.POST.get('password', '')
        user = auth.authenticate(username=username, password=password)
        u=User.objects.filter(username=username)
        if not u:
            return HttpResponse('username')
        if user is not None:
            auth.login(request, user)
#            response_data['result'] = 'Success'
#            response_data['message'] = 'you are login'
            #return HttpResponse(json.dumps(response_data),content_type="application/json")
            return HttpResponseRedirect('/')
        elif request.user.is_authenticated():
            return HttpResponseRedirect('/')
        else:


#            form = LoginForm(request.POST)
#            c = {'form': form}
#            c.update(csrf(request))
 #           response_data['result'] = 'fail'
  #          response_data['message'] = 'do not'
            return HttpResponse('not')
            #return HttpResponse(json.dumps(response_data),content_type="application/json")

            #return render(request, 'registration/login.html', c)"""""            



def Isread(request,pk):
    e = Inbox.objects.get(id=pk)
    e.is_read = True
    e.save()
    return HttpResponse('OK')

@login_required(login_url='/accounts/login')
def ProjectTask(request,pk):

    p = Project.objects.all()
    pi = Project.objects.get(id=pk)
    t=Task.objects.filter(assign_id=request.user.id,project_id=pk)
    #t=Task.objects.filter(project_id=pk)
    return render_to_response('home.html',{'project':p,'task':t,'pid':pi,'user':request.user})


@login_required(login_url='/accounts/login')
def Email_rest(request):
    e = Inbox.objects.filter(receiver_id_id=request.user.id)
    #e = Inbox.objects.all()
    cform = InboxForm()

    return render(request,'email_rest.html',{'email':e,'inbox':True,'cform':cform})

def Email(request):
    #e = Inbox.objects.filter(receiver_id_id=request.user.id)
    e = Inbox.objects.all()
    cform = InboxForm()

    return render(request,'email_rest.html',{'email':e,'inbox':True,'cform':cform})



def EmailDetail(request,pk):
    e=Inbox.objects.get(id=pk)
    return render_to_response('email.html',{'mail':e,'inbox':True})

from .form import InboxForm

from django.template import RequestContext
def Compose(request):
    form = InboxForm()
    sform = SentForm()
    return render(request,'email.html',{'compose':True,'form':form,'user':request.user,'sform':sform})

from django.http.response import HttpResponse,HttpResponseRedirect

@login_required(login_url='/accounts/login')

def SentView(request):
    d=Sent_item.objects.all()
    #return HttpResponse(d)
    return render_to_response('email.html',{'email':d,'sent':True,'user':request.user})
    #return HttpResponse(serializers.serialize('json',d))

def SentItem(request,pk):
    d=Sent_item.objects.get(id=pk)
    return render_to_response('email.html',{'mail':d,'sent_item':True,'user':request.user})


def sending(request):
    if request.method=='POST':
        form=InboxForm(request.POST)
        sent_form = SentForm(request.POST)
        if form.is_valid():
            f=form.save(commit=False)
            s=sent_form.save(commit=False)
            f.sender_id = str(request.user.first_name)+'<'+str(request.user.email)+'>'
            s.sender_id = str(request.user.first_name)+'<'+str(request.user.email)+'>'
            f.save()
            s.save()
            return HttpResponseRedirect('/email/')

@login_required(login_url='/accounts/login')

def CreateProject(request):
    if request.method == 'POST':
        form = ProjectForm(request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect('/')
    else:
        form = ProjectForm()
        #project=True
        return render(request,'home.html',{'form':form,'user':request.user,'project_c':True})        


def Searching(request,srchkey):
    if request.method=='GET':
        search_q=request.GET['search']
        if(srchkey=='project'):
            query=Task.objects.filter(name__contains=search_q)
            project=Project.objects.filter(name__contains=search_q)
        
            context={
                'task':query,
                'keyword':search_q,
                'project':project,
                'user':request.user
            }
        else:
            temp=[]
            t1=Inbox.objects.filter(content__contains=search_q,subject__contains=search_q)
            t2=Inbox.objects.filter(subject__contains=search_q)
            t3=Inbox.objects.filter(content__contains=search_q)
            t4=Inbox.objects.filter(sender_id__contains=search_q)
            temp.extend(t1)
            temp.extend(t2)
            temp.extend(t3)
            temp.extend(t4)
            query=list(set(temp))
            temp=[]
            t1=Sent_item.objects.filter(content__contains=search_q,subject__contains=search_q)
            t2=Sent_item.objects.filter(subject__contains=search_q)
            t3=Sent_item.objects.filter(content__contains=search_q)
            t4=Sent_item.objects.filter(sender_id__contains=search_q)
            temp.extend(t1)
            temp.extend(t2)
            temp.extend(t3)
            temp.extend(t4)
            sent_query=list(set(temp))


            temp=[]
            sent=Sent_item.objects.filter()
            context={
                'inbox':query,
                'sent':sent_query,
                'keyword':search_q,
                #'project':project,
                'user':request.user
            }            

        return render_to_response('search_result.html',context)


@login_required(login_url='/accounts/login')
def Edit(request,pk):
    #form=TaskEditForm()
    if request.method =='POST':
        task=get_object_or_404(Task,id=pk)
        form = TaskEditForm(request.POST or None,instance=task)
        if form.is_valid():
            name=request.user.first_name+" "+request.user.last_name
            task.modify_by=name
            task.save()
            form.save()
            return HttpResponseRedirect('/')
        else:
            return render(request,'home.html',{'form':form,'work':'taskedit','user':request.user})
    else:
        task=get_object_or_404(Task,id=pk)
        form = TaskEditForm(instance=task)   
        return render(request,'home.html',{'form':form,'work':'taskedit','user':request.user}) 
                
"""    task=get_object_or_404(Task,id=pk)
    form=TaskEditForm(request.POST or None,instance=task)
    user=request.user
    if request.POST and form.is_valid():
        name=request.user.first_name+" "+request.user.last_name
        task.modify_by=name
        task.save()
        form.save()
        return HttpResponseRedirect('/')
    return render(request,'home.html',{'form':form,'work':'taskedit','user':request.user})        """

import csv
def export_csv(requests):
    from django.utils.encoding import smart_str
    response=HttpResponse(content='text/csv')
    row = csv.writer(response, csv.excel)
    response.write(u'\ufeff'.encode('utf8'))
    query=Task.objects.all()
    response['Content-Disposition'] = 'attachment; filename="result.csv"'
    #row=csv.writer(response)
    #model=[]
    header=['ID','Name','Task Description','Comments','Created By','Created Date','Modify By','Project Name','Priority','TAT','Status']
    row.writerow(header)
    for f in query:
        row.writerow([
            smart_str(f.id),
            smart_str(f.name),
            smart_str(f.task_description),
            smart_str(f.comments),
            smart_str(f.created_by),
            smart_str(f.created_date),
            smart_str(f.modify_by),
            smart_str(f.project_id.name),
            smart_str(f.priority),
            smart_str(f.tat),
            smart_str(f.status)
        ])
    return response
