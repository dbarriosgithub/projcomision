from time import gmtime, strftime
from django.shortcuts import render, HttpResponse, get_object_or_404, redirect, render_to_response
from django.urls import reverse_lazy
from django.contrib import messages

from .models import Person
from .models import Solicitud
from .models import Metas

from .forms import PersonForm
from .forms import SolicitudForm
from .forms import MetaForm


from django.views.generic.list import ListView
from django.views.generic.edit import UpdateView
from django.views.generic import CreateView
from django.core.paginator import Paginator
from datetime import datetime, timedelta, date
import calendar
import json


class personIndex(ListView):
    model = Person
    template_name = 'sellingsapp/person_list.html'
    context_object_name = 'person_list'
    paginate_by = 7
    ordering = ['id']
    # def get_queryset(self):
    #     return Person.objects.filter(id!='')


# def personIndex(request):
#     person_list = Person.objects.order_by('id')
#     context = {'person_list': person_list}
#     return render(request, 'sellingsapp/person_index.html', context)

    # def get(self, request, *args, **kwargs):
    # person_list = Person.objects.order_by('id')
    # context = {'person_list': person_list}
    # return render(request, self.template_name, context)


def personAdd(request):
    if request.method == 'POST':
        form = PersonForm(request.POST)
        if form.is_valid():
            person = form.save(commit=False)
            person.first_name = request.POST['first_name']
            person.last_name = request.POST['last_name']
            person.celphone = request.POST['celphone']
            person.address = request.POST['address']
            person.email = request.POST['email']
            person.save()
            messages.success(request, 'El registro ha sido ingresado.')
            form = PersonForm()
    else:
        form = PersonForm()

    return render(request, 'sellingsapp/person_add.html', {'form': form})


class personDetail(UpdateView):
    model = Person
    fields = ['cc_id', 'first_name', 'last_name',
              'celphone', 'address', 'email']
    template_name = 'sellingsapp/person_detail.html'

    def form_valid(self, form):
        person = form.save(commit=False)
        # print(PersonForm(person))
        # print(vars(self.request))
        # print(person.objects)
        person.save()
        messages.success(self.request, 'El registro ha sido actualizado.')
        return self.render_to_response(self.get_context_data(form=form))
        # return redirect('personDetail',person.id)

        # return redirect('personDetail')

        # return self.render_to_response(self.get_context_data(form=self.form))

    # def personDetail(request):
    #     return render(request, 'sellingsapp/person_detail.html', {'urls': [home1, home2]})

    # def get(self, request, *args, **kwargs):
    #     if request.method == 'POST':
    #         messages.success(request, 'El registro ha sido actualizado.')
    #         return render(request, 'sellingsapp/person_detail.html')

    # busca el modelo idenficado por el id
    # person_detail = get_object_or_404(Person, pk=id_person)

    # # si se ha enviado el formulario de editar
    # if request.method == "POST":
    #     form = PersonForm(request.POST, instance=person_detail)

    #     if form.is_valid():
    #         person = form.save(commit=False)
    #         person.first_name = request.POST['first_name']
    #         person.last_name = request.POST['last_name']
    #         person.age = request.POST['age']
    #         person.celphone = request.POST['celphone']
    #         person.address = request.POST['address']
    #         person.email = request.POST['email']
    #         person.save()
    #         messages.success(request, 'El registro ha sido actualizado.')
    #     return render(request, 'sellingsapp/person_detail.html', {'form': form})
    # else:
    #     form = PersonForm(instance=person_detail)
    #     return render(request, 'sellingsapp/person_detail.html', {'form': form})


def personDelete(request, id_person):
    # busca el modelo idenficado por el id
    person_delete = get_object_or_404(Person, pk=id_person)
    person_delete.delete()
    custom_message = " | "+person_delete.first_name + \
        " " + person_delete.last_name + " | "
    messages.success(request, "El registro " + str(id_person) +
                     "-" + custom_message+" ha sido eliminado")

    return redirect('personList')


def handler404(request, exception, template_name="404.html"):
    response = render_to_response("404.html")
    response.status_code = 404
    return response


# --------------------------------------------------------------------------------
#       Utiliza la clase ListView para para crear una vista basada en clase
# --------------------------------------------------------------------------------
class solicitudIndex(ListView):
    model = Solicitud
    template_name = 'sellingsapp/solicitud_list.html'
    context_object_name = 'solicitud_list'
    paginate_by = 7
    ordering = ['product_name']

    def get_queryset(self):

        if self.request.user.is_anonymous == False:
            user_email = self.request.user.email
        else:
            result = []
            return result

        if self.request.user.get_username() == '@dm1n':
            result = Solicitud.objects.all()
            return result

        try:
            ObjPerson = Person.objects.get(email=user_email)

            if ObjPerson.id:
                findId = ObjPerson.id
                result = Solicitud.objects.filter(asesor_id=findId)

        except Person.DoesNotExist:
            result = []

        return result

