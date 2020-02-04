from time import gmtime, strftime
from django.shortcuts import render, HttpResponse, get_object_or_404, redirect, render_to_response
from django.urls import reverse_lazy
from django.contrib import messages

# Importación de modelos
from .models import Person
from .models import Solicitud
from .models import Metas
from .models import Tarifas
from .models import Feriados

# Importación de formularios
from .forms import PersonForm
from .forms import SolicitudForm
from .forms import MetaForm
from .forms import TarifaForm
from .forms import FeriadoForm

# Importación de vistas basadas en clases
from django.views.generic.list import ListView
from django.views.generic.edit import UpdateView
from django.views.generic import CreateView

from django.core.paginator import Paginator
from datetime import datetime, timedelta, date
import calendar
import json
import xlwt

# ----------------------------------------------------------------------------
#   Vista basada en clase para listar las personas o vendedores registrados
# -----------------------------------------------------------------------------


class personIndex(ListView):
    model = Person
    template_name = 'sellingsapp/person_list.html'
    context_object_name = 'person_list'
    paginate_by = 7
    ordering = ['id']

# ------------------------------------------------------------
#       Método o función para crear una persona o vendedor
# -------------------------------------------------------------


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
            person.canal_de_venta = request.POST['canal_de_venta']
            person.save()
            messages.success(request, 'El registro ha sido ingresado.')
            form = PersonForm()
    else:
        form = PersonForm()

    return render(request, 'sellingsapp/person_add.html', {'form': form})


# ------------------------------------------------------------
#       Vista basada en clase que utiliza la clase UpdateView
#       para editar una persona o vendendor
# -------------------------------------------------------------
class personDetail(UpdateView):
    model = Person
    fields = ['cc_id', 'first_name', 'last_name',
              'celphone', 'address', 'email', 'canal_de_venta']
    template_name = 'sellingsapp/person_detail.html'

    def form_valid(self, form):
        person = form.save(commit=False)
        person.save()
        messages.success(self.request, 'El registro ha sido actualizado.')
        return self.render_to_response(self.get_context_data(form=form))

# ---------------------------------------------------------
#            Método que elimina una persona o vendedor
# ----------------------------------------------------------


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

    query_person = ''  # Se establece un query para admin o usuario común

    # if (request.user.get_username() == "@dm1n" or request.user.get_username() == "supervis@r"):
    search_cc_id = request.GET.get('search_cc_id')

    if search_cc_id != '':
        query_person = "Person.objects.get(cc_id=search_cc_id)"
    else:
        search_email = ""

    # Buscamos el email asociado al cc_id o al usuario de la sesión
    if query_person != '':
        try:
            ObjPerson = eval(query_person)
            search_email = ObjPerson.email
        except Person.DoesNotExist:
            search_email = ""

    # Consultamos la cantidad de ventas realizadas (ingresadas e instaladas)
    if search_email != '' and search_email != None:
        cant_solicitadas = proyectionReview(
            search_email, search_mes[today.month-1], today.day, 'solicitado')
        cant_instaladas = proyectionReview(
            search_email, search_mes[today.month-1], today.day, 'instalado')
    else:
        result = {}
        return render(request, template_name, result)

    # Obtenemos días hábiles,días transcurridos,y total de ventas
    dias_habiles = validDays(lastDayMonth())
    dias_transcurridos = validDays("")-1
    tot_ingresadas = cant_solicitadas+cant_instaladas

    # Calculamos la proyección de ventas ingresadas e instaladas
    if dias_transcurridos == 0:
        proyeccion_ingresadas = 0
        proyeccion_instaladas = 0
    else:
        proyeccion_ingresadas = (
            (cant_solicitadas+cant_instaladas)/dias_transcurridos)*dias_habiles
        proyeccion_instaladas = (
            cant_instaladas/dias_transcurridos)*dias_habiles

    # Calculamos el porcentaje de ventas ingresadas e instaladas con respecto a la meta
    if (request.GET.get('meta_instalada') != "" and request.GET.get('meta_ingresada') != "" and int(request.GET.get('meta_instalada')) > 0 and int(request.GET.get('meta_ingresada')) > 0):
        meta_instalada = int(request.GET.get('meta_instalada'))
        meta_ingresada = int(request.GET.get('meta_ingresada'))
        porc_meta_ingresadas = (proyeccion_ingresadas/meta_ingresada)*100
        porc_meta_instaladas = (proyeccion_instaladas/meta_instalada)*100
    else:
        meta_ingresada = 0
        meta_instalada = 0
        porc_meta_ingresadas = 0
        porc_meta_instaladas = 0

    # calcula el valor de la tarifa de comisión
    comision = getComision(cant_instaladas)

    if comision != []:
        tabla_comision = comision
        rango_comision = comision["nombre_rango"]
    else:
        valor_comision = 0
        rango_comision = 'no aplica'
        tabla_comision = 'no aplica'

    return render(request, template_name,
                  {"dias_habiles": dias_habiles,
                   "dias_transcurridos": dias_transcurridos,
                   "cant_instaladas": cant_instaladas,
                   "cant_solicitadas": tot_ingresadas,
                   "proyeccion_ingre": format(proyeccion_ingresadas, ".2f"),
                   "proyeccion_instal": format(proyeccion_instaladas, ".2f"),
                   "meta_ingresadas": meta_ingresada,
                   "meta_instaladas": meta_instalada,
                   "porc_meta_ingresadas": format(porc_meta_ingresadas, ".2f"),
                   "porc_meta_instaladas": format(porc_meta_instaladas, ".2f"),
                   "nombre_rango": rango_comision,
                   "tabla_comision": tabla_comision
                   })


