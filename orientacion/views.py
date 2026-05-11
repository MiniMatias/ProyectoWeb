from django.shortcuts import render, redirect 
from django.http import JsonResponse
from django.core.exceptions import ValidationError
from .models import AreaEspecialidad, Especialidad, Estudiante, Pregunta, RespuestaHabilidad

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
            
            # 🚨 REDIRECCIÓN ESTRICTA: Guardamos el ID de forma segura en el servidor
            request.session['estudiante_id'] = nuevo_estudiante.id
            # Forzamos al navegador a ir a la ruta del test
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
    # Endpoint para cargar el segundo dropdown dinámicamente
    area_id = request.GET.get('area_id')
    if area_id and area_id.isdigit():
        especialidades = Especialidad.objects.filter(area_id=area_id).order_by('nombre')
        # Convertimos el QuerySet a una lista de diccionarios para que sea serializable a JSON
        data = list(especialidades.values('id', 'nombre'))
        return JsonResponse(data, safe=False)
    return JsonResponse({'error': 'ID inválido'}, status=400)

def realizar_test(request):
    # Validamos que nadie entre a esta URL escribiéndola a mano si no se ha registrado
    estudiante_id = request.session.get('estudiante_id')
    if not estudiante_id:
        return redirect('registro') # Lo devolvemos al inicio
    
    estudiante = Estudiante.objects.get(id=estudiante_id)
    preguntas = Pregunta.objects.all().order_by('habilidad__nombre')

    if request.method == 'POST':
        # Los datos llegan al sistema. Iteramos sobre las preguntas para atrapar respuestas.
        for pregunta in preguntas:
            # El HTML enviará inputs con el nombre "pregunta_1", "pregunta_2", etc.
            puntaje = request.POST.get(f'pregunta_{pregunta.id}')
            
            if puntaje and puntaje.isdigit():
                # Guardamos la respuesta en la base de datos
                RespuestaHabilidad.objects.update_or_create(
                    estudiante=estudiante,
                    pregunta=pregunta,
                    defaults={'puntaje': int(puntaje)}
                )
        
        # AQUÍ ES DONDE ENTRARÁ EL CÁLCULO FINAL. 
        del request.session['estudiante_id']
        return render(request, 'orientacion/exito_temporal.html', {'estudiante': estudiante})

    return render(request, 'orientacion/test.html', {
        'estudiante': estudiante,
        'preguntas': preguntas
    })