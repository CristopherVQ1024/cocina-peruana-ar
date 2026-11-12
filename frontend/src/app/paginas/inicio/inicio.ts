import { ChangeDetectionStrategy, Component, inject } from '@angular/core';
import { toSignal } from '@angular/core/rxjs-interop';
import { RouterLink } from '@angular/router';
import { HlmButtonImports } from '@spartan-ng/helm/button';
import { catchError, of } from 'rxjs';
import { Visor3d } from '../../componentes/visor-3d/visor-3d';
import { Api } from '../../datos/api';
import { IdiomaService } from '../../datos/idioma';
import { PlatoResumen } from '../../datos/modelos';

@Component({
  selector: 'app-inicio',
  imports: [RouterLink, Visor3d, HlmButtonImports],
  templateUrl: './inicio.html',
  styleUrl: './inicio.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class Inicio {
  protected readonly t = inject(IdiomaService).t;
  protected readonly platos = toSignal(
    inject(Api)
      .platos()
      .pipe(catchError(() => of<PlatoResumen[] | null>(null))),
  );
}
