import { ChangeDetectionStrategy, Component, ElementRef, inject, input, signal, viewChild } from '@angular/core';
import { HlmButtonImports } from '@spartan-ng/helm/button';
import { HlmInputImports } from '@spartan-ng/helm/input';
import { Api } from '../../datos/api';
import { IdiomaService } from '../../datos/idioma';
import { Mensaje } from '../../datos/modelos';

@Component({
  selector: 'app-asistente-chat',
  imports: [HlmButtonImports, HlmInputImports],
  templateUrl: './asistente-chat.html',
  styleUrl: './asistente-chat.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class AsistenteChat {
  readonly platoId = input.required<string>();
  readonly paso = input.required<number>();

  private readonly api = inject(Api);
  private readonly idioma = inject(IdiomaService);
  protected readonly t = this.idioma.t;
  protected readonly mensajes = signal<Mensaje[]>([]);
  protected readonly esperando = signal(false);
  protected readonly error = signal(false);
  private readonly lista = viewChild<ElementRef<HTMLElement>>('lista');

  protected enviar(campo: HTMLInputElement, texto = campo.value) {
    const pregunta = texto.trim();
    if (!pregunta || this.esperando()) return;
    const historial = this.mensajes();
    this.mensajes.set([...historial, { rol: 'usuario', texto: pregunta }]);
    campo.value = '';
    this.error.set(false);
    this.esperando.set(true);
    this.bajar();

    this.api.preguntar(this.platoId(), pregunta, this.idioma.actual(), this.paso(), historial).subscribe({
      next: (r) => {
        this.mensajes.update((m) => [...m, { rol: 'asistente', texto: r.respuesta, fueraDeFicha: r.fuera_de_ficha }]);
        this.esperando.set(false);
        this.bajar();
      },
      error: () => {
        this.error.set(true);
        this.esperando.set(false);
      },
    });
  }

  private bajar() {
    requestAnimationFrame(() => {
      const lista = this.lista()?.nativeElement;
      lista?.scrollTo({ top: lista.scrollHeight, behavior: 'smooth' });
    });
  }
}