#----------------------------------------------------------#
#   Obtiene la comisión a partir del rango de venta
# -----------------------------------------------------------
def getComision(cant_instaladas):

    array_range = {}

    try:
        sql_query = "limite_inf <= %s and limite_sup >=%s"
        result = Tarifas.objects.extra(where=[sql_query], params=[
                                       cant_instaladas, cant_instaladas])
    except Tarifas.DoesNotExist:
        result = []

    if result.exists():

        for record in result:
            array_range[record.porce_title] = format(
                (int(record.comision) * cant_instaladas), ",d")
            array_range["nombre_rango"] = record.nombre_rango
            array_range["escala"] = str(
                record.limite_inf)+"-"+str(record.limite_sup)

        return array_range

    return []
# ---------------------------------------------------------------------------
#       Calcula la proyección de cada asesor
# ---------------------------------------------------------------------------


def proyectionReview(user_email, mes, dia, status):
    tot_status = 0
    try:
        ObjPerson = Person.objects.get(email=user_email)
        asesor_id = ObjPerson.id
    except Person.DoesNotExist:
        return 0

    if user_email != '':
        sql_query = "status=%s and asesor_id=%s and mes=%s and dia != %s"
        result = Solicitud.objects.extra(where=[sql_query], params=[
                                         status, asesor_id, mes, dia])
        for record in result:
            tot_status += record.product_cant

    return tot_status


# ----------------------------------------------------------------------------
#       Función para obtener días hábiles del  mes transcurridos hasta hora
# ----------------------------------------------------------------------------
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
    formato = '%Y-%m-%d'
    hollidays = '[{"feriado":"14/10/2019"}]'
    dias_feriados = json.loads(hollidays)

    if existFeriado(datetime.strftime(dia, formato)) == True:
        return True

    return False

# -----------------------------------------------------------------------
#       Función que obtiene el último día del mes
# -----------------------------------------------------------------------


def lastDayMonth():
    today = date.today()
    day = calendar.monthrange(int(strftime("%Y", gmtime())),
                              int(strftime("%m", gmtime())))[1]
    lastDate = str(day)+"/"+str(today.month)+"/"+str(today.year)
    return lastDate

# -----------------------------------------------------------------------
#   Función para verificar si ya existe la meta resgistrada
# -------------------------------------------------------------------------


def getMeta(mes_meta, anio_meta, canal_venta):

    try:
        sql_query = "mes=%s and anio=%s and canal_venta=%s"
        result = Metas.objects.extra(where=[sql_query], params=[
                                     mes_meta, anio_meta, canal_venta])
    except Metas.DoesNotExist:
        result = []

    return result

