import json
from django.shortcuts import render, redirect 
from django.http import JsonResponse
from django.core.exceptions import ValidationError
from .models import Especialidad, Estudiante, Pregunta, AreaEspecialidad
from .services import RegistroService, TestVocacionalService, EstudianteDashboardService
from .inference_engine import PromedioPonderadoStrategy

def registro_estudiante(request):
    areas = AreaEspecialidad.objects.all().order_by('nombre')
    error_msg = None

    if request.method == 'POST':
        try:
            estudiante = RegistroService.registrar_estudiante(
                cedula=request.POST.get('cedula', ''),
                nombre_completo=request.POST.get('nombre_completo', ''),
                area_id=request.POST.get('area', ''),
                especialidad_id=request.POST.get('especialidad', '')
            )
            request.session['estudiante_id'] = estudiante.id
            return redirect('realizar_test') 
        except ValidationError as e:
            error_msg = e.messages[0] if hasattr(e, 'messages') else str(e)
        except Exception:
            error_msg = "Ocurrió un error inesperado al procesar la solicitud."

    return render(request, 'orientacion/registro.html', {'areas': areas, 'error_msg': error_msg})

def cargar_especialidades(request):
    area_id = request.GET.get('area_id')
    if area_id and str(area_id).isdigit():
        especialidades = Especialidad.objects.filter(area_id=area_id).order_by('nombre')
        return JsonResponse(list(especialidades.values('id', 'nombre')), safe=False)
    return JsonResponse({'error': 'ID inválido'}, status=400)

def realizar_test(request):
    estudiante_id = request.session.get('estudiante_id')
    if not estudiante_id:
        return redirect('registro') 
    
    try:
        estudiante = Estudiante.objects.get(id=estudiante_id)
    except Estudiante.DoesNotExist:
        return redirect('registro')

    if request.method == 'POST':
        # Extracción segura: Filtramos basura de la web y construimos un diccionario tipado
        respuestas_puras = {}
        for key, value in request.POST.items():
            if key.startswith('pregunta_') and value.isdigit():
                try:
                    pregunta_id = int(key.split('_')[1])
                    respuestas_puras[pregunta_id] = int(value)
                except ValueError:
                    continue
                    
        TestVocacionalService.guardar_respuestas(estudiante, respuestas_puras)
        return redirect('dashboard')

    preguntas = Pregunta.objects.select_related('habilidad').order_by('habilidad__nombre')
    return render(request, 'orientacion/test.html', {'estudiante': estudiante, 'preguntas': preguntas})

def acceso_dashboard(request):
    if request.method == 'POST':
        estudiante = Estudiante.objects.filter(cedula=request.POST.get('cedula')).first()
        if estudiante:
            request.session['estudiante_id'] = estudiante.id
            return redirect('dashboard')
        return render(request, 'orientacion/acceso.html', {'error': 'Cédula no encontrada.'})
            
    return render(request, 'orientacion/acceso.html')

def dashboard(request):
    estudiante_id = request.session.get('estudiante_id')
    if not estudiante_id:
        return redirect('acceso_dashboard')
        
    try:
        estudiante = Estudiante.objects.select_related('area_interes', 'especialidad_especifica').get(id=estudiante_id)
    except Estudiante.DoesNotExist:
        return redirect('acceso_dashboard')
        
    servicio = EstudianteDashboardService(motor_inferencia=PromedioPonderadoStrategy())
    resultado = servicio.procesar_dashboard(estudiante)
    
    if resultado.get('vacio'):
        return render(request, 'orientacion/dashboard_vacio.html', {'estudiante': estudiante})
        
    return render(request, 'orientacion/dashboard.html', {
        'estudiante': estudiante,
        'chart_labels': json.dumps(resultado.get('labels', [])), 
        'chart_data': json.dumps(resultado.get('data_points', [])),
        'top_3': resultado.get('top_3', []),
        'error_inferencia': resultado.get('error_inferencia', False)
    })