import assert from 'node:assert/strict';
import { randomUUID } from 'node:crypto';
import { writeFileSync } from 'node:fs';

const base = process.env.TEST_BASE_URL || 'http://127.0.0.1:5173';
const url = new URL(base);
if (!['127.0.0.1','localhost'].includes(url.hostname)) throw new Error('Las pruebas solo admiten un servidor local.');
const checks = [];
const fixtures = [];
const password = 'Solo pruebas locales ' + randomUUID();
let cookieA = '', cookieB = '';
async function call(path, { method='GET', body, cookie='', origin=base } = {}) {
 const r = await fetch(base+path,{method,headers:{'Content-Type':'application/json', ...(cookie?{Cookie:cookie}:{}),...(method==='GET'?{}:{Origin:origin})},...(body===undefined?{}:{body:JSON.stringify(body)})});
 const text = await r.text(); let json;try{json=JSON.parse(text);}catch{json={};}
 return {status:r.status,json,cookie:r.headers.getSetCookie().map(c=>c.split(';')[0]).join('; '),setCookie:r.headers.get('set-cookie')||''};
}
function check(name, callback){callback();checks.push(name);}
async function account() {
 const email='api-smoke-'+randomUUID()+'@example.test';
 const r=await call('/api/auth/register',{method:'POST',body:{name:'Prueba local',email,password}});
 assert.equal(r.status,201,JSON.stringify(r.json));fixtures.push({email,cookie:r.cookie});return {email,...r};
}
try {
 let r=await call('/api/health');check('sqlite_bootstrap',()=>{assert.equal(r.status,200);assert.equal(r.json.database,'sqlite');});
 r=await call('/api/me');check('anonymous_session_rejected',()=>assert.equal(r.status,401));
 r=await call('/api/me',{cookie:'inmoscore_session=forged'});check('forged_session_rejected',()=>assert.equal(r.status,401));
 r=await call('/api/auth/register',{method:'POST',origin:'https://example.test',body:{}});check('cross_origin_registration_rejected',()=>assert.equal(r.status,403));
 r=await call('/api/auth/register',{method:'POST',body:{name:'Prueba',email:'bad',password:'short'}});check('invalid_credentials_rejected',()=>assert.equal(r.status,400));
 const a=await account();cookieA=a.cookie;
 check('registration_creates_own_account',()=>{assert.ok(cookieA);assert.ok(a.json.user.id);assert.ok(!('passwordHash' in a.json.user));assert.equal(a.json.profile,null);});
 check('session_cookie_protections',()=>{assert.match(a.setCookie,/HttpOnly/i);assert.match(a.setCookie,/SameSite=Lax/i);assert.match(a.setCookie,/Path=\//i);});
 r=await call('/api/me',{cookie:cookieA});check('registered_session_works',()=>assert.equal(r.json.user.id,a.json.user.id));
 r=await call('/api/auth/register',{method:'POST',body:{name:'Prueba',email:a.email.toUpperCase(),password}});check('case_insensitive_email_unique',()=>assert.equal(r.status,409));
 r=await call('/api/auth/login',{method:'POST',body:{email:a.email,password:'Contraseña equivocada'}});check('wrong_password_rejected',()=>assert.equal(r.status,401));
 const wrongMessage=r.json.message;
 r=await call('/api/auth/login',{method:'POST',body:{email:'missing-'+randomUUID()+'@example.test',password}});check('unknown_account_generic_error',()=>{assert.equal(r.status,401);assert.equal(r.json.message,wrongMessage);});
 const profile={name:'María de prueba',income:15000,savings:150000,budget:700000,minRooms:3,minArea:60,districts:[],weights:{price:.2,safety:.45,convenience:.35}};
 r=await call('/api/profile',{method:'PUT',cookie:cookieA,origin:'https://example.test',body:profile});check('cross_origin_profile_rejected',()=>assert.equal(r.status,403));
 r=await call('/api/profile',{method:'PUT',cookie:cookieA,body:{...profile,weights:{price:0,safety:0,convenience:0}}});check('zero_weight_profile_rejected',()=>assert.equal(r.status,400));
 r=await call('/api/profile',{method:'PUT',cookie:cookieA,body:profile});check('profile_saved',()=>{assert.equal(r.status,200);assert.equal(r.json.profile.name,profile.name);});
 r=await call('/api/me',{cookie:cookieA});check('profile_persisted',()=>assert.equal(r.json.profile.budget,profile.budget));
 r=await call('/api/ranking',{method:'POST',body:{profile,limit:12}});
 check('ranking_preserves_filters',()=>{assert.equal(r.status,200);assert.ok(r.json.listings.length>0);for(const row of r.json.listings){assert.ok(row.price<=r.json.cap);assert.ok(row.rooms>=3);assert.ok(row.area>=60);assert.ok(Number.isFinite(row.score));assert.ok(!row.flags.includes('retired_at_last_check'));}});
 const listing=r.json.listings[0];
 r=await call('/api/listings/'+listing.id);check('listing_detail_matches_ranking',()=>assert.equal(r.json.listing.price,listing.price));
 r=await call('/api/listings/nonexistent');check('unknown_listing_rejected',()=>assert.equal(r.status,404));
 r=await call('/api/favorites',{method:'POST',cookie:cookieA,body:{id:listing.id}});check('favorite_saved',()=>assert.ok(r.json.favorites.includes(listing.id)));
 r=await call('/api/favorites',{method:'POST',cookie:cookieA,body:{id:'invalid'}});check('invalid_favorite_rejected',()=>assert.equal(r.status,400));
 const b=await account();cookieB=b.cookie;
 r=await call('/api/me',{cookie:cookieB});check('second_account_data_isolated',()=>{assert.equal(r.json.profile,null);assert.deepEqual(r.json.favorites,[]);assert.notEqual(r.json.user.id,a.json.user.id);});
 r=await call('/api/favorites',{method:'POST',cookie:cookieB,body:{id:listing.id,userId:a.json.user.id}});check('user_id_payload_cannot_impersonate',()=>assert.ok(r.json.favorites.includes(listing.id)));
 r=await call('/api/auth/logout',{method:'POST',cookie:cookieA});check('logout_expires_cookie',()=>{assert.equal(r.status,200);assert.match(r.setCookie,/Max-Age=0/i);});
 r=await call('/api/me',{cookie:cookieA});check('logout_revokes_old_token',()=>assert.equal(r.status,401));
 r=await call('/api/auth/login',{method:'POST',body:{email:a.email,password}});cookieA=r.cookie;fixtures[0].cookie=cookieA;
 check('login_recovers_saved_data',()=>{assert.equal(r.status,200);assert.equal(r.json.profile.budget,700000);assert.ok(r.json.favorites.includes(listing.id));});
 const old=cookieA;
 r=await call('/api/auth/login',{method:'POST',cookie:cookieA,body:{email:a.email,password}});cookieA=r.cookie;fixtures[0].cookie=cookieA;
 check('login_rotates_session_token',()=>assert.notEqual(cookieA,old));
 r=await call('/api/me',{cookie:old});check('rotated_token_is_invalid',()=>assert.equal(r.status,401));
 r=await call('/api/ranking',{method:'POST',body:{profile,onlyLocated:true,limit:100}});check('located_filter',()=>{assert.ok(r.json.listings.length);assert.ok(r.json.listings.every(x=>x.location));});
 r=await call('/api/account',{method:'DELETE',cookie:cookieA,body:{password:'Contraseña equivocada'}});check('delete_requires_current_password',()=>assert.equal(r.status,403));
 r=await call('/api/account',{method:'DELETE',cookie:cookieA,body:{password}});check('own_account_deleted',()=>assert.equal(r.status,200));fixtures[0].cookie='';
 r=await call('/api/me',{cookie:cookieA});check('account_deletion_revokes_session',()=>assert.equal(r.status,401));
 r=await call('/api/auth/login',{method:'POST',body:{email:a.email,password}});check('deleted_credentials_rejected',()=>assert.equal(r.status,401));
 r=await call('/api/me',{cookie:cookieB});check('other_account_survives_deletion',()=>{assert.equal(r.status,200);assert.equal(r.json.user.id,b.json.user.id);assert.ok(r.json.favorites.includes(listing.id));});

} finally {
 for(const fixture of fixtures) if(fixture.cookie){const result=await call('/api/account',{method:'DELETE',cookie:fixture.cookie,body:{password}});if(result.status!==200)throw Error('No se pudo limpiar la cuenta sintética de prueba.');}
}

 writeFileSync('tests/results/api-smoke.json',JSON.stringify({status:'passed',environment:'loopback / SQLite / disposable local test accounts',checks:checks.length,results:checks},null,2)+'\n');
 console.log(checks.length+' comprobaciones de API aprobadas.');
