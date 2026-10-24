# Guía de Despliegue en AWS - InmoScore

Esta guía explica cómo desplegar InmoScore en AWS usando ECS (Elastic Container Service) y API Gateway.

## Requisitos previos

- Cuenta de AWS con permisos administrativos
- AWS CLI instalado y configurado
- Docker instalado localmente
- Dominio configurado (opcional, para Route53)

## Arquitectura propuesta

```
Usuario → API Gateway → ECS (Fargate) → RDS PostgreSQL
                      → S3 (archivos estáticos)
                      → CloudFront (CDN opcional)
```

## Paso 1: Preparar la aplicación para contenedorización

### 1.1 Crear Dockerfile

Crea un archivo `Dockerfile` en la raíz del proyecto:

```dockerfile
# Build stage
FROM node:22-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

# Production stage
FROM node:22-alpine AS runner
WORKDIR /app
ENV NODE_ENV=production
COPY --from=builder /app/package*.json ./
RUN npm ci --omit=dev
COPY --from=builder /app/.next ./.next
COPY --from=builder /app/public ./public
COPY --from=builder /app/next.config.ts ./
COPY --from=builder /app/tsconfig.json ./

# Install SQLite dependencies (para compatibilidad temporal)
RUN apk add --no-cache sqlite

EXPOSE 3000
CMD ["npm", "start"]
```

### 1.2 Crear .dockerignore

```
node_modules
.next
.git
.env.local
storage
*.sqlite
*.sqlite-shm
*.sqlite-wal
tests
.github
```

### 1.3 Actualizar package.json scripts

Asegúrate de tener estos scripts en `package.json`:

```json
{
  "scripts": {
    "dev": "node scripts/start-local.mjs dev --webpack --hostname 127.0.0.1 --port 5173",
    "build": "next build",
    "start": "node scripts/start-local.mjs start --hostname 0.0.0.0 --port 3000",
    "typecheck": "tsc --noEmit"
  }
}
```

## Paso 2: Configurar variables de entorno

Crea un archivo `.env.production`:

```env
NODE_ENV=production
DB_DRIVER=postgres
DATABASE_URL=postgresql://usuario:password@endpoint:5432/inmoscore
SQLITE_PATH=/app/storage/inmoscore.sqlite
```

**Nota:** Para producción, deberías migrar de SQLite a PostgreSQL. Vea el Paso 3.

## Paso 3: Migrar a PostgreSQL (recomendado para producción)

### 3.1 Crear RDS PostgreSQL

```bash
# Crear instancia RDS
aws rds create-db-instance \
  --db-instance-identifier inmoscore-db \
  --db-instance-class db.t3.micro \
  --engine postgres \
  --master-username inmoscore \
  --master-user-password TuPasswordSeguro123! \
  --allocated-storage 20 \
  --vpc-security-group-ids sg-xxxxxxxx \
  --db-subnet-group-name default
```

### 3.2 Crear adaptador PostgreSQL

Crea `db/postgres.ts`:

```typescript
import { Pool } from 'pg';
import type { Repository } from './repository';

export class PostgresRepository implements Repository {
  private pool: Pool;

  constructor(connectionString: string) {
    this.pool = new Pool({ connectionString });
  }

  async query<T>(sql: string, params: any[] = []): Promise<T[]> {
    const client = await this.pool.connect();
    try {
      const result = await client.query(sql, params);
      return result.rows as T[];
    } finally {
      client.release();
    }
  }

  async execute(sql: string, params: any[] = []): Promise<void> {
    await this.query(sql, params);
  }

  async close(): Promise<void> {
    await this.pool.end();
  }
}
```

### 3.3 Actualizar `db/repository.ts` para seleccionar el driver

```typescript
import { SqliteRepository } from './sqlite';
import { PostgresRepository } from './postgres';

const DB_DRIVER = process.env.DB_DRIVER || 'sqlite';

export function getRepository(): Repository {
  if (DB_DRIVER === 'postgres') {
    const connectionString = process.env.DATABASE_URL;
    if (!connectionString) throw new Error('DATABASE_URL required for postgres');
    return new PostgresRepository(connectionString);
  }
  return new SqliteRepository();
}
```

## Paso 4: Construir y subir imagen a ECR

### 4.1 Crear repositorio ECR

```bash
aws ecr create-repository \
  --repository-name inmoscore \
  --image-scanning-configuration scanOnPush=true
```

### 4.2 Autenticar en ECR

