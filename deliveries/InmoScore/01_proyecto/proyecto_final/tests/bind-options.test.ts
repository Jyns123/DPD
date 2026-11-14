import test from 'node:test';
import assert from 'node:assert/strict';
import { bindOptions } from '../scripts/bind-options.mjs';

test('el servidor conserva loopback por defecto y no cambia los argumentos de entrada', () => {
  const input = ['--port', '5193', '--webpack'];
  const result = bindOptions(input);
  assert.equal(result.localOnly, true);
  assert.equal(result.hostname, '127.0.0.1');
  assert.deepEqual(input, ['--port', '5193', '--webpack']);
  assert.deepEqual(result.args, [...input, '--hostname', '127.0.0.1']);
});

test('las formas admitidas se normalizan a un único hostname para Next', () => {
  for (const args of [['-H', 'LOCALHOST'], ['--hostname=::1'], ['--hostname', '127.0.0.1']]) {
    const result = bindOptions(args);
    assert.equal(result.localOnly, true);
    assert.deepEqual(result.args, ['--hostname', result.hostname]);
  }
  for (const hostname of ['0.0.0.0', '::', '192.168.1.10', 'equipo.example.test']) {
    const result = bindOptions(['--hostname', hostname]);
    assert.equal(result.localOnly, false);
    assert.equal(result.args.at(-1), hostname);
  }
});

test('no puede haber un hostname local para el guard y otro público para el CLI', () => {
  for (const args of [
    ['--hostname', '127.0.0.1', '--hostname', '0.0.0.0'],
    ['--hostname=127.0.0.1', '--hostname=0.0.0.0'],
    ['-H', '127.0.0.1', '--hostname=0.0.0.0'],
    ['--hostname', 'localhost', '-H', 'localhost'],
  ]) assert.throws(() => bindOptions(args), /una sola vez/);
});

test('los argumentos adjuntos y los valores malformados se rechazan antes de iniciar', () => {
  for (const args of [
    ['-H0.0.0.0'], ['-H=localhost'], ['--hostname'], ['--hostname='],
    ['--hostname', '--port', '5193'], ['--hostname', 'http://localhost'],
    ['--hostname', '127.0.0.1:5193'], ['--hostname', ' localhost '],
    ['--', '--hostname', '0.0.0.0'], ['--hostname-extra', 'localhost'],
  ]) assert.throws(() => bindOptions(args));
});
