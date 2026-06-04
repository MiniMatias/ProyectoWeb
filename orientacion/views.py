import json
from django.shortcuts import render, redirect 
from django.http import JsonResponse
from django.core.exceptions import ValidationError
from .models import AreaEspecialidad, Especialidad, Estudiante, Pregunta, RespuestaHabilidad

# SISTEMA DE REGISTRO ORIGINAL

def registro_estudiante(request):
    areas = AreaEspecialidad.objects.all().order_by('nombre')
    error_msg = None

    if request.method == 'POST':
        cedula_ingresada = request.POST.get('cedula')
        nombre_ingresado = request.POST.get('nombre_completo')
        area_id = request.POST.get('area')
        especialidad_id = request.POST.get('especialidad')

        try:
            area_obj = AreaEspecialidad.objects.get(id=area_id)
            especialidad_obj = Especialidad.objects.get(id=especialidad_id)

            nuevo_estudiante = Estudiante(
                cedula=cedula_ingresada,
                nombre_completo=nombre_ingresado,
                area_interes=area_obj,
                especialidad_especifica=especialidad_obj
            )
            nuevo_estudiante.save()
            
            request.session['estudiante_id'] = nuevo_estudiante.id
            return redirect('realizar_test') 

        except ValidationError as e:
            error_msg = e.messages[0] if hasattr(e, 'messages') else str(e)
        except Exception as e:
            error_msg = "Ocurrió un error al procesar la solicitud."

    return render(request, 'orientacion/registro.html', {
        'areas': areas,
        'error_msg': error_msg
    })

def cargar_especialidades(request):
    area_id = request.GET.get('area_id')
    if area_id and area_id.isdigit():
        especialidades = Especialidad.objects.filter(area_id=area_id).order_by('nombre')
        data = list(especialidades.values('id', 'nombre'))
        return JsonResponse(data, safe=False)
    return JsonResponse({'error': 'ID inválido'}, status=400)

def realizar_test(request):
    estudiante_id = request.session.get('estudiante_id')
    if not estudiante_id:
        return redirect('registro') 
    
    estudiante = Estudiante.objects.get(id=estudiante_id)
    preguntas = Pregunta.objects.all().order_by('habilidad__nombre')

    if request.method == 'POST':
        for pregunta in preguntas:
            puntaje = request.POST.get(f'pregunta_{pregunta.id}')
            if puntaje and puntaje.isdigit():
                RespuestaHabilidad.objects.update_or_create(
                    estudiante=estudiante,
                    pregunta=pregunta,
                    defaults={'puntaje': int(puntaje)}
                )
                
        # Una vez completado, en lugar de mostrar exito_temporal, 
        # lo enviamos directamente a su nuevo dashboard analítico.
        return redirect('dashboard')

    return render(request, 'orientacion/test.html', {
        'estudiante': estudiante,
        'preguntas': preguntas
    })

# 2. (DASHBOARD)

def acceso_dashboard(request):
    """Actúa como un login falso basado en la cédula."""
    if request.method == 'POST':
        cedula_ingresada = request.POST.get('cedula')
        estudiante = Estudiante.objects.filter(cedula=cedula_ingresada).first()
        
        if estudiante:
            request.session['estudiante_id'] = estudiante.id
            return redirect('dashboard')
        else:
            return render(request, 'orientacion/acceso.html', {'error': 'Cédula no encontrada. Regístrate primero.'})
            
    return render(request, 'orientacion/acceso.html')

def dashboard(request):
    """El panel principal del estudiante con sus gráficos."""
    estudiante_id = request.session.get('estudiante_id')
    if not estudiante_id:
        return redirect('acceso_dashboard')
        
    estudiante = Estudiante.objects.get(id=estudiante_id)
    respuestas = RespuestaHabilidad.objects.filter(estudiante=estudiante).select_related('pregunta__habilidad')
    
    # Si no ha dado el test, lo mandamos a la vista de estado vacío
    if not respuestas.exists():
        return render(request, 'orientacion/dashboard_vacio.html', {'estudiante': estudiante})
        
    # Procesamiento matemático para el Gráfico Radial de Chart.js
    habilidades_data = {}
    for r in respuestas:
        hab_nombre = r.pregunta.habilidad.nombre
        if hab_nombre not in habilidades_data:
            habilidades_data[hab_nombre] = {'suma': 0, 'conteo': 0}
        
        porcentaje = (r.puntaje - 1) * 25
        habilidades_data[hab_nombre]['suma'] += porcentaje
        habilidades_data[hab_nombre]['conteo'] += 1
        
    labels = list(habilidades_data.keys())
    data_points = [round(data['suma'] / data['conteo'], 1) for data in habilidades_data.values()]
    
    contexto = {
        'estudiante': estudiante,
        'respuestas': respuestas,
        'chart_labels': json.dumps(labels), 
        'chart_data': json.dumps(data_points) 
    }
    
    return render(request, 'orientacion/dashboard.html', contexto)