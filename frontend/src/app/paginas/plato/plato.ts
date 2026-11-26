import { ChangeDetectionStrategy, Component, computed, effect, inject, input, linkedSignal } from '@angular/core';
import { rxResource } from '@angular/core/rxjs-interop';
import { RouterLink } from '@angular/router';
import { HlmButtonImports } from '@spartan-ng/helm/button';
import { catchError, throwError } from 'rxjs';
import { AsistenteChat } from '../../componentes/asistente-chat/asistente-chat';
import { Visor3d } from '../../componentes/visor-3d/visor-3d';
import { Api } from '../../datos/api';
import { IdiomaService } from '../../datos/idioma';
import { Plato } from '../../datos/modelos';

@Component({
  selector: 'app-plato',
  imports: [RouterLink, Visor3d, AsistenteChat, HlmButtonImports],
  templateUrl: './plato.html',
  styleUrl: './plato.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class PlatoPagina {
  readonly id = input.required<string>();
  readonly pasoInicial = input<string>(undefined, { alias: 'paso' });

  private readonly api = inject(Api);
  private readonly idioma = inject(IdiomaService);
  protected readonly t = this.idioma.t;

  protected readonly plato = rxResource({
    params: () => ({ id: this.id(), idioma: this.idioma.actual() }),
    stream: ({ params }) =>
      this.api.plato(params.id, params.idioma).pipe(
        // si la traduccion falla se muestra la ficha original
        catchError((error) => (params.idioma === 'es' ? throwError(() => error) : this.api.plato(params.id, 'es'))),
      ),
  });

  // mantiene la ficha anterior mientras llega la traduccion
  protected readonly datos = linkedSignal<Plato | undefined, Plato | undefined>({
    source: () => (this.plato.hasValue() ? this.plato.value() : undefined),
    computation: (actual, previo) => actual ?? (previo?.value?.id === this.id() ? previo.value : undefined),
  });
  protected readonly indice = linkedSignal({
    source: () => ({ id: this.id(), paso: this.pasoInicial() }),
    computation: ({ paso }) => Math.max(0, (Number(paso) || 1) - 1),
  });
  protected readonly pasos = computed(() => this.datos()?.pasos ?? []);
  protected readonly paso = computed(() => this.pasos()[this.indice()]);
  protected readonly siguienteModelo = computed(() => this.pasos()[this.indice() + 1]?.modelo);

  constructor() {
    effect(() => {
      const nombre = this.datos()?.nombre;
      if (nombre) document.title = `${nombre} · ${this.t().marca}`;
    });
  }

  protected irA(indice: number) {
    this.indice.set(Math.max(0, Math.min(indice, this.pasos().length - 1)));
  }
}