```bash
aws ecr get-login-password --region us-east-1 | \
  docker login --username AWS --password-stdin \
  <account-id>.dkr.ecr.us-east-1.amazonaws.com
```

### 4.3 Construir imagen Docker

```bash
docker build -t inmoscore .
```

### 4.4 Etiquetar imagen

```bash
docker tag inmoscore:latest \
  <account-id>.dkr.ecr.us-east-1.amazonaws.com/inmoscore:latest
```

### 4.5 Subir imagen

```bash
docker push <account-id>.dkr.ecr.us-east-1.amazonaws.com/inmoscore:latest
```

## Paso 5: Configurar ECS

### 5.1 Crear Cluster ECS

```bash
aws ecs create-cluster \
  --cluster-name inmoscore-cluster \
  --capacity-providers FARGATE
```

### 5.2 Crear Task Definition

Crea `ecs-task-definition.json`:

```json
{
  "family": "inmoscore-task",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "512",
  "memory": "1024",
  "containerDefinitions": [
    {
      "name": "inmoscore",
      "image": "<account-id>.dkr.ecr.us-east-1.amazonaws.com/inmoscore:latest",
      "portMappings": [
        {
          "containerPort": 3000,
          "protocol": "tcp"
        }
      ],
      "environment": [
        {
          "name": "NODE_ENV",
          "value": "production"
        },
        {
          "name": "DB_DRIVER",
          "value": "postgres"
        }
      ],
      "secrets": [
        {
          "name": "DATABASE_URL",
          "valueFrom": "arn:aws:secretsmanager:us-east-1:<account-id>:secret:inmoscore/db-url"
        }
      ],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/inmoscore",
          "awslogs-region": "us-east-1",
          "awslogs-stream-prefix": "ecs"
        }
      }
    }
  ]
}
```

### 5.3 Registrar Task Definition

```bash
aws ecs register-task-definition \
  --cli-input-json file://ecs-task-definition.json
```

### 5.4 Crear Security Group

```bash
aws ec2 create-security-group \
  --group-name inmoscore-sg \
  --description "Security group for InmoScore"

aws ec2 authorize-security-group-ingress \
  --group-id sg-xxxxxxxx \
  --protocol tcp \
  --port 3000 \
  --source-group <api-gateway-sg-id>
```

### 5.5 Crear Service

```bash
aws ecs create-service \
  --cluster inmoscore-cluster \
  --service-name inmoscore-service \
  --task-definition inmoscore-task \
  --desired-count 1 \
  --launch-type FARGATE \
  --network-configuration "awsvpcConfiguration={subnets=[subnet-xxxxxxxx,subnet-yyyyyyyy],securityGroups=[sg-xxxxxxxx],assignPublicIp=ENABLED}"
```

## Paso 6: Configurar API Gateway

### 6.1 Crear REST API

```bash
aws apigateway create-rest-api \
  --name "InmoScore API" \
  --description "API Gateway for InmoScore"
```

### 6.2 Crear recursos

```bash
# Recurso raíz ya existe, crear sub-recursos
API_ID=<api-id>
PARENT_ID=<root-resource-id>

# Crear /api
aws apigateway create-resource \
  --rest-api-id $API_ID \
  --parent-id $PARENT_ID \
  --path-part "api"

# Crear /api/health
HEALTH_ID=$(aws apigateway create-resource \
  --rest-api-id $API_ID \
  --parent-id <api-resource-id> \
  --path-part "health" \
  --query 'id' --output text)
```

### 6.3 Crear métodos

```bash
# GET /api/health
aws apigateway put-method \
  --rest-api-id $API_ID \
  --resource-id $HEALTH_ID \
  --http-method GET \
  --authorization-type NONE

# Integración con ECS
aws apigateway put-integration \
  --rest-api-id $API_ID \
  --resource-id $HEALTH_ID \
  --http-method GET \
  --type HTTP_PROXY \
  --integration-http-method GET \
  --uri "http://<ecs-load-balancer-dns>:3000/api/health"
```

### 6.4 Deploy API

```bash
aws apigateway create-deployment \
  --rest-api-id $API_ID \
  --stage-name prod
```

## Paso 7: Configurar Route53 (opcional)

```bash
# Crear registro A para apuntar a API Gateway
aws route53 change-resource-record-sets \
  --hosted-zone-id <zone-id> \
  --change-batch '{
    "Changes": [{
      "Action": "CREATE",
      "ResourceRecordSet": {
        "Name": "inmoscore.tudominio.com",
        "Type": "A",
        "AliasTarget": {
          "DNSName": "<api-gateway-domain>",
          "EvaluateTargetHealth": false,
          "HostedZoneId": "<cloudfront-zone-id>"
        }
      }
    }]
  }'
```