# -------------------------------------------------------------------------
#    Función para verificar si ya existe la TARIFA resgistrada
# -------------------------------------------------------------------------


def getTarifa(nombre_rango, porce_title):

    try:
        sql_query = "nombre_rango=%s and porce_title=%s"
        result = Tarifas.objects.extra(where=[sql_query], params=[
                                       nombre_rango, porce_title])
    except Tarifas.DoesNotExist:
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
                where=[search_field+"= %s"], params=[search_value])
            return result

        try:
            ObjPerson = Person.objects.get(email=user_email)
            asesor_id = ObjPerson.id

        except Person.DoesNotExist:
            result = []

        if search_value != '':
            result = Solicitud.objects.extra(
                where=[search_field+"=%s and asesor_id=%s"], params=[search_value, asesor_id])
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
        solicitud.nomcliente = request.POST['nomcliente']
        solicitud.celcliente = request.POST['celcliente']
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
        solicitud.nomcliente = request.POST['nomcliente']
        solicitud.celcliente = request.POST['celcliente']
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


# ---------------------------------------------------------------------------
#       Funcion para registrar una nueva Meta para diferente canal de venta
# ----------------------------------------------------------------------------
def metaAdd(request):
    if request.method == 'POST':
        form = MetaForm(request.POST)
        if form.is_valid():
            if (getMeta(request.POST['mes'], request.POST['anio'], request.POST['canal_venta']).exists() == False):
                meta = form.save(commit=False)

                if (meta.meta_ingresada != 0 and meta.meta_instalada != 0):
                    meta.meta_ingresada = request.POST['meta_ingresada']
                    meta.meta_instalada = request.POST['meta_instalada']
                    meta.mes = request.POST['mes']
                    meta.anio = request.POST['anio']
                    meta.canal_venta = request.POST['canal_venta']
                    meta.save()
                    messages.success(
                        request, 'El registro ha sido ingresado!.')
                    form = MetaForm()
                else:
                    messages.error(
                        request, 'Las metas no pueden tener un valor  = 0 (cero)!.')
            else:
                messages.error(
                    request, 'Ya existe una meta para el mes indicado!.')

    else:
        form = MetaForm()

    return render(request, 'sellingsapp/metas_add.html', {'form': form})

# ---------------------------------------------------------
#   Vista basada en clase para listar las metas de venta
# ------------------------------------------------------------


class metaIndex(ListView):
    model = Metas
    template_name = 'sellingsapp/metas_list.html'
    context_object_name = 'metas_list'
    paginate_by = 7
    ordering = ['id']


# -----------------------------------------------------------
#   Vista basada en clase para Editar las metas de venta
# ------------------------------------------------------------
class metaDetail(UpdateView):
    model = Metas
    fields = ['id', 'meta_ingresada', 'meta_instalada',
              'mes', 'anio', 'canal_venta']
    template_name = 'sellingsapp/metas_detail.html'

    def form_valid(self, form):
        meta = form.save(commit=False)
        objTarifa = getMeta(meta.mes, meta.anio, meta.canal_venta)

        if (meta.meta_ingresada != 0 and meta.meta_instalada != 0):

            if (objTarifa.exists() == True):
                if (objTarifa[0].id == meta.id):
                    meta.save()
                    messages.success(
                        self.request, 'El registro ha sido actualizado!.')
                else:
                    messages.error(
                        self.request, 'Ya existe una meta para el mes indicado!.')
            else:
                meta.save()
                messages.success(
                    self.request, 'El registro ha sido actualizado!.')
        else:
            messages.error(
                self.request, 'Las metas no pueden tener un valor  = 0 (cero)!.')

        return self.render_to_response(self.get_context_data(form=form))


# ------------------------------------------------------------
#       Función para eliminar las metas registradas
# ------------------------------------------------------------
def metaDelete(request, id_meta):
    # busca el modelo idenficado por el id
    meta_delete = get_object_or_404(Metas, pk=id_meta)
    meta_delete.delete()
    custom_message = " | "+meta_delete.mes + \
        " " + str(meta_delete.anio) + " | "
    messages.success(request, "El registro " + str(id_meta) +
                     "-" + custom_message+" ha sido eliminado")

    return redirect('metaList')

