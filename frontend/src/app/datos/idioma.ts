import { DOCUMENT, Injectable, computed, effect, inject, signal } from '@angular/core';
import { Idioma } from './modelos';

const TEXTOS = {
  es: {
    marca: 'Cocina peruana AR',
    titular: 'Platos peruanos, paso a paso, sobre tu mesa',
    bajada: 'Mira cómo se arma cada plato en 3D, ponlo sobre la mesa con tu celular y pregúntale al guía lo que quieras saber.',
    verPlato: 'Ver paso a paso',
    volver: 'Todos los platos',
    paso: 'Paso',
    de: 'de',
    anterior: 'Anterior',
    siguiente: 'Siguiente',
    verEnMesa: 'Ver en tu mesa',
    verConCamara: 'Ver con la cámara',
    arAyuda: 'Abre esta página en un celular Android para ver el plato en realidad aumentada.',
    arFallo: 'Tu celular no pudo abrir Ver en tu mesa. Prueba con Ver con la cámara.',
    camaraAbriendo: 'Abriendo la cámara',
    camaraApunta: 'Apunta a la mesa y mueve el celular despacio',
    camaraMover: 'Toca la mesa para mover el plato',
    camaraError: 'No se pudo abrir la cámara. Revisa que el navegador tenga permiso para usarla.',
    camaraSensores: 'Permite los sensores de movimiento en la configuración del sitio del navegador y vuelve a abrir esta página.',
    camaraSoloMovil: 'Abre esta página en un celular Android para ver el plato con la cámara.',
    cerrar: 'Cerrar',
    volverPlato: 'Volver al plato',
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
    sugerencias: ['¿De dónde viene el nombre?', '¿Es picante?', '¿Qué ingredientes típicos lleva?'],
    min: 'min',
  },
  en: {
    marca: 'Peruvian Cooking AR',
    titular: 'Peruvian dishes, step by step, on your table',
    bajada: 'See how each dish comes together in 3D, place it on your table with your phone and ask the guide anything.',
    verPlato: 'See step by step',
    volver: 'All dishes',
    paso: 'Step',
    de: 'of',
    anterior: 'Previous',
    siguiente: 'Next',
    verEnMesa: 'View on your table',
    verConCamara: 'View with camera',
    arAyuda: 'Open this page on an Android phone to see the dish in augmented reality.',
    arFallo: 'Your phone could not open View on your table. Try View with camera.',
    camaraAbriendo: 'Opening the camera',
    camaraApunta: 'Point at the table and move your phone slowly',
    camaraMover: 'Tap the table to move the dish',
    camaraError: 'The camera could not be opened. Check that the browser is allowed to use it.',
    camaraSensores: "Allow motion sensors in the browser's site settings and open this page again.",
    camaraSoloMovil: 'Open this page on an Android phone to see the dish with the camera.',
    cerrar: 'Close',
    volverPlato: 'Back to the dish',
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
    sugerencias: ['Where does the name come from?', 'Is it spicy?', 'Which typical ingredients does it use?'],
    min: 'min',
  },
  pt: {
    marca: 'Cozinha peruana AR',
    titular: 'Pratos peruanos, passo a passo, na sua mesa',
    bajada: 'Veja como cada prato é montado em 3D, coloque-o na mesa com o celular e pergunte ao guia o que quiser.',
    verPlato: 'Ver passo a passo',
    volver: 'Todos os pratos',
    paso: 'Passo',
    de: 'de',
    anterior: 'Anterior',
    siguiente: 'Próximo',
    verEnMesa: 'Ver na sua mesa',
    verConCamara: 'Ver com a câmera',
    arAyuda: 'Abra esta página em um celular Android para ver o prato em realidade aumentada.',
    arFallo: 'Seu celular não conseguiu abrir Ver na sua mesa. Experimente Ver com a câmera.',
    camaraAbriendo: 'Abrindo a câmera',
    camaraApunta: 'Aponte para a mesa e mova o celular devagar',
    camaraMover: 'Toque na mesa para mover o prato',
    camaraError: 'Não foi possível abrir a câmera. Verifique se o navegador tem permissão para usá-la.',
    camaraSensores: 'Permita os sensores de movimento nas configurações do site do navegador e abra esta página de novo.',
    camaraSoloMovil: 'Abra esta página em um celular Android para ver o prato com a câmera.',
    cerrar: 'Fechar',
    volverPlato: 'Voltar ao prato',
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
    sugerencias: ['De onde vem o nome?', 'É picante?', 'Que ingredientes típicos leva?'],
    min: 'min',
  },
  fr: {
    marca: 'Cuisine péruvienne AR',
    titular: 'Des plats péruviens, étape par étape, sur votre table',
    bajada: 'Voyez comment chaque plat se monte en 3D, posez-le sur la table avec votre téléphone et posez vos questions au guide.',
    verPlato: 'Voir étape par étape',
    volver: 'Tous les plats',
    paso: 'Étape',
    de: 'sur',
    anterior: 'Précédente',
    siguiente: 'Suivante',
    verEnMesa: 'Voir sur votre table',
    verConCamara: 'Voir avec la caméra',
    arAyuda: 'Ouvrez cette page sur un téléphone Android pour voir le plat en réalité augmentée.',
    arFallo: "Votre téléphone n'a pas pu ouvrir Voir sur votre table. Essayez Voir avec la caméra.",
    camaraAbriendo: 'Ouverture de la caméra',
    camaraApunta: 'Visez la table et bougez le téléphone lentement',
    camaraMover: 'Touchez la table pour déplacer le plat',
    camaraError: "Impossible d'ouvrir la caméra. Vérifiez que le navigateur a l'autorisation de l'utiliser.",
    camaraSensores: 'Autorisez les capteurs de mouvement dans les paramètres du site du navigateur, puis rouvrez cette page.',
    camaraSoloMovil: 'Ouvrez cette page sur un téléphone Android pour voir le plat avec la caméra.',
    cerrar: 'Fermer',
    volverPlato: 'Retour au plat',
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
    sugerencias: ["D'où vient le nom ?", 'Est-ce épicé ?', 'Quels ingrédients typiques contient-il ?'],
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
