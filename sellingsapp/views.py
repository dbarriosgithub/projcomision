from time import gmtime, strftime
from django.shortcuts import render, HttpResponse, get_object_or_404, redirect, render_to_response
from django.urls import reverse_lazy
from django.contrib import messages
from .models import Person
from .models import Solicitud
from .forms import PersonForm
from .forms import SolicitudForm
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
    paginate_by = 2
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
    paginate_by = 2
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

    if dias_transcurridos==0:
        dias_transcurridos=1;

    proyeccion_ingresadas = (
        (cant_solicitadas+cant_instaladas)/dias_transcurridos)*dias_habiles
    proyeccion_instaladas = (cant_instaladas/dias_transcurridos)*dias_habiles

    return render(request, template_name, {"proyeccion_ingre": proyeccion_ingresadas, "proyeccion_instal": proyeccion_instaladas})

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
    hollidays = '[{"feriado":"05/10/2019"},{"feriado":"08/10/2019"},{"feriado": "09/10/2019"}, {"feriado": "07/10/2019"}]'
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
#       Clase ListView que utiliza filter para búsqueda personalizada
# -----------------------------------------------------------------------


class searchSolicitud(ListView):
    model = Solicitud
    template_name = 'sellingsapp/solicitud_list.html'
    context_object_name = 'solicitud_list'
    paginate_by = 3
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
    if request.method == 'POST':
        form = SolicitudForm(request.POST)

        if form.is_valid():
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
            form = SolicitudForm()
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

# Create your views here.
