import {
  ChangeDetectionStrategy,
  Component,
  DestroyRef,
  ElementRef,
  afterNextRender,
  computed,
  effect,
  inject,
  input,
  linkedSignal,
  signal,
  viewChild,
} from '@angular/core';
import { rxResource } from '@angular/core/rxjs-interop';
import { Meta } from '@angular/platform-browser';
import { HlmButtonImports } from '@spartan-ng/helm/button';
import { catchError, throwError } from 'rxjs';
import * as THREE from 'three';
import { Api } from '../../datos/api';
import { esAndroid } from '../../datos/dispositivo';
import { IdiomaService } from '../../datos/idioma';
import { EscenaAr } from './escena-ar';
import { ModuloCamara, Xr8, cargarMotor, lienzoCompleto } from './motor-xr';

// altura inicial supuesta del celular sobre la mesa en metros
const ALTURA = 0.4;

@Component({
  selector: 'app-ar-camara',
  imports: [HlmButtonImports],
  templateUrl: './ar-camara.html',
  styleUrl: './ar-camara.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class ArCamara {
  readonly id = input.required<string>();
  readonly paso = input.required<string>();

  private readonly api = inject(Api);
  private readonly idioma = inject(IdiomaService);
  private readonly meta = inject(Meta);
  protected readonly t = this.idioma.t;
  private readonly lienzo = viewChild.required<ElementRef<HTMLCanvasElement>>('lienzo');

  protected readonly plato = rxResource({
    params: () => ({ id: this.id(), idioma: this.idioma.actual() }),
    stream: ({ params }) =>
      this.api
        .plato(params.id, params.idioma)
        .pipe(catchError((error) => (params.idioma === 'es' ? throwError(() => error) : this.api.plato(params.id, 'es')))),
  });
  protected readonly pasos = computed(() => (this.plato.hasValue() ? this.plato.value().pasos : []));
  protected readonly indice = linkedSignal(() => Math.max(0, (Number(this.paso()) || 1) - 1));
  protected readonly actual = computed(() => this.pasos()[Math.min(this.indice(), this.pasos().length - 1)]);
  private readonly modelo = computed(() => this.actual()?.modelo);
  protected readonly volver = computed(() => `/plato/${this.id()}?paso=${this.actual()?.numero ?? 1}`);

  protected readonly estado = signal<'abriendo' | 'activo' | 'error' | 'movil'>(esAndroid() ? 'abriendo' : 'movil');
  protected readonly motivo = signal<'camara' | 'sensores'>('camara');
  private readonly normal = signal(false);
  private readonly colocado = signal(false);
  private readonly cargando = signal(false);
  private readonly modeloFallo = signal(false);
  private readonly escena = signal<EscenaAr | undefined>(undefined);
  protected readonly indicacion = computed(() => {
    const t = this.t();
    if (this.modeloFallo()) return t.errorModelo;
    if (this.estado() === 'abriendo') return t.camaraAbriendo;
    if (this.cargando()) return t.cargandoModelo;
    return this.colocado() && this.normal() ? t.camaraMover : t.camaraApunta;
  });

  private xr8?: Xr8;
  private destruido = false;
  private turno = 0;

  constructor() {
    const colorPrevio = this.meta.getTag('name="theme-color"')?.content;
    this.meta.updateTag({ name: 'theme-color', content: '#000000' });

    inject(DestroyRef).onDestroy(() => {
      this.destruido = true;
      this.xr8?.stop();
      this.xr8?.clearCameraPipelineModules();
      if (colorPrevio) this.meta.updateTag({ name: 'theme-color', content: colorPrevio });
    });

    afterNextRender(() => {
      if (this.estado() === 'abriendo') this.iniciar();
    });

    effect(() => {
      const escena = this.escena();
      const url = this.modelo();
      if (escena && url) this.mostrar(escena, url);
    });

    effect(() => {
      const nombre = this.plato.hasValue() ? this.plato.value().nombre : undefined;
      if (nombre) document.title = `${nombre} · ${this.t().marca}`;
    });
  }

  protected irA(indice: number) {
    this.indice.set(Math.max(0, Math.min(indice, this.pasos().length - 1)));
  }

  protected tocar(evento: MouseEvent) {
    const escena = this.escena();
    if (!escena) return;
    const borde = this.lienzo().nativeElement.getBoundingClientRect();
    const x = ((evento.clientX - borde.left) / borde.width) * 2 - 1;
    const y = 1 - ((evento.clientY - borde.top) / borde.height) * 2;
    if (escena.colocar(x, y)) this.colocado.set(true);
  }

  private async iniciar() {
    try {
      const xr8 = await cargarMotor();
      if (this.destruido) return;
      Object.assign(window, { THREE });
      xr8.addCameraPipelineModules([
        xr8.GlTextureRenderer.pipelineModule(),
        xr8.Threejs.pipelineModule(),
        xr8.XrController.pipelineModule(),
        lienzoCompleto(),
        this.modulo(xr8),
      ]);
      this.xr8 = xr8;
      xr8.run({ canvas: this.lienzo().nativeElement });
    } catch (error) {
      this.fallar(error);
    }
  }

  private fallar(error: unknown) {
    console.error(error);
    const permiso = (error as { permission?: string } | null)?.permission ?? '';
    this.motivo.set(permiso.startsWith('device') ? 'sensores' : 'camara');
    this.estado.set('error');
  }

  private modulo(xr8: Xr8): ModuloCamara {
    const suave = !matchMedia('(prefers-reduced-motion: reduce)').matches;
    let anterior = 0;
    return {
      name: 'cocinaperuana',
      onStart: () => {
        const { scene, camera, renderer } = xr8.Threejs.xrScene();
        camera.position.set(0, ALTURA, 0);
        xr8.XrController.updateCameraProjectionMatrix({ origin: camera.position, facing: camera.quaternion });
        this.escena.set(new EscenaAr(scene, camera, renderer, suave));
        this.estado.set('activo');
      },
      onUpdate: () => {
        const escena = this.escena();
        if (!escena) return;
        const ahora = performance.now();
        escena.actualizar(anterior ? Math.min((ahora - anterior) / 1000, 0.1) : 0);
        anterior = ahora;
        if (!this.colocado() && escena.colocarAlFrente()) this.colocado.set(true);
      },
      onCameraStatusChange: (datos) => {
        if (datos.status === 'failed') this.fallar(datos);
      },
      onException: (error) => this.fallar(error),
      listeners: [{ event: 'reality.trackingstatus', process: ({ detail }) => this.normal.set(detail.status === 'NORMAL') }],
    };
  }

  private async mostrar(escena: EscenaAr, url: string) {
    const turno = ++this.turno;
    this.cargando.set(true);
    this.modeloFallo.set(false);
    try {
      const modelo = await escena.cargar(url);
      if (turno !== this.turno) return;
      escena.poner(modelo);
      // precarga el modelo del paso siguiente
      const siguiente = this.pasos()[this.indice() + 1]?.modelo;
      if (siguiente) escena.cargar(siguiente).catch(() => {});
    } catch {
      if (turno === this.turno) this.modeloFallo.set(true);
    } finally {
      if (turno === this.turno) this.cargando.set(false);
    }
  }
}
