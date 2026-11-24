// valida cada GLB con gltf-validator y resume errores y avisos
import { readFileSync, readdirSync } from 'node:fs';
import { join } from 'node:path';
import { createRequire } from 'node:module';

const require = createRequire(process.env.VALIDATOR_DIR + '/');
const validator = require('gltf-validator');
const raiz = new URL('../frontend/public/modelos/', import.meta.url).pathname;
const filas = [];
for (const plato of readdirSync(raiz).sort()) {
  for (const archivo of readdirSync(join(raiz, plato)).filter((a) => a.endsWith('.glb')).sort()) {
    const r = await validator.validateBytes(new Uint8Array(readFileSync(join(raiz, plato, archivo))));
    filas.push({ archivo: `${plato}/${archivo}`, errores: r.issues.numErrors, avisos: r.issues.numWarnings, info: r.issues.numInfos });
  }
}
console.log(JSON.stringify(filas));
