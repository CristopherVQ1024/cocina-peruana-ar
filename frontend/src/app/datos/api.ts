import { HttpClient } from '@angular/common/http';
import { Injectable, inject } from '@angular/core';
import { Idioma, Mensaje, Plato, PlatoResumen, RespuestaAsistente } from './modelos';

@Injectable({ providedIn: 'root' })
export class Api {
  private readonly http = inject(HttpClient);

  platos() {
    return this.http.get<PlatoResumen[]>('/api/platos');
  }

  plato(id: string, idioma: Idioma) {
    return this.http.get<Plato>(`/api/platos/${id}`, { params: { idioma } });
  }

  preguntar(platoId: string, pregunta: string, idioma: Idioma, paso: number, historial: Mensaje[]) {
    return this.http.post<RespuestaAsistente>('/api/asistente', {
      plato_id: platoId,
      pregunta,
      idioma,
      paso,
      historial: historial.slice(-6).map(({ rol, texto }) => ({ rol, texto })),
    });
  }
}
