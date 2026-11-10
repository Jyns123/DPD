import fs from 'node:fs/promises';
import path from 'node:path';
import { pathToFileURL, fileURLToPath } from 'node:url';
import { Presentation, PresentationFile } from '@oai/artifact-tool';

const DIR = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '../..');
const BUILD = path.join(DIR, 'presentation/.build');
const FINAL = path.join(DIR, 'PresentationWeek10.pptx');
const VALIDATED = path.join(BUILD, `validated-${Date.now()}.pptx`);
const SHOTS = path.join(DIR, 'screenshots');
const SKILL = '/Users/denzel/.codex/plugins/cache/openai-primary-runtime/presentations/26.1015.12040/skills/presentations';
const W = 1280, H = 720;
const C = {
  bg: '#F6F7F2', forest: '#173D31', green: '#2A5947', lime: '#DDF98A',
  orange: '#ED825F', ink: '#1C2822', muted: '#66716A', line: '#D9DED5',
  white: '#FFFFFF', pale: '#E9EEE6', dark2: '#244B3D', fog: '#EFF2EB',
};
const FONT = 'Arial';

const pres = Presentation.create({ slideSize: { width: W, height: H } });

function shape(slide, geometry, x, y, w, h, fill='none', lineFill='none', lineWidth=0, name='') {
  return slide.shapes.add({ geometry, name, position: { left:x, top:y, width:w, height:h }, fill,
    line: { style:'solid', fill:lineFill, width:lineWidth } });
}
function text(slide, value, x, y, w, h, opts={}) {
  const box = shape(slide, 'textbox', x, y, w, h, 'none', 'none', 0, opts.name || '');
  box.text = value;
  box.text.style = { typeface: FONT, fontSize: opts.size ?? 20, color: opts.color ?? C.ink,
    bold: opts.bold ?? false, italic: opts.italic ?? false, alignment: opts.align ?? 'left',
    verticalAlignment: opts.valign ?? 'middle', wrap: true, ...opts.style };
  return box;
}
function rect(slide,x,y,w,h,fill,r=0,line='none',lw=0,name='') {
  return shape(slide, r ? 'roundRect':'rect',x,y,w,h,fill,line,lw,name);
}
function line(slide,x1,y1,x2,y2,color=C.line,width=2) {
  return shape(slide,'line',x1,y1,x2-x1,y2-y1,'none',color,width);
}
function label(slide,value,x,y,w,fill=C.lime,color=C.forest) {
  rect(slide,x,y,w,28,fill,14);
  text(slide,value,x+10,y+1,w-20,25,{size:12,bold:true,color,align:'center'});
}
function footer(slide,n,dark=false) {
  text(slide,'InmoScore  /  Week 10',50,681,300,22,{size:12,color:dark?'#B6C8BD':C.muted});
  text(slide,String(n).padStart(2,'0'),1205,681,35,22,{size:12,color:dark?'#B6C8BD':C.muted,align:'right'});
}
function base(kicker,title,n,{dark=false,subtitle=''}={}) {
  const s = pres.slides.add();
  s.background.fill = dark ? C.forest : C.bg;
  text(s,kicker.toUpperCase(),52,34,850,23,{size:12,bold:true,color:dark?C.lime:C.green});
  text(s,title,52,68,1165,63,{size:36,bold:true,color:dark?C.white:C.ink});
  if (subtitle) text(s,subtitle,54,132,1120,36,{size:17,color:dark?'#D0DDD3':C.muted});
  footer(s,n,dark);
  return s;
}
function metric(slide,value,caption,x,y,w,{accent=C.forest}={}) {
  text(slide,value,x,y,w,62,{size:42,bold:true,color:accent});
  text(slide,caption,x,y+62,w,55,{size:16,color:C.muted});
}
function bullet(slide,head,body,x,y,w,{dark=false}={}) {
  rect(slide,x,y+5,9,9,C.orange,5);
  text(slide,head,x+22,y,w-22,28,{size:19,bold:true,color:dark?C.white:C.ink});
  text(slide,body,x+22,y+31,w-24,48,{size:15,color:dark?'#C9D6CD':C.muted,valign:'top'});
}
async function readShot(key) {
  const f = path.join(SHOTS, `${key}.jpg`);
  try { return await fs.readFile(f); } catch { return null; }
}
async function screenshot(slide,key,x,y,w,h,caption) {
  const bytes = await readShot(key);
  if (bytes) {
    const blob = bytes.buffer.slice(bytes.byteOffset,bytes.byteOffset+bytes.byteLength);
    slide.images.add({blob,contentType:'image/jpeg',alt:`Captura real de ${caption}`,fit:'contain',position:{left:x,top:y,width:w,height:h},geometry:'roundRect',borderRadius:'rounded-lg'});
    return true;
  }
  rect(slide,x,y,w,h,C.white,14,C.line,1);
  rect(slide,x,y,w,32,C.pale,14);
  text(slide,caption.toUpperCase(),x+14,y+4,w-28,21,{size:11,bold:true,color:C.green});
  line(slide,x+12,y+34,x+w-12,y+34,C.line,1);
  text(slide,'Captura de interfaz pendiente',x+20,y+h/2-12,w-40,25,{size:16,bold:true,color:C.muted,align:'center'});
  return false;
}

