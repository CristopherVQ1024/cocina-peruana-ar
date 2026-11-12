import { ChangeDetectionStrategy, Component, inject } from '@angular/core';
import { RouterLink, RouterOutlet } from '@angular/router';
import { IDIOMAS, IdiomaService } from './datos/idioma';
import { Idioma } from './datos/modelos';

@Component({
  selector: 'app-root',
  imports: [RouterOutlet, RouterLink],
  templateUrl: './app.html',
  styleUrl: './app.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class App {
  protected readonly idioma = inject(IdiomaService);
  protected readonly idiomas = IDIOMAS;

  protected cambiarIdioma(evento: Event) {
    this.idioma.actual.set((evento.target as HTMLSelectElement).value as Idioma);
  }
}