# --------------------------------------------------------------------------------
#       Utiliza la clase ListView para para crear una vista basada en clase
# --------------------------------------------------------------------------------


def proyectionIndex(request):

    model = Solicitud
    template_name = 'sellingsapp/proyection_list.html'
    context_object_name = 'proyection_list'

    today = date.today()
    search_mes = ["enero", "febrero", "marzo", "abril", "mayo", "junio",
                  "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"]

    if request.user.is_anonymous == True:
        return redirect('sign_out')

    if (request.user.get_username() == "@dm1n" or request.user.get_username() == "supervis@r"):
        search_cc_id = request.GET.get('search_cc_id')

        try:
            ObjPerson = Person.objects.get(cc_id=search_cc_id)
            search_email = ObjPerson.email
        except Person.DoesNotExist:
            search_email = ""
    else:
        search_email = request.user.email

    if search_email != '' and search_email != None:
        cant_solicitadas = proyectionReview(
            search_email, search_mes[today.month-1], today.day, 'solicitado')
        cant_instaladas = proyectionReview(
            search_email, search_mes[today.month-1], today.day, 'instalado')
    else:
        result = {}
        return render(request, template_name, result)

    dias_habiles = validDays(lastDayMonth())

    dias_transcurridos = validDays("")-1

    tot_ingresadas =  cant_solicitadas+cant_instaladas

    if dias_transcurridos==0:
        proyeccion_ingresadas=0
        proyeccion_instaladas=0
    else:
        proyeccion_ingresadas = ((cant_solicitadas+cant_instaladas)/dias_transcurridos)*dias_habiles
        proyeccion_instaladas = (cant_instaladas/dias_transcurridos)*dias_habiles
    
    metaObjFVD = getMeta(search_mes[today.month-1],today.year,'FVD')
    metaObjCU = getMeta(search_mes[today.month-1],today.year,'CU')

    
    if (metaObjFVD.exists()==True):
        meta_ingresadasFVD = metaObjFVD[0].meta_ingresada
        meta_instaladasFVD = metaObjFVD[0].meta_instalada
        porc_meta_ingresadasFVD = (proyeccion_ingresadas/meta_ingresadasFVD)*100
        porc_meta_instaladasFVD = (proyeccion_instaladas/meta_instaladasFVD)*100
    else:
        meta_ingresadasFVD = 0
        meta_instaladasFVD = 0
        porc_meta_ingresadasFVD=0
        porc_meta_instaladasFVD=0


    if (metaObjCU.exists()==True):
        meta_ingresadasCU = metaObjCU[0].meta_ingresada
        meta_instaladasCU = metaObjCU[0].meta_instalada
        porc_meta_ingresadasCU = (proyeccion_ingresadas/meta_ingresadasCU)*100
        porc_meta_instaladasCU = (proyeccion_instaladas/meta_instaladasCU)*100
    else:
        meta_ingresadasCU = 0
        meta_instaladasCU = 0
        porc_meta_ingresadasCU=0
        porc_meta_instaladasCU=0



    return render(request, template_name,
        {"dias_habiles": dias_habiles,
         "dias_transcurridos": dias_transcurridos,
         "cant_instaladas": cant_instaladas,
         "cant_solicitadas": tot_ingresadas,
         "proyeccion_ingre": format(proyeccion_ingresadas,".2f"),
         "proyeccion_instal": format(proyeccion_instaladas,".2f"),
         "meta_ingresadasFVD": meta_ingresadasFVD,
         "meta_instaladasFVD": meta_instaladasFVD,
         "porc_meta_ingresadasFVD": format(porc_meta_ingresadasFVD,".2f"),
         "porc_meta_instaladasFVD": format(porc_meta_instaladasFVD,".2f"),
         "meta_ingresadasCU": meta_ingresadasCU,
         "meta_instaladasCU": meta_instaladasCU,
         "porc_meta_ingresadasCU":format(porc_meta_ingresadasCU,".2f"),
         "porc_meta_instaladasCU":format(porc_meta_instaladasCU,".2f"),
         })

# ------------------------------------------------------------------------
#       Calcula la proyección de cada asesor
# -----------------------------------------------------------------------


def proyectionReview(user_email, mes, dia, status):
    tot_status = 0
    try:
        ObjPerson = Person.objects.get(email=user_email)
        asesor_id = ObjPerson.id
    except Person.DoesNotExist:
        return 0

    if user_email != '':
        sql_query = "status='"+status+"' and asesor_id='" + \
            str(asesor_id)+"' and mes='"+mes+"' and dia != '"+str(dia)+"'"
        result = Solicitud.objects.extra(where=[sql_query])
        for record in result:
            tot_status += record.product_cant

    return tot_status