// 1. Portada
{
  const s=pres.slides.add(); s.background.fill=C.forest;
  rect(s,866,0,414,720,C.lime);
  text(s,'INMOSCORE  /  PRODUCTO DE DATOS',60,52,680,25,{size:13,bold:true,color:C.lime});
  text(s,'Buscar vivienda\ncon mejores señales',60,160,760,170,{size:58,bold:true,color:C.white,valign:'top'});
  text(s,'Un recorrido personalizado para comparar precio, entorno y capacidad de pago en Lima.',64,365,690,78,{size:22,color:'#D8E4DA',valign:'top'});
  text(s,'Week 10  ·  19 de octubre de 2026',64,605,600,28,{size:15,bold:true,color:C.lime});
  text(s,'INMO\nSCORE',924,232,300,142,{size:50,bold:true,color:C.forest,align:'center'});
  text(s,'PRODUCTO WEB',925,397,300,25,{size:13,bold:true,color:C.green,align:'center'});
  text(s,'InmoScore  /  Week 10',64,681,300,22,{size:12,color:'#B6C8BD'});
  text(s,'01',1205,681,35,22,{size:12,color:C.forest,align:'right'});
}
// 2. Problema y producto
{
  const s=base('Problema y producto','La decisión reúne señales que hoy están dispersas',2,{subtitle:'InmoScore convierte el aviso en una comparación guiada por el perfil de compra.'});
  bullet(s,'Precio','¿El monto pedido se acerca al valor estimado para una vivienda similar?',58,214,530);
  bullet(s,'Entorno','¿Qué nivel de seguridad y conveniencia ofrece la zona?',58,320,530);
  bullet(s,'Capacidad de pago','¿El precio cabe dentro del límite financiero del comprador?',58,426,530);
  rect(s,672,210,548,330,C.forest,24);
  label(s,'PRODUCTO',710,245,122,C.lime,C.forest);
  text(s,'Un perfil.\nUn ranking explicable.',708,297,438,112,{size:37,bold:true,color:C.white,valign:'top'});
  text(s,'Cada vivienda combina precio, seguridad y conveniencia, con un tope financiero definido por el usuario.',710,435,454,66,{size:17,color:'#DBE5DD',valign:'top'});
  text(s,'La salida es una lista que se puede revisar, guardar y comparar.',60,588,1120,35,{size:19,bold:true,color:C.green});
}
// 3. Cobertura y límites de datos
{
  const s=base('Base de datos','La base describe el mercado publicado en 20 distritos',3,{subtitle:'Datos históricos de avisos para construir referencias de precio y contexto local.'});
  metric(s,'3 896','avisos históricos en el conjunto de trabajo',60,220,250);
  metric(s,'20','distritos de Lima representados',380,220,210,{accent:C.orange});
  metric(s,'91','avisos históricos excluidos del conjunto de análisis',655,220,250);
  metric(s,'133','ubicaciones de calle o edificio para el mapa',960,220,250,{accent:C.orange});
  line(s,60,396,1220,396,C.line,1);
  bullet(s,'Uso','Entrenar y evaluar valoración; enriquecer cada zona con seguridad y conveniencia.',62,430,510);
  bullet(s,'Alcance','El inventario es histórico. La disponibilidad actual de cada aviso no está verificada.',650,430,540);
  text(s,'El mapa muestra las coordenadas disponibles; su precisión es de calle o edificio.',650,548,535,45,{size:15,italic:true,color:C.muted,valign:'top'});
}
// 4. Recorrido de usuario
{
  const s=base('Recorrido del producto','La experiencia acompaña seis decisiones del comprador',4,{subtitle:'El usuario entra por la landing, completa su perfil y evalúa resultados antes de guardar o comparar.'});
  const steps=[['01','Landing'],['02','Acceso'],['03','Perfil'],['04','Ranking'],['05','Detalle'],['06','Guardados']];
  const xs=[70,270,470,670,870,1070];
  line(s,120,311,1120,311,C.line,3);
  steps.forEach(([n,l],i)=>{
    const x=xs[i]; rect(s,x,273,76,76,i===3?C.lime:C.white,38,i===3?C.lime:C.line,1);
    text(s,n,x,292,76,30,{size:20,bold:true,color:C.forest,align:'center'});
    text(s,l,x-36,371,148,27,{size:16,bold:true,color:C.ink,align:'center'});
  });
  rect(s,66,474,1148,104,C.pale,18);
  text(s,'En cualquier punto, el usuario puede volver a sus favoritos y revisar hasta tres opciones a la vez.',96,500,1085,47,{size:20,bold:true,color:C.green,align:'center'});
  text(s,'Cuentas propias con correo y contraseña; las sesiones usan token aleatorio y hash en SQLite.',70,604,1120,28,{size:14,color:C.muted,align:'center'});
}
// 5. Landing y acceso
{
  const s=base('Experiencia · entrada','Una entrada simple lleva al perfil de búsqueda',5,{subtitle:'La landing presenta el producto; una cuenta propia permite conservar el perfil y los favoritos.'});
  await screenshot(s,'01-landing',58,206,550,375,'Landing');
  await screenshot(s,'02-login',669,206,550,375,'Inicio de sesión');
  text(s,'Landing',58,601,550,25,{size:16,bold:true,color:C.green});
  text(s,'Inicio de sesión con correo y contraseña',669,601,550,25,{size:16,bold:true,color:C.green});
}
// 6. Perfil y ranking
{
  const s=base('Experiencia · personalización','Tres criterios ordenan los resultados para cada perfil',6,{subtitle:'Precio, seguridad y conveniencia tienen pesos configurables; el límite financiero filtra opciones.'});
  await screenshot(s,'03-profile',58,200,510,360,'Perfil');
  await screenshot(s,'04-ranking',608,200,612,360,'Ranking');
  const items=[['Precio','Valor estimado y precio publicado'],['Seguridad','Señal de seguridad de la zona'],['Conveniencia','Servicios y accesibilidad del entorno']];
  items.forEach((it,i)=>{
    const x=58+i*388; label(s,it[0],x,580,i===2?148:104,C.lime,C.forest);
    text(s,it[1],x+(i===2?160:118),581,i===2?210:255,42,{size:14,color:C.muted});
  });
}
// 7. Detalle, guardados y mapa
{
  const s=base('Experiencia · evaluación','El detalle explica cada opción y habilita acciones',7,{subtitle:'El comprador revisa la ficha, guarda favoritos y compara hasta tres viviendas.'});
  await screenshot(s,'05-detail',58,200,555,360,'Detalle de vivienda');
  await screenshot(s,'06-saved',672,200,548,360,'Viviendas guardadas');
  bullet(s,'Mapa','133 ubicaciones geocodificadas con precisión de calle o edificio.',70,594,515);
  bullet(s,'Guardados','Recupera tus favoritas al volver a iniciar sesión.',665,594,515);
}
// 8. Mobile
{
  const s=base('Experiencia · móvil','El recorrido también se adapta a pantallas pequeñas',8,{subtitle:'Captura del prototipo web en formato móvil.'});
  const ok=await screenshot(s,'07-mobile',386,174,508,435,'Experiencia móvil');
  if (!ok) {
    text(s,'WEB RESPONSIVA',62,255,265,30,{size:13,bold:true,color:C.green});
    text(s,'Mismos pasos,\nformato compacto',62,306,280,112,{size:31,bold:true,color:C.ink,valign:'top'});
    text(s,'El usuario puede revisar el ranking y abrir el detalle desde su teléfono.',62,442,280,76,{size:16,color:C.muted,valign:'top'});
  }
}
// 9. Arquitectura
{
  const s=base('Arquitectura','SQLite local sostiene la experiencia web',9,{subtitle:'Next.js sirve la API; el contrato async de persistencia deja espacio para un adaptador futuro de RDS.'});
  const cols=[
    {x:60,w:285,k:'01  DATOS',t:'Pipeline batch',b:'Limpieza y preparación\nPython'},
    {x:440,w:355,k:'02  MODELO',t:'Valoración',b:'Gradient Boosting\nCálculo de resultados'},
    {x:850,w:370,k:'03  APLICACIÓN',t:'Experiencia web',b:'React + Next.js API\nSQLite local'},
  ];
  for (const d of cols) {
    rect(s,d.x,253,d.w,222,d.white,20,C.line,1);
    text(s,d.k,d.x+24,277,d.w-48,23,{size:12,bold:true,color:C.green});
    text(s,d.t,d.x+24,321,d.w-48,40,{size:25,bold:true,color:C.ink});
    text(s,d.b,d.x+24,383,d.w-48,60,{size:17,color:C.muted,valign:'top'});
  }
  line(s,351,362,430,362,C.orange,3); line(s,801,362,840,362,C.orange,3);
  rect(s,60,518,1160,74,C.forest,18);
  text(s,'Persistencia',84,541,120,27,{size:15,bold:true,color:C.lime});
  text(s,'db/repository.ts define el contrato async; db/sqlite.ts crea storage/inmoscore.sqlite al iniciar.',212,539,974,34,{size:16,color:C.white});
}
// 10. Evaluación y próximos pasos
{
  const s=base('Evaluación y alcance','El MAE baja 22 % frente a la línea base',10,{subtitle:'Comparación en 779 registros finales después del desarrollo con 3 117 registros.'});
  rect(s,62,220,530,292,C.white,22,C.line,1);
  text(s,'ERROR ABSOLUTO MEDIO',92,251,410,22,{size:12,bold:true,color:C.muted});
  text(s,'S/ 119 801',92,298,400,58,{size:41,bold:true,color:C.forest});
  text(s,'Modelo actual',94,358,400,24,{size:15,color:C.muted});
  text(s,'S/ 153 665',92,408,400,48,{size:31,bold:true,color:C.muted});
  text(s,'Línea base',94,457,400,22,{size:14,color:C.muted});
  rect(s,430,417,116,40,C.lime,20); text(s,'−22 %',430,422,116,29,{size:18,bold:true,color:C.forest,align:'center'});
  rect(s,622,220,594,292,C.pale,22);
  metric(s,'12,2 %','MdAPE en el conjunto final',656,257,240,{accent:C.green});
  text(s,'La métrica expresa el error porcentual absoluto mediano.',656,381,500,49,{size:16,color:C.muted,valign:'top'});
  line(s,62,550,1216,550,C.line,1);
  text(s,'Siguientes validaciones',63,574,262,28,{size:16,bold:true,color:C.green});
  text(s,'Verificar inventario vigente, ampliar geocodificación y realizar estudio con usuarios.',340,572,854,38,{size:17,color:C.ink});
  text(s,'Resultados orientativos. InmoScore no ofrece asesoría financiera ni confirma disponibilidad actual.',63,624,1135,29,{size:13,color:C.muted});
}