# ---------------------------------------------------------------------------
#       Funcion para registrar una nueva Meta para diferente canal de venta
# ----------------------------------------------------------------------------


def tarifaAdd(request):
    if request.method == 'POST':
        form = TarifaForm(request.POST)
        if form.is_valid():
            if (getTarifa(request.POST['nombre_rango'], request.POST['porce_title']).exists() == False):
                tarifa = form.save(commit=False)

                if (tarifa.limite_inf != 0 and tarifa.limite_sup != 0):

                    if(tarifa.limite_inf < tarifa.limite_sup):
                        tarifa.limite_inf = request.POST['limite_inf']
                        tarifa.limite_sup = request.POST['limite_sup']
                        tarifa.nombre_rango = request.POST['nombre_rango']
                        tarifa.porce_title = request.POST['porce_title']
                        tarifa.comision = request.POST['comision']
                        tarifa.save()
                        messages.success(
                            request, 'El registro ha sido ingresado!.')
                        form = TarifaForm()
                    else:
                        messages.error(
                            request, 'El límite inferior del rango debe ser menor al límite superior!')

                else:
                    messages.error(
                        request, 'Los  límites de las tarifas no pueden tener un valor  = 0 (cero)!.')
            else:
                messages.error(
                    request, 'Ya existe una tarifa registrada para el rango límite indicado!.')

    else:
        form = TarifaForm()

    return render(request, 'sellingsapp/tarifas_add.html', {'form': form})


# ----------------------------------------------------------------------
#   Vista basada en clase para listar las TARIFAS de comision de ventas
# ----------------------------------------------------------------------
class tarifaIndex(ListView):
    model = Tarifas
    template_name = 'sellingsapp/tarifas_list.html'
    context_object_name = 'tarifas_list'
    paginate_by = 7
    ordering = ['id']

# -----------------------------------------------------------
#   Vista basada en clase para Editar las metas de venta
# ------------------------------------------------------------


class tarifaDetail(UpdateView):
    model = Tarifas
    fields = ['id', 'limite_inf', 'limite_sup',
              'nombre_rango', 'porce_title', 'comision']
    template_name = 'sellingsapp/tarifas_detail.html'

    def form_valid(self, form):
        isValid = True
        tarifa = form.save(commit=False)
        objTarifa = getTarifa(tarifa.nombre_rango, tarifa.porce_title)

        if (tarifa.limite_inf == 0 and tarifa.limite_sup == 0):
            isValid = False
            messages.error(
                self.request, 'Los  límites de las tarifas no pueden tener un valor  = 0 (cero)!.')

        if (objTarifa.exists() == True):
            if (objTarifa[0].id != tarifa.id):
                isValid = False
                messages.error(
                    self.request, 'Ya existe una tarifa registrada para el rango límite indicado!.')

        if(tarifa.limite_inf > tarifa.limite_sup):
            isValid = False
            messages.error(
                self.request, 'El límite inferior del rango debe ser menor al límite superior!')

        if isValid == True:
            tarifa.save()
            messages.success(self.request, 'El registro ha sido actualizado!.')

        return self.render_to_response(self.get_context_data(form=form))


# ------------------------------------------------------------
#       Función para Eliminar las tarifas registradas
# ------------------------------------------------------------
def tarifaDelete(request, id_tarifa):
    # busca el modelo idenficado por el id
    tarifa_delete = get_object_or_404(Tarifas, pk=id_tarifa)
    tarifa_delete.delete()
    custom_message = " | rango "+tarifa_delete.nombre_rango + \
        " Comisión " + str(tarifa_delete.comision) + " | "
    messages.success(request, "El registro " + str(id_tarifa) +
                     "-" + custom_message+" ha sido eliminado")

    return redirect('tarifaList')


# ---------------------------------------------------------------
#                Función para adicionar días Off
# --------------------------------------------------------------
def feriadoAdd(request):
    if request.method == 'POST':
        form = FeriadoForm(request.POST)

        if form.is_valid():
            if existFeriado(request.POST['fecha'])==False:
                feriado = form.save(commit=False)
                feriado.fecha = request.POST['fecha']
                feriado.notes = request.POST['notes']
                feriado.save()
                messages.success(request, 'El registro ha sido ingresado!.')
                form = FeriadoForm()
            else:
                messages.error(request, 'La fecha indicada ya existe')

    else:
        form = FeriadoForm()

    return render(request, 'sellingsapp/feriados_add.html', {'form': form})

