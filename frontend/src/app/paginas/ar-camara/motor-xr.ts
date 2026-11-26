import type { PerspectiveCamera, Quaternion, Scene, Vector3, WebGLRenderer } from 'three';

interface DatosCamara {
  canvas: HTMLCanvasElement;
  videoWidth: number;
  videoHeight: number;
  orientation: number;
}

export interface ModuloCamara {
  name: string;
  onAttach?: (datos: DatosCamara) => void;
  onDetach?: () => void;
  onStart?: (datos: DatosCamara) => void;
  onUpdate?: () => void;
  onCameraStatusChange?: (datos: { status: string; video?: HTMLVideoElement }) => void;
  onVideoSizeChange?: (datos: { videoWidth: number; videoHeight: number }) => void;
  onCanvasSizeChange?: () => void;
  onDeviceOrientationChange?: (datos: { orientation: number }) => void;
  onException?: (error: unknown) => void;
  listeners?: { event: string; process: (evento: { detail: { status: string } }) => void }[];
}

export interface Xr8 {
  loadChunk(nombre: 'slam'): Promise<void>;
  addCameraPipelineModules(modulos: ModuloCamara[]): void;
  clearCameraPipelineModules(): void;
  run(opciones: { canvas: HTMLCanvasElement }): void;
  stop(): void;
  GlTextureRenderer: { pipelineModule(): ModuloCamara };
  Threejs: {
    pipelineModule(): ModuloCamara;
    xrScene(): { scene: Scene; camera: PerspectiveCamera; renderer: WebGLRenderer };
  };
  XrController: {
    pipelineModule(): ModuloCamara;
    updateCameraProjectionMatrix(origen: { origin: Vector3; facing: Quaternion }): void;
  };
}

let motor: Promise<Xr8> | undefined;

export function cargarMotor(): Promise<Xr8> {
  motor ??= new Promise<Xr8>((resolve, reject) => {
    window.addEventListener('xrloaded', () => resolve((window as unknown as { XR8: Xr8 }).XR8), { once: true });
    const script = document.createElement('script');
    script.src = '/xr/xr.js';
    script.async = true;
    script.onerror = () => {
      motor = undefined;
      reject(new Error('xr'));
    };
    document.head.append(script);
  }).then(async (xr8) => {
    await xr8.loadChunk('slam');
    return xr8;
  });
  return motor;
}

// ajusta el canvas a la pantalla recortando el video sin pasar la resolucion del dispositivo
export function lienzoCompleto(): ModuloCamara {
  let lienzo: HTMLCanvasElement | null = null;
  let orientacion = 0;
  let esperas = 0;
  const video = { ancho: 0, alto: 0 };

  const ajustar = () => {
    if (!lienzo) return;
    const ancho = innerWidth * devicePixelRatio;
    const alto = innerHeight * devicePixelRatio;
    // espera a que la ventana termine de girar
    const vertical = orientacion === 0 || orientacion === 180;
    if (vertical === ancho > alto && esperas++ < 30) {
      requestAnimationFrame(ajustar);
      return;
    }
    esperas = 0;
    const pantallaLargo = Math.max(ancho, alto);
    const pantallaCorto = Math.min(ancho, alto);
    const proporcion = pantallaLargo / pantallaCorto;
    const videoLargo = Math.max(video.ancho, video.alto);
    const videoCorto = Math.min(video.ancho, video.alto);
    let largo = videoLargo;
    let corto = Math.round(videoLargo / proporcion);
    if (corto > videoCorto) {
      corto = videoCorto;
      largo = Math.round(videoCorto * proporcion);
    }
    if (corto > pantallaCorto || largo > pantallaLargo) {
      corto = pantallaCorto;
      largo = pantallaLargo;
    }
    lienzo.style.width = '100%';
    lienzo.style.height = '100%';
    lienzo.width = ancho > alto ? largo : corto;
    lienzo.height = ancho > alto ? corto : largo;
  };

  return {
    name: 'lienzocompleto',
    onAttach: ({ canvas, orientation, videoWidth, videoHeight }) => {
      lienzo = canvas;
      orientacion = orientation;
      video.ancho = videoWidth;
      video.alto = videoHeight;
      ajustar();
    },
    onDetach: () => {
      lienzo = null;
    },
    onCameraStatusChange: ({ status, video: elemento }) => {
      if (status !== 'hasVideo' || !elemento) return;
      video.ancho = elemento.videoWidth;
      video.alto = elemento.videoHeight;
    },
    onVideoSizeChange: ({ videoWidth, videoHeight }) => {
      video.ancho = videoWidth;
      video.alto = videoHeight;
      ajustar();
    },
    onDeviceOrientationChange: ({ orientation }) => {
      orientacion = orientation;
      ajustar();
    },
    onCanvasSizeChange: ajustar,
    // el renderer de three cambia el estilo del canvas al redimensionar
    onUpdate: () => {
      if (lienzo && (lienzo.style.width !== '100%' || lienzo.style.height !== '100%')) ajustar();
    },
  };
}
