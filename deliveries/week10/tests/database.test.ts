import test from 'node:test';
import assert from 'node:assert/strict';
import { mkdirSync, mkdtempSync, rmSync } from 'node:fs';
import { join } from 'node:path';
import { SqliteRepository } from '../db/sqlite.ts';

mkdirSync('storage',{recursive:true});
function fixture() {
 const directory=mkdtempSync(join(process.cwd(),'storage','test-db-'));
 const filename=join(directory,'test.sqlite');
 const repository = new SqliteRepository(filename);
 return { repository,filename,cleanup:()=>rmSync(directory,{recursive:true,force:true}) };
}
const user = (id:string,email=id+'@example.test')=>({id,email,name:id,passwordHash:'private-test-hash'});
test('startup creates SQLite and migrations are idempotent; data survives reopening',async()=>{
 const f=fixture();let db=f.repository;
 try { await db.createUser(user('a'));await db.saveProfile('a','María','{"budget":700000}');await db.toggleFavorite('a','123');db.close();db=new SqliteRepository(f.filename);
 assert.equal((await db.findUserByEmail('a@example.test'))?.name,'María');assert.deepEqual(await db.listFavorites('a'),['123']);await db.health(); }
 finally {db.close();f.cleanup();}
});
test('users have isolated profiles, favorites and sessions; account deletion cascades',async()=>{
 const f=fixture(),db=f.repository;
 try {await db.createUser(user('a'));await db.createUser(user('b'));await db.saveProfile('a','Solo A','{"income":15000}');await db.toggleFavorite('a','123');
 await db.createSession('hashed-a','a',Date.now()+10000);await db.createSession('hashed-b','b',Date.now()+10000);
 assert.deepEqual(await db.listFavorites('b'),[]);assert.equal((await db.findUserByEmail('b@example.test'))?.profileJson,null);
 await db.deleteAccount('a');assert.equal(await db.findSessionUser('hashed-a',Date.now()),null);assert.deepEqual(await db.listFavorites('a'),[]);
 assert.equal((await db.findSessionUser('hashed-b',Date.now()))?.id,'b');assert.ok(await db.findUserByEmail('b@example.test'));}
 finally {db.close();f.cleanup();}
});
test('session expiry and logout reject reused session tokens',async()=>{
 const f=fixture(),db=f.repository;
 try {await db.createUser(user('a'));await db.createSession('expired','a',Date.now()-1000);assert.equal(await db.findSessionUser('expired',Date.now()),null);
 await db.createSession('active','a',Date.now()+10000);assert.ok(await db.findSessionUser('active',Date.now()));await db.deleteSession('active');assert.equal(await db.findSessionUser('active',Date.now()),null);}
 finally {db.close();f.cleanup();}
});
test('unique email is case insensitive and SQL inputs are parameterized',async()=>{
 const f=fixture(),db=f.repository;
 try {await db.createUser(user('a'));assert.equal(await db.createUser(user('b','A@EXAMPLE.TEST')),null);assert.equal(await db.findUserByEmail("' OR 1=1 --"),null);assert.ok(await db.findUserByEmail('a@example.test'));}
 finally {db.close();f.cleanup();}
});
test('authentication attempt limits persist and reset after successful login',async()=>{
 const f=fixture(),db=f.repository;
 try {assert.equal(await db.takeAuthAttempt('key',2,50000),true);assert.equal(await db.takeAuthAttempt('key',2,50000),true);assert.equal(await db.takeAuthAttempt('key',2,50000),false);await db.clearAuthAttempts('key');assert.equal(await db.takeAuthAttempt('key',2,50000),true);}
 finally {db.close();f.cleanup();}
});
