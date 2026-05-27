# Container Engineering Standards

Loaded by Apply when gateway-engineering is active and Dockerfile or Kubernetes manifests are detected.

## Dockerfile requirements

Every Dockerfile must use multi-stage builds for production images:

```dockerfile
# Stage 1: builder
FROM node:22-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production       # install production deps only
COPY . .
RUN npm run build

# Stage 2: runtime
FROM node:22-alpine AS runtime
WORKDIR /app

# Run as non-root user
RUN addgroup -S app && adduser -S app -G app
USER app

COPY --from=builder --chown=app:app /app/dist ./dist
COPY --from=builder --chown=app:app /app/node_modules ./node_modules

EXPOSE 3000
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s CMD wget -qO- http://localhost:3000/health || exit 1
CMD ["node", "dist/index.js"]
```

### Required Dockerfile practices

- **Non-root user**: do not run as root; create and use a dedicated user
- **Multi-stage build**: separate build environment from runtime image (smaller attack surface, smaller image)
- **HEALTHCHECK**: define how the orchestrator checks if the container is healthy
- **Pinned base image**: use a specific tag (not `latest`); prefer distroless or alpine
- **No secrets in layers**: never `COPY .env` or `RUN export SECRET=...` in Dockerfile
- **Layer order**: copy package files before source code (cache invalidation optimization)

## Docker image security

Spec must declare:
- **Base image**: specific tag + hash pinning for reproducibility
- **Vulnerability scanning**: `docker scout` or `trivy` in CI; fail on CRITICAL vulnerabilities
- **Non-root**: confirmed; document if exception required
- **Image signing**: declare if Cosign/Notary is used for supply chain verification

## Kubernetes deployment requirements

### Deployment manifest

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: my-service
spec:
  replicas: 3
  selector:
    matchLabels:
      app: my-service
  template:
    metadata:
      labels:
        app: my-service
    spec:
      containers:
        - name: my-service
          image: my-service:1.2.3        # pinned tag; never :latest in production
          ports:
            - containerPort: 3000
          resources:
            requests:
              cpu: "100m"
              memory: "128Mi"
            limits:
              cpu: "500m"
              memory: "256Mi"
          livenessProbe:
            httpGet:
              path: /health
              port: 3000
            initialDelaySeconds: 10
            periodSeconds: 30
          readinessProbe:
            httpGet:
              path: /ready
              port: 3000
            initialDelaySeconds: 5
            periodSeconds: 10
          env:
            - name: DATABASE_URL
              valueFrom:
                secretKeyRef:
                  name: db-secret
                  key: url
          securityContext:
            runAsNonRoot: true
            runAsUser: 1000
            allowPrivilegeEscalation: false
            readOnlyRootFilesystem: true
```

### Required fields in spec

- **Resource requests and limits**: declared per container; limits prevent one pod from starving others
- **Liveness probe**: restarts the container if it fails (stuck process, deadlock)
- **Readiness probe**: removes pod from load balancer traffic during startup or overload
- **Secrets via Kubernetes Secrets or external secrets operator** — not env vars in manifest
- **Security context**: `runAsNonRoot: true`; `allowPrivilegeEscalation: false`

### Horizontal Pod Autoscaler

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: my-service-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: my-service
  minReplicas: 2
  maxReplicas: 20
  metrics:
    - type: Resource
      resource:
        name: cpu
        target:
          type: Utilization
          averageUtilization: 70
```

Spec must declare: min and max replicas; scale trigger metric and threshold.

## Health check endpoints

Every containerized service must expose:
- `GET /health` — liveness: returns 200 if process is running; 503 if it should be killed
- `GET /ready` — readiness: returns 200 if service can handle traffic; 503 during startup, maintenance, or dependency failure

Liveness and readiness are different:
- Liveness failure → Kubernetes kills and restarts the pod
- Readiness failure → Kubernetes removes pod from service load balancer (not killed)

## Container networking

Spec must declare:
- **Service**: ClusterIP (internal), NodePort (external via node port), or LoadBalancer (cloud LB)
- **Ingress**: ingress controller (nginx, Traefik, etc.) + ingress rules for external traffic
- **Network policy**: declare which pods can talk to which (default-deny + explicit allow is the security target)
