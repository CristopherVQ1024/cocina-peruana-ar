export type Idioma = 'es' | 'en' | 'pt' | 'fr';

export interface Ingrediente {
  nombre: string;
  cantidad: string;
}

export interface Paso {
  numero: number;
  titulo: string;
  descripcion: string;
  duracion_min: number;
  modelo: string;
}

export interface Plato {
  id: string;
  nombre: string;
  region: string;
  resumen: string;
  historia: string;
  porciones: number;
  ingredientes: Ingrediente[];
  pasos: Paso[];
}

export interface PlatoResumen {
  id: string;
  nombre: string;
  region: string;
  resumen: string;
  modelo: string;
}

export interface Mensaje {
  rol: 'usuario' | 'asistente';
  texto: string;
  fueraDeFicha?: boolean;
}

export interface RespuestaAsistente {
  respuesta: string;
  fuera_de_ficha: boolean;
}
