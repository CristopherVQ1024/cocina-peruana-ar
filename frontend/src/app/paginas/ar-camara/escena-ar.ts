import {
  Box3,
  DirectionalLight,
  Group,
  Mesh,
  NeutralToneMapping,
  Object3D,
  PCFShadowMap,
  PerspectiveCamera,
  Plane,
  PlaneGeometry,
  PMREMGenerator,
  Raycaster,
  Scene,
  ShadowMaterial,
  Vector2,
  Vector3,
  WebGLRenderer,
} from 'three';
import { RoomEnvironment } from 'three/addons/environments/RoomEnvironment.js';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';

const MESA = new Plane(new Vector3(0, 1, 0), 0);
const ALCANCE = 3;
// puntos de pantalla donde se busca la mesa al empezar
const MIRAS = [0, -0.4, -0.75];

export class EscenaAr {
  private readonly cargador = new GLTFLoader();
  private readonly modelos = new Map<string, Promise<Object3D>>();
  private readonly plato = new Group();
  private readonly objetivo = new Vector3();
  private readonly rayo = new Raycaster();
  private colocado = false;

  constructor(
    scene: Scene,
    private readonly camara: PerspectiveCamera,
    renderer: WebGLRenderer,
    private readonly suave: boolean,
  ) {
    renderer.toneMapping = NeutralToneMapping;
    renderer.toneMappingExposure = 1.05;
    renderer.shadowMap.enabled = true;
    renderer.shadowMap.type = PCFShadowMap;
    const pmrem = new PMREMGenerator(renderer);
    scene.environment = pmrem.fromScene(new RoomEnvironment(), 0.04).texture;
    pmrem.dispose();
    // suelta el programa borrado para que el motor no lo restaure
    renderer.getContext().useProgram(null);
    renderer.resetState();

    const luz = new DirectionalLight(0xffffff, 0.6);
    luz.position.set(0.3, 1.2, 0.4);
    luz.target = this.plato;
    luz.castShadow = true;
    luz.shadow.mapSize.set(1024, 1024);
    luz.shadow.radius = 4;
    Object.assign(luz.shadow.camera, { left: -0.4, right: 0.4, top: 0.4, bottom: -0.4, near: 0.1, far: 3 });

    const sombra = new Mesh(new PlaneGeometry(0.9, 0.9).rotateX(-Math.PI / 2), new ShadowMaterial({ opacity: 0.3 }));
    sombra.receiveShadow = true;

    this.plato.add(luz, sombra);
    this.plato.visible = false;
    scene.add(this.plato);
  }

  cargar(url: string): Promise<Object3D> {
    let modelo = this.modelos.get(url);
    if (!modelo) {
      modelo = this.cargador.loadAsync(url).then(({ scene }) => {
        scene.traverse((pieza) => {
          if (pieza instanceof Mesh) pieza.castShadow = !(Array.isArray(pieza.material) ? pieza.material[0] : pieza.material).transparent;
        });
        scene.position.y -= new Box3().setFromObject(scene).min.y;
        return scene;
      });
      modelo.catch(() => this.modelos.delete(url));
      this.modelos.set(url, modelo);
    }
    return modelo;
  }

  poner(modelo: Object3D) {
    this.plato.getObjectByName('modelo')?.removeFromParent();
    modelo.name = 'modelo';
    this.plato.add(modelo);
  }

  // x e y en coordenadas normalizadas de pantalla
  colocar(x: number, y: number): boolean {
    this.camara.updateMatrixWorld();
    this.rayo.setFromCamera(new Vector2(x, y), this.camara);
    const punto = this.rayo.ray.intersectPlane(MESA, new Vector3());
    if (!punto || punto.distanceTo(this.camara.position) > ALCANCE) return false;
    this.objetivo.copy(punto);
    if (!this.colocado) {
      this.colocado = true;
      this.plato.position.copy(punto);
      this.plato.rotation.y = Math.atan2(this.camara.position.x - punto.x, this.camara.position.z - punto.z);
      this.plato.scale.setScalar(this.suave ? 0.85 : 1);
      this.plato.visible = true;
    } else if (!this.suave) {
      this.plato.position.copy(punto);
    }
    return true;
  }

  colocarAlFrente(): boolean {
    return MIRAS.some((y) => this.colocar(0, y));
  }

  actualizar(segundos: number) {
    if (!this.colocado || !this.suave) return;
    const avance = 1 - Math.exp(-segundos * 14);
    this.plato.position.lerp(this.objetivo, avance);
    const escala = this.plato.scale.x;
    if (escala < 1) this.plato.scale.setScalar(escala > 0.998 ? 1 : escala + (1 - escala) * avance);
  }
}