# -------------------------------------------------------------------------
#       Función para obtener días hábiles del  mes transcurridos hasta hora
# -------------------------------------------------------------------------
def validDays(finalday):
    # Día actual
    today = date.today()

    formato = '%d/%m/%Y'
    contador = 0

    fechadesde = "01/"+str(today.month)+"/"+str(today.year)

    if finalday != "":
        fechahasta = finalday
    else:
        fechahasta = str(today.day)+"/"+str(today.month)+"/"+str(today.year)

    fechadesde = datetime.strptime(fechadesde, formato)
    fechahasta = datetime.strptime(fechahasta, formato)

    while fechadesde <= fechahasta:
        if datetime.weekday(fechadesde) != 6:
            if isHoliday(fechadesde) == False:
                contador += 1
        fechadesde = fechadesde + timedelta(days=1)

    return contador

# -----------------------------------------------------------------------
#      Función que verifica si el día es feriado
# -----------------------------------------------------------------------
def isHoliday(dia):
    formato = '%d/%m/%Y'
    hollidays = '[{"feriado":"14/10/2019"}]'
    dias_feriados = json.loads(hollidays)

    for value in dias_feriados:
        if value["feriado"] == datetime.strftime(dia, formato):
            return True

    return False

# -----------------------------------------------------------------------
#       Función que obtien el último día del mes
# -----------------------------------------------------------------------
def lastDayMonth():
    today = date.today()
    day = calendar.monthrange(int(strftime("%Y", gmtime())),
                              int(strftime("%m", gmtime())))[1]
    lastDate = str(day)+"/"+str(today.month)+"/"+str(today.year)
    return lastDate

# -----------------------------------------------------------------------
#  función para verificar si ya existe la meta resgistrada
# -------------------------------------------------------------------------
def getMeta(mes_meta,anio_meta,canal_venta):
  #TODO mejorar código
    try:
        sql_query = "mes='"+mes_meta+"' and anio='" +str(anio_meta) +"' and canal_venta='"+canal_venta+"'"
        result = Metas.objects.extra(where=[sql_query])
    except Metas.DoesNotExist:
        result = []

    return result



# -----------------------------------------------------------------------
#       Clase ListView que utiliza filter para búsqueda personalizada
# -----------------------------------------------------------------------
class searchSolicitud(ListView):
    model = Solicitud
    template_name = 'sellingsapp/solicitud_list.html'
    context_object_name = 'solicitud_list'
    paginate_by = 7
    ordering = ['product_name']

    def get_queryset(self):
        queryset = super(searchSolicitud, self).get_queryset()

        search_field = self.request.GET.get('search_field').strip()
        search_value = self.request.GET.get('search_text').strip()

        if self.request.user.is_anonymous == False:
            user_email = self.request.user.email
        else:
            result = []
            return result

        if self.request.user.get_username() == '@dm1n':
            result = Solicitud.objects.extra(
                where=[search_field+"='"+search_value+"'"])
            return result

        try:
            ObjPerson = Person.objects.get(email=user_email)
            asesor_id = ObjPerson.id

        except Person.DoesNotExist:
            result = []

        if search_value != '':
            result = Solicitud.objects.extra(
                where=[search_field+"='"+search_value+"' and asesor_id='"+str(asesor_id)+"'"])
        else:
            result = Solicitud.objects.filter(asesor_id=asesor_id)

        return result

# -------------------------------------------------------------------------
#             Auto-complete del campo de búsqueda de campañas
#  ------------------------------------------------------------------------
def autoCompleteSearchSolicitud(request):

    if request.is_ajax():
        q = request.GET.get('term')
        field_search = request.GET.get('field')
        solicitudes = Solicitud.objects.extra(
            where=[field_search+" LIKE %s"], params=["%"+str(q)+"%"])
        results = []

        for pl in solicitudes:
            place_json = {}
            place_json = str(eval("pl."+field_search))
            results.append(place_json)

        data = json.dumps(results)
        mimetype = ''

    else:
        data = 'fail'
        mimetype = 'application/json'

    return HttpResponse(data, mimetype)


# -----------------------------------------------------------------------
#                Utiliza una función para la view
# -----------------------------------------------------------------------
def solicitudAdd(request):

    if request.user.is_anonymous == True:
        return redirect('sign_out')

    if request.method == 'POST':
        form = SolicitudForm(request.POST)
        solicitud = form.save(commit=False)
        solicitud.product_name = request.POST['product_name']
        solicitud.status = request.POST['status']
        solicitud.dia = request.POST['dia']
        solicitud.mes = request.POST['mes']
        solicitud.anio = request.POST['anio']
        solicitud.product_cant = request.POST['product_cant']
        solicitud.notes = request.POST['notes']
        solicitud.asesor = Person.objects.get(id=request.POST['asesor'])
        solicitud.save()
        messages.success(request, 'El registro ha sido ingresado.')
    else:
        form = SolicitudForm(request)

    return render(request, 'sellingsapp/solicitud_add.html', {'form': form})


