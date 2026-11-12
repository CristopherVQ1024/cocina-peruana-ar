import '@google/model-viewer';
import {
  CUSTOM_ELEMENTS_SCHEMA,
  ChangeDetectionStrategy,
  Component,
  ElementRef,
  computed,
  inject,
  input,
  signal,
  viewChild,
} from '@angular/core';
import { HlmButtonImports } from '@spartan-ng/helm/button';
import { IdiomaService } from '../../datos/idioma';

interface ModelViewerElement extends HTMLElement {
  canActivateAR: boolean;
}

@Component({
  selector: 'app-visor-3d',
  imports: [HlmButtonImports],
  templateUrl: './visor-3d.html',
  styleUrl: './visor-3d.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
  schemas: [CUSTOM_ELEMENTS_SCHEMA],
})
export class Visor3d {
  readonly src = input.required<string>();
  readonly alt = input.required<string>();
  readonly siguiente = input<string>();
  readonly conAr = input(true);
  readonly vitrina = input(false);

  protected readonly t = inject(IdiomaService).t;
  protected readonly progreso = signal(0);
  protected readonly puedeAr = signal(false);
  protected readonly arFallo = signal(false);
  private readonly cargado = signal<string | null>(null);
  private readonly fallido = signal<string | null>(null);
  protected readonly estado = computed(() =>
    this.fallido() === this.src() ? 'error' : this.cargado() === this.src() ? 'listo' : 'cargando',
  );
  private readonly visor = viewChild.required<ElementRef<ModelViewerElement>>('visor');

  protected alProgresar(evento: Event) {
    this.progreso.set((evento as CustomEvent<{ totalProgress: number }>).detail.totalProgress);
  }

  protected alCargar() {
    this.cargado.set(this.src());
    this.puedeAr.set(this.visor().nativeElement.canActivateAR);
    const siguiente = this.siguiente();
    // precarga el modelo del paso siguiente
    if (siguiente) fetch(siguiente).catch(() => {});
  }

  protected alCambiarAr(evento: Event) {
    if ((evento as CustomEvent<{ status: string }>).detail.status === 'failed') this.arFallo.set(true);
  }

  protected alFallar() {
    this.fallido.set(this.src());
  }
}