## Paso 8: Configurar Secrets Manager

```bash
# Guardar DATABASE_URL
aws secretsmanager create-secret \
  --name inmoscore/db-url \
  --secret-string "postgresql://usuario:password@endpoint:5432/inmoscore"
```

## Paso 9: Monitoreo y logs

### 9.1 CloudWatch Logs

```bash
# Crear grupo de logs
aws logs create-log-group \
  --log-group-name /ecs/inmoscore

# Ver logs
aws logs tail /ecs/inmoscore --follow
```

### 9.2 CloudWatch Alarms (opcional)

```bash
aws cloudwatch put-metric-alarm \
  --alarm-name inmoscore-high-cpu \
  --alarm-description "Alerta si CPU > 80%" \
  --metric-name CPUUtilization \
  --namespace AWS/ECS \
  --statistic Average \
  --period 300 \
  --threshold 80 \
  --comparison-operator GreaterThanThreshold
```

## Paso 10: CI/CD con GitHub Actions

Crea `.github/workflows/deploy.yml`:

```yaml
name: Deploy to AWS ECS

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v4
        with:
          aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          aws-region: us-east-1

      - name: Login to Amazon ECR
        id: login-ecr
        uses: aws-actions/amazon-ecr-login@v2

      - name: Build, tag, and push image to Amazon ECR
        env:
          ECR_REGISTRY: ${{ steps.login-ecr.outputs.registry }}
          ECR_REPOSITORY: inmoscore
          IMAGE_TAG: ${{ github.sha }}
        run: |
          docker build -t $ECR_REGISTRY/$ECR_REPOSITORY:$IMAGE_TAG .
          docker push $ECR_REGISTRY/$ECR_REPOSITORY:$IMAGE_TAG

      - name: Deploy to ECS
        run: |
          aws ecs update-service \
            --cluster inmoscore-cluster \
            --service inmoscore-service \
            --force-new-deployment
```

## Costos estimados (us-east-1)

- **ECS Fargate (t3.micro):** ~$8-12/mes
- **RDS PostgreSQL (t3.micro):** ~$15-20/mes
- **API Gateway:** ~$3.50/mes (mínimo)
- **ECS ECR:** ~$0.10/GB/mes
- **CloudWatch Logs:** ~$0.50/GB ingestado
- **Total estimado:** ~$30-40/mes

## Limitaciones y consideraciones

1. **Base de datos:** Esta guía usa PostgreSQL para producción. SQLite no es recomendado para entornos multi-usuario.
2. **Autenticación:** Actualmente usa contraseñas con scrypt local. Para producción, considere agregar:
   - Verificación por correo (AWS SES)
   - Recuperación de contraseña
   - MFA opcional
3. **HTTPS:** Configure un certificado SSL en API Gateway o CloudFront.
4. **Rate limiting:** Configure límites de tasa en API Gateway para prevenir abuso.
5. **Backup:** Configure backups automáticos en RDS (retención de 7-30 días).

## Troubleshooting

### Contenedor no inicia
```bash
# Ver logs de ECS
aws logs tail /ecs/inmoscore --follow

# Ver eventos de servicio
aws ecs describe-services \
  --cluster inmoscore-cluster \
  --services inmoscore-service
```

### Error de conexión a base de datos
- Verifique que el Security Group de RDS permite conexiones desde el Security Group de ECS
- Verifique que DATABASE_URL esté correctamente configurado en Secrets Manager

### API Gateway timeout
- Aumente el timeout en la integración (máximo 29 segundos para integraciones HTTP)
- Para tareas largas, considere usar funciones asíncronas con SQS + Lambda

## Alternativa más simple: Vercel

Si prefieres una solución más simple que ECS + API Gateway:

1. Instala Vercel CLI: `npm i -g vercel`
2. Ejecuta: `vercel`
3. Configura variables de entorno en el dashboard de Vercel
4. Usa un servicio de PostgreSQL externo (Neon, Supabase, o AWS RDS)

Vercel maneja automáticamente el despliegue, HTTPS, CDN y escalado.

## Referencias

- [AWS ECS Documentation](https://docs.aws.amazon.com/ecs/)
- [AWS API Gateway Documentation](https://docs.aws.amazon.com/apigateway/)
- [Next.js Deployment](https://nextjs.org/docs/deployment)