# ---------------------------------------------------------------------------
#    Utiliza una vista basada en clase inyectando la clase Createview
# ---------------------------------------------------------------------------
# class campaignAdd(CreateView):
#     model = Campaign
#     fields = ['title', 'url', 'status', 'mes', 'anio', 'notes', 'num_campaign']
#     template_name = 'sellingsapp/campaign_add.html'

# ---------------------------------------------------------------------------
#    Utiliza la vista basada en clase inyectando la clase UpdateView
# ---------------------------------------------------------------------------
# class campaignDetail(UpdateView):
#     model = Campaign
#     fields = ['title', 'url', 'status', 'mes', 'anio', 'notes', 'num_campaign']
#     template_name = 'sellingsapp/campaign_detail.html'

#     def form_valid(self, form):
#         campaign = form.save(commit=False)
#         campaign.save()
#         messages.success(self.request, 'El registro ha sido actualizado.')
#         return self.render_to_response(self.get_context_data(form=form))


def solicitudDetail(request, pk):
    solicitud = get_object_or_404(Solicitud, pk=pk)

    if request.method == "POST":
        form = SolicitudForm(request.POST, instance=solicitud)
        solicitud = form.save(commit=False)
        solicitud.product_name = request.POST['product_name']
        solicitud.status = request.POST['status']
        solicitud.dia = request.POST['dia']
        solicitud.mes = request.POST['mes']
        solicitud.anio = request.POST['anio']
        solicitud.product_cant = request.POST['product_cant']
        solicitud.notes = request.POST['notes']
        solicitud.asesor = Person.objects.get(id=request.POST['asesor'])
        solicitud.save()
        messages.success(request, 'El registro ha sido actualizado.')

    form = SolicitudForm(request, instance=solicitud)

    return render(request, 'sellingsapp/solicitud_detail.html', {'form': form})


# -----------------------------------------------------------------------------
#               Función para eliminar una solicitud
# -----------------------------------------------------------------------------
def solicitudDelete(request, id_solicitud):
    # busca el modelo idenficado por el id
    solicitud_delete = get_object_or_404(Solicitud, pk=id_solicitud)
    solicitud_delete.delete()
    custom_message = " | "+solicitud_delete.product_name + " | "
    messages.success(request, "El registro " + str(id_solicitud) +
                     "-" + custom_message+" ha sido eliminado")

    return redirect('solicitudList')


def metaAdd(request):
    if request.method == 'POST':
        form = MetaForm(request.POST)
        if form.is_valid():
            if (getMeta(request.POST['mes'],request.POST['anio'],request.POST['canal_venta']).exists()==False):
                meta = form.save(commit=False)
                meta.meta_ingresada = request.POST['meta_ingresada']
                meta.meta_instalada = request.POST['meta_instalada']
                meta.mes = request.POST['mes']
                meta.anio = request.POST['anio']
                meta.canal_venta = request.POST['canal_venta']
                meta.save()
                messages.success(request, 'El registro ha sido ingresado!.')
                form = MetaForm()
            else:
                messages.error(request, 'Ya existe una meta para el mes indicado!.')


    else:
        form = MetaForm()

    return render(request, 'sellingsapp/metas_add.html', {'form': form})

class metaIndex(ListView):
    model = Metas
    template_name = 'sellingsapp/metas_list.html'
    context_object_name = 'metas_list'
    paginate_by = 7
    ordering = ['id']


class metaDetail(UpdateView):
    model = Metas
    fields = ['id', 'meta_ingresada', 'meta_instalada',
              'mes', 'anio', 'canal_venta']
    template_name = 'sellingsapp/metas_detail.html'

    def form_valid(self, form):
        meta = form.save(commit=False)
        objMeta = getMeta(meta.mes,meta.anio,meta.canal_venta)

        if (objMeta.exists()==True):
            if (objMeta[0].id == meta.id):
                meta.save()
                messages.success(self.request, 'El registro ha sido actualizado!.')
            else:
                messages.error(self.request, 'Ya existe una meta para el mes indicado!.')
        else:
            meta.save()
            messages.success(self.request, 'El registro ha sido actualizado!.')



        return self.render_to_response(self.get_context_data(form=form))

def metaDelete(request, id_meta):
    # busca el modelo idenficado por el id
    meta_delete = get_object_or_404(Metas, pk=id_meta)
    meta_delete.delete()
    custom_message = " | "+meta_delete.mes + \
        " " + str(meta_delete.anio) + " | "
    messages.success(request, "El registro " + str(id_meta) +
                     "-" + custom_message+" ha sido eliminado")

    return redirect('metaList')