async function writeBlob(file, blob) { await fs.writeFile(file,new Uint8Array(await blob.arrayBuffer())); }
await fs.mkdir(BUILD,{recursive:true});
for (let i=0;i<pres.slides.items.length;i++) {
  const png=await pres.export({slide:pres.slides.items[i],format:'png',scale:1});
  await writeBlob(path.join(BUILD,`slide-${String(i+1).padStart(2,'0')}.png`),png);
}
const montage=await pres.export({format:'webp',montage:true});
await writeBlob(path.join(BUILD,'montage.webp'),montage);
const draft=path.join(BUILD,'draft.pptx');
await (await PresentationFile.exportPptx(pres)).save(draft);
const { finalizePresentation }=await import(pathToFileURL(path.join(SKILL,'container_tools/artifact_tool_utils.mjs')).href);
await fs.mkdir(path.dirname(FINAL),{recursive:true});
await fs.mkdir(path.join(DIR,'presentation/.validation'),{recursive:true});
await finalizePresentation({
  explicitTotalSlideCount:10,
  requiredNativeChartOwnerSlides:[],
  requiredNativeTableOwnerSlides:[],
  workspaceDir:DIR,
  candidatePath:draft,
  finalPath:VALIDATED,
  pythonExecutable:'/Users/denzel/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3',
  integrityValidatorPath:path.join(SKILL,'container_tools/inspect_presentation_package_integrity.py'),
  layoutValidatorPath:path.join(SKILL,'container_tools/inspect_presentation_layout_geometry.py'),
  layoutArgs:['--expected-slide-size-emu','12192000,6858000','--validate-heading-fit'],
  fontPolicy:{basis:'design',families:[FONT]},
  verifyArtifactToolImport:true,
  receiptPath:path.join(DIR,`presentation/.validation/week10-${Date.now()}.json`),
});
await fs.copyFile(VALIDATED,FINAL);
console.log(`Created ${FINAL}`);
