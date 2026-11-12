import { DOCUMENT, Injectable, computed, effect, inject, signal } from '@angular/core';
import { Idioma } from './modelos';

const TEXTOS = {
  es: {
    marca: 'Cocina peruana AR',
    titular: 'Platos peruanos, paso a paso, sobre tu mesa',
    bajada: 'Mira cómo se arma cada plato en 3D, ponlo sobre la mesa con tu celular y pregúntale al guía lo que quieras saber.',
    verPlato: 'Ver paso a paso',
    proximamente: 'Próximamente',
    volver: 'Todos los platos',
    paso: 'Paso',
    de: 'de',
    anterior: 'Anterior',
    siguiente: 'Siguiente',
    verEnMesa: 'Ver en tu mesa',
    arAyuda: 'Abre esta página en un celular Android para ver el plato en realidad aumentada.',
    arFallo: "No se pudo abrir la realidad aumentada. Instala o actualiza Servicios de Google Play para AR desde Play Store y vuelve a intentarlo.",
    cargandoModelo: 'Cargando modelo',
    errorModelo: 'No se pudo cargar el modelo 3D.',
    ingredientes: 'Ingredientes',
    porciones: 'porciones',
    historia: 'Historia',
    preparacion: 'Preparación',
    asistente: 'Pregúntale al guía',
    asistenteBajada: 'Responde con la ficha del plato y en tu idioma.',
    placeholder: 'Escribe tu pregunta',
    enviar: 'Enviar',
    pensando: 'Pensando',
    errorAsistente: 'El guía no está disponible ahora. Intenta de nuevo en un momento.',
    errorPlato: 'No se pudo cargar el plato.',
    reintentar: 'Reintentar',
    sugerencias: ['¿De dónde viene el nombre?', '¿Es picante?', '¿Qué es la papa amarilla?'],
    min: 'min',
  },
  en: {
    marca: 'Peruvian Cooking AR',
    titular: 'Peruvian dishes, step by step, on your table',
    bajada: 'See how each dish comes together in 3D, place it on your table with your phone and ask the guide anything.',
    verPlato: 'See step by step',
    proximamente: 'Coming soon',
    volver: 'All dishes',
    paso: 'Step',
    de: 'of',
    anterior: 'Previous',
    siguiente: 'Next',
    verEnMesa: 'View on your table',
    arAyuda: 'Open this page on an Android phone to see the dish in augmented reality.',
    arFallo: "Augmented reality could not start. Install or update Google Play Services for AR from the Play Store and try again.",
    cargandoModelo: 'Loading model',
    errorModelo: 'The 3D model could not be loaded.',
    ingredientes: 'Ingredients',
    porciones: 'servings',
    historia: 'History',
    preparacion: 'Preparation',
    asistente: 'Ask the guide',
    asistenteBajada: 'Answers from the dish card, in your language.',
    placeholder: 'Type your question',
    enviar: 'Send',
    pensando: 'Thinking',
    errorAsistente: 'The guide is not available right now. Please try again shortly.',
    errorPlato: 'The dish could not be loaded.',
    reintentar: 'Retry',
    sugerencias: ['Where does the name come from?', 'Is it spicy?', 'What is papa amarilla?'],
    min: 'min',
  },
  pt: {
    marca: 'Cozinha peruana AR',
    titular: 'Pratos peruanos, passo a passo, na sua mesa',
    bajada: 'Veja como cada prato é montado em 3D, coloque-o na mesa com o celular e pergunte ao guia o que quiser.',
    verPlato: 'Ver passo a passo',
    proximamente: 'Em breve',
    volver: 'Todos os pratos',
    paso: 'Passo',
    de: 'de',
    anterior: 'Anterior',
    siguiente: 'Próximo',
    verEnMesa: 'Ver na sua mesa',
    arAyuda: 'Abra esta página em um celular Android para ver o prato em realidade aumentada.',
    arFallo: "Não foi possível abrir a realidade aumentada. Instale ou atualize o Google Play Services para RA na Play Store e tente de novo.",
    cargandoModelo: 'Carregando modelo',
    errorModelo: 'Não foi possível carregar o modelo 3D.',
    ingredientes: 'Ingredientes',
    porciones: 'porções',
    historia: 'História',
    preparacion: 'Preparo',
    asistente: 'Pergunte ao guia',
    asistenteBajada: 'Responde com a ficha do prato, no seu idioma.',
    placeholder: 'Escreva sua pergunta',
    enviar: 'Enviar',
    pensando: 'Pensando',
    errorAsistente: 'O guia não está disponível agora. Tente novamente em instantes.',
    errorPlato: 'Não foi possível carregar o prato.',
    reintentar: 'Tentar de novo',
    sugerencias: ['De onde vem o nome?', 'É picante?', 'O que é papa amarilla?'],
    min: 'min',
  },
  fr: {
    marca: 'Cuisine péruvienne AR',
    titular: 'Des plats péruviens, étape par étape, sur votre table',
    bajada: 'Voyez comment chaque plat se monte en 3D, posez-le sur la table avec votre téléphone et posez vos questions au guide.',
    verPlato: 'Voir étape par étape',
    proximamente: 'Bientôt',
    volver: 'Tous les plats',
    paso: 'Étape',
    de: 'sur',
    anterior: 'Précédente',
    siguiente: 'Suivante',
    verEnMesa: 'Voir sur votre table',
    arAyuda: 'Ouvrez cette page sur un téléphone Android pour voir le plat en réalité augmentée.',
    arFallo: "Impossible de lancer la réalité augmentée. Installez ou mettez à jour Services Google Play pour la RA depuis le Play Store, puis réessayez.",
    cargandoModelo: 'Chargement du modèle',
    errorModelo: 'Impossible de charger le modèle 3D.',
    ingredientes: 'Ingrédients',
    porciones: 'portions',
    historia: 'Histoire',
    preparacion: 'Préparation',
    asistente: 'Demandez au guide',
    asistenteBajada: 'Répond à partir de la fiche du plat, dans votre langue.',
    placeholder: 'Écrivez votre question',
    enviar: 'Envoyer',
    pensando: 'Réflexion',
    errorAsistente: "Le guide n'est pas disponible pour le moment. Réessayez dans un instant.",
    errorPlato: "Le plat n'a pas pu être chargé.",
    reintentar: 'Réessayer',
    sugerencias: ["D'où vient le nom ?", 'Est-ce épicé ?', "Qu'est-ce que la papa amarilla ?"],
    min: 'min',
  },
} satisfies Record<Idioma, Record<string, string | string[]>>;

export const IDIOMAS: { codigo: Idioma; nombre: string }[] = [
  { codigo: 'es', nombre: 'Español' },
  { codigo: 'en', nombre: 'English' },
  { codigo: 'pt', nombre: 'Português' },
  { codigo: 'fr', nombre: 'Français' },
];

const CLAVE = 'idioma';

function leerGuardado(): Idioma {
  try {
    const guardado = localStorage.getItem(CLAVE);
    if (IDIOMAS.some((i) => i.codigo === guardado)) return guardado as Idioma;
  } catch {}
  return 'es';
}

@Injectable({ providedIn: 'root' })
export class IdiomaService {
  private readonly documento = inject(DOCUMENT);
  readonly actual = signal<Idioma>(leerGuardado());
  readonly t = computed(() => TEXTOS[this.actual()]);

  constructor() {
    effect(() => {
      const idioma = this.actual();
      this.documento.documentElement.lang = idioma;
      try {
        localStorage.setItem(CLAVE, idioma);
      } catch {}
    });
  }
}
