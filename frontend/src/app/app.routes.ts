import { Routes } from '@angular/router';

export const routes: Routes = [
  { path: '', loadComponent: () => import('./paginas/inicio/inicio').then((m) => m.Inicio) },
  { path: 'plato/:id', loadComponent: () => import('./paginas/plato/plato').then((m) => m.PlatoPagina) },
  { path: 'ar/:id/:paso', loadComponent: () => import('./paginas/ar-camara/ar-camara').then((m) => m.ArCamara) },
  { path: '**', redirectTo: '' },
];
