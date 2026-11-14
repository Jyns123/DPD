-- Agiliza la limpieza por vencimiento sin modificar cuentas ni sesiones vigentes.
CREATE INDEX IF NOT EXISTS sessions_expiry_idx ON sessions(expires_at);
CREATE INDEX IF NOT EXISTS auth_attempts_expiry_idx ON auth_attempts(reset_at);
PRAGMA user_version = 2;