# -------------------------------------------------------------------------------------
#     Función para verificar si una fecha ya se encuentra ingresada como feriado
# -------------------------------------------------------------------------------------
def existFeriado(fecha,pk='none'):
    try:
       if pk=='none':
            sql_query = "fecha=%s"
            result = Feriados.objects.extra(where=[sql_query], params=[fecha])
       else:
            sql_query = "fecha=%s and id!=%s"
            result = Feriados.objects.extra(where=[sql_query], params=[fecha,pk])

    except Feriados.DoesNotExist:
        result = []

    if (result.exists() == True):
        return True
    else:
        return False


# ------------------------------------------------------------------
#   Vista basada en clase para Editar los días feriados o días Off
# ------------------------------------------------------------------

class feriadoDetail(UpdateView):
    model = Feriados
    fields = ['fecha','notes']
    template_name = 'sellingsapp/feriados_detail.html'

    def form_valid(self, form):
        feriado = form.save(commit=False)

        if (existFeriado(self.request.POST['fecha'],feriado.id)):
            messages.error(self.request, 'La fecha indicada ya se encuentra registrada!')
        else:
            feriado.save()
            messages.success(self.request, 'El registro ha sido actualizado!.')

        return self.render_to_response(self.get_context_data(form=form))


# ----------------------------------------------------------------------
#   Vista basada en clase para listar los días feriados o días OFF
# ----------------------------------------------------------------------
class feriadoIndex(ListView):
    model = Feriados
    template_name = 'sellingsapp/feriados_list.html'
    context_object_name = 'feriados_list'
    paginate_by = 7
    ordering = ['id']

# ---------------------------------------------------------------------
#    Función para Eliminar los días feriados o dias Off registrados
# ---------------------------------------------------------------------
def feriadoDelete(request, id_feriado):
    # busca el modelo idenficado por el id
    feriado_delete = get_object_or_404(Feriados, pk=id_feriado)
    feriado_delete.delete()
    custom_message = " | fecha "+str(feriado_delete.fecha) 
    messages.success(request, "El registro " + str(id_feriado) +
                     "-" + custom_message+" ha sido eliminado")

    return redirect('feriadoList')

#----------------------------------------------------------------------
#     Función para exportar las ventas registradas a EXCEL
# ---------------------------------------------------------------------
def export_solicitudes_xls(request):
    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename="solicitudes.xls"'

    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet('Solicitudes')

    # Sheet header, first row
    row_num = 0

    font_style = xlwt.XFStyle()
    font_style.font.bold = True

    columns = ['Producto', 'Estado', 'dia', 'mes','anio','notes','Rel.productos','Asesor','Cliente','cel. cliente' ]

    for col_num in range(len(columns)):
        ws.write(row_num, col_num, columns[col_num], font_style)

    # Sheet body, remaining rows
    font_style = xlwt.XFStyle()

    sql_query = "mes=%s and anio=%s"
    rows = Solicitud.objects.extra(where=[sql_query], params=[
        request.POST['search_mes_excel'], request.POST['anio']])

    # rows = Solicitud.objects.all().select_related('asesor')
   
    for row in rows:
        row_num = row_num + 1
        ws.write(row_num, 0, row.product_name, font_style)
        ws.write(row_num, 1, row.status, font_style)
        ws.write(row_num, 2, row.dia, font_style)
        ws.write(row_num, 3, row.mes, font_style)
        ws.write(row_num, 4, row.anio, font_style)
        ws.write(row_num, 5, row.notes, font_style)
        ws.write(row_num, 6, row.product_cant, font_style)
        ws.write(row_num, 7, row.asesor.cc_id, font_style)
        ws.write(row_num, 8, row.nomcliente, font_style) 
        ws.write(row_num, 9, row.celcliente, font_style)


    wb.save(response)
    return response






   

    
