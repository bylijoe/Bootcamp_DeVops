# Contenedores ,mas que Vms.

### Practica Contenedores-Kubernetes
 - Leonardo Silva Nevado

# Pre-requisito
 - Ubuntu 20.04 / Windows10 / MACS OS
 - Docker
 - minikube
 - kubectl
 - Una cuenta GCP
 - Helm
 
 
 ## Descripción del proyecto
 
  Vamos a implementar una  aplicacion consistente en un micro servicio el cual sera capaz de leer y escribir en una base de datos, en nuestro caso nos hemos basado en la aplicacion flask-counter trabajada durante el curso
  La aplicación escrita en python debe recuperar el número de veces que se visitó el sitio web y almacenarlo en la base de datos de Redis. Al llamar a la URL http://localhost:5000, deberá mostrar el número de veces que hayamos accedido a dicha direccion en local o al  llamar http://flask.34-132-94-3.nip.io/ a traves de internet.

  
  
  # Docker
  
  el codigo de la aplicacion se expone en el archivo **app.py** , el cual se describe a continueción: 
  
              import time
              import os
              import redis
              from flask import Flask, render_template
              import logging ,sys ,json_logging
              from prometheus_flask_exporter import PrometheusMetrics

              REDIS_HOST = os.environ.get('REDIS_HOST', 'redis')
              REDIS_PORT = os.environ.get('REDIS_PORT', 6379 )
              REDIS_PASSWORD = os.environ.get('REDIS_PASSWORD',"")

              app = Flask(__name__)

              metrics = PrometheusMetrics( app )

              json_logging.init_flask(enable_json=True)
              json_logging.init_request_instrument(app)

              logger = logging.getLogger("keep-counter")
              logger.setLevel(logging.DEBUG)
              logger.addHandler(logging.StreamHandler(sys.stdout))

              cache = redis.Redis(host=REDIS_HOST, port=(REDIS_PORT), password=REDIS_PASSWORD)
              metrics.info( 'app_info' , 'Application info', version='1.0.3')



              def get_hit_count():
                 retries = 5
                 while True:
                     try:
                         logger.info('iniciando contador')
                         hitss = cache.incr('hits')
                         return hitss
                     except redis.exceptions.ConnectionError as exc:
                         if retries == 0:
                             logger.error( "Error de conexion" )
                             logger.exception(exc)
                             raise exc
                         retries -=1
                         time.sleep(0.5)

              @app.route('/')
              def hello():
                 count = get_hit_count()
                 message = "Hello Keepcoding!!!! I have been seen {} time HTML. \n".format(count)
                 return  render_template("index.html",message=message)

              @app.route('/health/liveness')    
              def healthx():
                 return "<h1><center>Liveness check completed</center><h1>"  

              @app.route('/health/readiness')
              def healthz():
                 return "<h1><center>Readiness check completed</center><h1>"          
                 
                 
Hemos utilizado la funcion  render_template que importamos desde flask que  se utiliza para generar resultados a partir de un archivo de plantilla(en nuestro caso index.html) basado en el motor Jinja2 que se encuentra en la carpeta Templates contenida en la carpeta src donde se encuentra la aplicació, el cual  es el sguiente:

 index.html
 
            <!DOCTYPE html>
             <html>
             <body>
                <h1>
                     <center>{{ message }}</center>
                </h1>
             </body>
             </html>
             
  
 Hemos creado un fichero de configuracion y/o  variables de entorno requeridas por la aplicacion denominado **.env** , el cual contiene:
 
          REDIS_HOST="redis"
          REDIS_PORT="6379"
          REDIS_PASSWORD=''
 
  
             
Contruida la aplicacion pasaremos a creaar el archivo Dockerfile, el cual nos permitira crear una imagen de nuestra aplicacion leyendo las instrucciones que le indiquemos , hemos creado una imagen multistage, mediente dicho proceso se puede reducir el tamaño de las imagenes de Docker mediante el uso del builder, el cual es un patron de diseño que, en el caso de Docker ,utiliza dos imagenes para crear primero una imagen base para la construccion  de assets  (representacion de cualquier item) y compilacion del codigo fuente, y una segunda imagen que se utiliza para desplegar la aplicacion final. 


 Dockerfile
 
            FROM python:3.7-alpine as base

            FROM base AS dependencias 

            WORKDIR /install

            RUN apk add --no-cache gcc musl-dev linux-headers
            COPY src/requirements.txt .
            RUN pip install --prefix=/install -r requirements.txt


            FROM base

            COPY --from=dependencias /install  /usr/local

            WORKDIR /app
            COPY src .

            ENV FLASK_APP=app.py
            ENV FLASK_RUN_HOST=0.0.0.0

            EXPOSE 5000

            CMD ["flask", "run"]
            
  Una vez definido nuestro Dockerfile pasaremos a construir nuestra imagen que utilizaremos a lo largo del prpoyecto, con los siguientes comando la crearemos y posetriormente la subiremos a nuestro repositorio de docker hub, desde donde posteriormente nuestro objeto Deploymen se descargara nuestra imagen para desplegarla en kubernetes
          
           docker build -t leosn/keep-counter:3.0 .
           
           docker push leosn/keep-coounter:3.0
           
           
Ahora pasaremos a la creacion del docker-compose , el cual es una herramienta de orquestacion local de docker, que nos permite definir y orquestar de forma local varios contenedores que se comunican por red la cual se crea  por defecto permitiendo la comunicacion entre los servicios ,al ser multicontenedor nos permite ejecutar varias imagenes a la vez, como un stack completo de aplicacion.
 
 docker-compose.yaml
 
           version: "3.9"
           services:
             app:
               build: .
               ports:
               - "5000:5000"
               environment:
               - REDIS_HOST=${REDIS_HOST}
               - REDIS_PORT=${REDIS_PORT}
               - REDIS_PASSWORD=${REDIS_PASSWORD}
               links:
               - redis
               restart: unless-stopped
             redis:
               image: redis
               restart: unless-stopped
               
               
 Podemos  crear y arrancar los contenedores mediante la opcion **up** o parar el servicio y destruir los contenedores con **down** 
          
          
          docker-compose up   --------> crea y arranca los contenedores
          docker-compose down --------> para los servicios y destruye los contenedores 

Levantado los servicios podemos acceder a la aplicacion a través de nuestro navegador introduciendo  ( localhost:5000)
  
 * **Logs**- Permiten obtener información sobre las aplicaciones, añadiendo información adicional a los mensajes de error, ya que son privados.
             
      *  beben incluir 4 elementos:
           - Nivel: INFO(information), WARN (Warning), ERROR y DEBUG (Debugging)
           - Timestamp: hora exacta de error.
           - Mensaje: mensaje del error, puede componerse por varios errores encadenados
           - Handler: quién es el generador del error 

 Para el apartado de los **logs** hemos utilizado el modulo de  python **json_logging** ------> que hemos incluido en el archivo requirements.txt
 

De forma predeterminada, el registro se emitirá en formato normal para facilitar el desarrollo local. Para habilitarlo en producción, establezca enable_json en json_logging.init_< framework_name >() llamada al método. Una vez configurada la biblioteca intentará configurar todos los registradores (existentes y recién creados) para emitir el registro en formato JSON. Puede encontrar distintos casos de usos en :
 ------> ( https://github.com/bobbui/json-logging-python )
  
  
  
# K8s  
 Primeramente crearemos un cluster en GCP, a tarvez  del siguiente comando:
      
        gcloud beta container --project "natural-chiller-347811" clusters create "cluster-1" --region "us-central1" --no-enable-basic-auth --cluster-version "1.21.6-gke.1503" --release-channel "regular" --machine-type "e2-medium" --image-type "COS_CONTAINERD" --disk-type "pd-standard" --disk-size "100" --metadata disable-legacy-endpoints=true --scopes "https://www.googleapis.com/auth/devstorage.read_only","https://www.googleapis.com/auth/logging.write","https://www.googleapis.com/auth/monitoring","https://www.googleapis.com/auth/servicecontrol","https://www.googleapis.com/auth/service.management.readonly","https://www.googleapis.com/auth/trace.append" --max-pods-per-node "110" --num-nodes "3" --logging=SYSTEM,WORKLOAD --monitoring=SYSTEM --enable-ip-alias --network "projects/natural-chiller-347811/global/networks/default" --subnetwork "projects/natural-chiller-347811/regions/us-central1/subnetworks/default" --no-enable-intra-node-visibility --default-max-pods-per-node "110" --no-enable-master-authorized-networks --addons HorizontalPodAutoscaling,HttpLoadBalancing,GcePersistentDiskCsiDriver --enable-autoupgrade --enable-autorepair --max-surge-upgrade 1 --max-unavailable-upgrade 0 --enable-shielded-nodes
 
 y nos conectaremos a él.
 
 podemos ver los nodos que contiene el cluster mediante el siguiente comando:
 
     kubectl get nodes
 
 ver los contesxtos:
 
     kubectl config get-contexts
 
cambiarnos de contexto :

     kubectl config use-context
     
Ahora pasaremos a describir los manifiestos necesarios para desplegar la correspondiente aplicación:

* **Deployment**-  Es un tipo de controlador que nos permite de manera declarativa manejar Pods y ResplicaSets. Se establece un estado deseado, y el controlador de Deployment se encarga   de que los Pods que estan a su cargo alcancen dicho estado.
   Deployment---->Pod------>contenedores
   
   
   dep_flask.yaml
   
          apiVersion: apps/v1  #Version de la API
          kind: Deployment     # TIPO: Deployment
          metadata:            # Metadatos del Deployment
            labels:
            name: flask-dpl
          spec:                # Specificacion del DEPLOYMENT
            selector:
              matchLabels:
                app: flask
            replicas: 1         # indica al controlador que ejecute 1 pods
            template:
              metadata:
                labels:
                  app: flask
                annotations:
                  prometheus.io/path: "/metrics"
                  prometheus.io/port: "5000"    -------------------> mediante la siguiente annotacion le indicamos a Prometheus que recoja las metricas
                  prometheus.io/scrape: "true"  
              spec:             # Especificación del POD
                affinity:
                  podAntiAffinity:
                    requiredDuringSchedulingIgnoredDuringExecution:  -------------------> obligatoriamente rechazara los pods con key: app y values: flask
                    - labelSelector:
                        matchExpressions        
                          - key: app
                            operator: In   
                            values:
                            - flask
                      topologyKey: "kubernetes.io/hostname" 
                  podAffinity:
                    preferredDuringSchedulingIgnoredDuringExecution: ------------------------------> preferiblemente buscara pods con key :app y values:redis
                    - weight: 100
                      podAffinityTerm:
                        labelSelector:
                          matchExpressions:
                          - key: app
                            operator: In
                            values:
                            - redis
                        topologyKey: "kubernetes.io/hostname"
                containers: # Declaración de los contenedores del POD
                - image: leosn/keep-counter:3.0
                  name: flask
                  env:
                  - name: REDIS_PORT -------->buscara el valor de la correspondiente  a la key: redis_port en el configmap creado con el nombre db-configmap 
                    valueFrom:
                      configMapKeyRef:
                        name: db-config
                        key: redis_port  
                  - name: REDIS_HOST -------------->buscara el valor de la key:redis_hot en el configmap creado con el nombre db-configmap
                    valueFrom:
                      configMapKeyRef:
                        name: db-config
                        key: redis_host
                  - name: REDIS_PASSWORD ------------> buscara el valor del secreto en este caso el password para autenticarnos y comunicarnos con redis en el 
                    valueFrom:                         secreto creado con nombre db-secret
                      secretKeyRef:
                        name: db-secret
                        key: password  
                  resources:
                    requests:
                      memory: "128Mi"
                      cpu: "100m"
                    limits:
                      memory: "256Mi"
                      cpu: "200m"
                  livenessProbe:  ---------> ayuda a determinar si  las aplicaciones que se ejecutan detro de los contenedores estan operativas.
                    httpGet:                  De forma predeterminada , los controladores de Kubernetes comprueban si se esta ejecutando un po y, de lo contrario   
                      path: /health/liveness  lo reiniciara de acuerdo con la politica de reinicio del pod.
                      port: 5000
                    initialDelaySeconds: 10
                    periodSeconds: 10
                    timeoutSeconds: 3
                    failureThreshold: 3        
                  readinessProbe: ----------------> permite comprobar si un pod esta listo para recibir el trafico.en el caso de que falle o no se reinicie, dicho 
                    httpGet:                        servicio lo eliminara de su lista de endpoint.
                      path: /health/readiness
                      port: 5000 
                    initialDelaySeconds: 10
                    periodSeconds: 10
                    timeoutSeconds: 3
                    failureThreshold: 3     
                  ports:
                  - containerPort: 5000
                  imagePullPolicy: Always
                  
                  
                 
        
    dep_redis.yaml 
                  
                 
                 apiVersion: apps/v1
                 kind: Deployment
                 metadata:
                   labels:
                     app: redis
                   name: redis-dpl
                 spec:
                   replicas: 1
                   selector:
                     matchLabels:
                       app: redis
                   template:
                     metadata:
                       labels:
                         app: redis
                     spec:
                       containers:
                       - image: redis
                         name: redis
                         args: ["--requirepass", "$(REDIS_PASSWORD)"] ---------> nos permitira inyectar el secreto de la contraseña como una variable de 
                         ports:                                                 entorno por lo que tendremos la autenticacion de contraseña habilitada.
                         - containerPort: 6379
                         env:
                           - name: REDIS_PASSWORD
                             valueFrom:
                               secretKeyRef:
                                 name: db-secret
                                 key: password
                         resources:
                           requests:
                             memory: 128Mi
                             cpu: 100m
                           limits:
                             memory: 256Mi
                             cpu: 200m
                         volumeMounts:
                         - name: data
                           mountPath: /data
                       volumes:
                         - name: data  -----------> volumen que se montara en /data de redis (pvc-redis)
                           persistentVolumeClaim:
                             claimName: pvc-redis
                             
                             
                             
* **Servicios**- Permiten exponer nuestra aplicaciones(pods) dentro del cluster y que otras aplicaciones puedan conectarse a ellas. Hemos utilizado dos ClusterIP, el cual expone la apliaccion en una IP interna cvirtual (VIP) al resto del cluster.  Proporcionando acceso interno.
   
   svc_flask.yaml

                 apiVersion: v1
                 kind: Service
                 metadata:
                   name: flask-svc  ---------> debemos referenciarlo en el ingress
                 spec:
                   type: ClusterIP
                   selector:
                     app: flask
                   ports:
                     - protocol: TCP
                       port: 5000    ----------> debemos referenciarlo en el ingresss
                       targetPort: 5000 -------> puerto donde escucha la aplicacion

  svc_redis.yaml
 
                    
                  apiVersion: v1
                  kind: Service
                  metadata:
                    labels:
                      app: redis
                    name: redis-svc   -------> debemos referenciarlo en el Configmap, para poder comunicarnos con redis.
                  spec:
                    type: ClusterIP
                    selector:
                      app: redis
                    ports:
                    - protocol: TCP
                      port: 6379
                      targetPort: 6379       
                      
  
* **Persistenvoluumeclaim**- Representan solicitudes de storage  , si no hay PVs disponibles el sistema lo autoprovionara de una forma dinamica.

    pvc_redis.yaml

                   apiVersion: v1
                   kind: PersistentVolumeClaim
                   metadata:
                     name: pvc-redis
                     labels:
                       app: redis
                   spec:
                     accessModes:
                       - ReadWriteOnce
                     resources:
                       requests:
                         storage: 8Gi
                         
 
 
* **Configmap**- Utilizados para almacenar datos no confidenciales en formato clave-valor

  configmaps.yaml


                 apiVersion: v1
                 kind: ConfigMap
                 metadata:
                   name: db-config
                 data:
                   redis_host: redis-svc
                   redis_port: "6379"
  
  
* **Secrets**- Similar a los configmaps , pero los usaremos para almacenar y manejar informacion sensible, la  informacion va codificada .
 
  secrets.yaml
         
                apiVersion: v1
                kind: Secret
                metadata:
                  name: db-secret
                type: Opaque
                data:
                  password: MWYyZDFlMmU2N2Rm
                  
 * **hpa**- Realiza un autoescalado basado en memoriay/o CPU, ya que utiliza la memoria y/o CPU para conocer si se debe aumentar o disminuir recursos en base a un valor especificado.
 
   hpa_flask.yaml
 
               piVersion: autoscaling/v1
               kind: HorizontalPodAutoscaler
               metadata:
                 name: flask-hpa
               spec:
                 maxReplicas: 3
                 minReplicas: 1
                 scaleTargetRef:
                   apiVersion: apps/v1
                   kind: Deployment
                   name: flask-deployment
                 targetCPUUtilizationPercentage: 70
                  
* **Ingress**- Para exponer la aplicacion al exterior a traves de un ingress controller
 
  ingress.yaml
 
               apiVersion: networking.k8s.io/v1
               kind: Ingress
               metadata:
                 name: flask-ingress
                 annotations:
                   kubernetes.io/ingress.class: nginx -----> importante indicar la clase
               spec:
                 rules:
                 - host: flask.34-132-94-3.nip.io -------> IP proporcionada por el ingress
                   http:
                     paths:
                     - pathType: ImplementationSpecific
                       path: /
                       backend:
                         service:
                           name: flask-svc
                           port:
                             number: 5000       
  
 Puesto que nuestro cluster de kubernetes es GKE, los pasos para instalarlo son los siguientes:
 
  - En primer lugar, el usuario debe tener permisos en el clúster. Esto se puede hacer con el siguiente comando:
           
            kubectl create clusterrolebinding cluster-admin-binding \
            --clusterrole cluster-admin \
            --user $(gcloud config get-value account)
            
  - Posteriormente, instalaremos el Ingress controller:
  
            kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/controller-v1.2.0/deploy/static/provider/cloud/deploy.yaml
        
        
  Podemos ver que nos ha creado el ingress-controller : 
         
           k get all -n ingress-nginx
           
           NAME                                            READY   STATUS    RESTARTS   AGE
           pod/ingress-nginx-controller-756f546d89-t9fbj   1/1     Running   0          4d1h

           NAME                                         TYPE           CLUSTER-IP    EXTERNAL-IP   PORT(S)                      AGE
           service/ingress-nginx-controller             LoadBalancer   10.8.10.250   34.132.94.3   80:30292/TCP,443:31849/TCP   7d3h
           service/ingress-nginx-controller-admission   ClusterIP      10.8.5.72     <none>        443/TCP                      7d3h

           NAME                                       READY   UP-TO-DATE   AVAILABLE   AGE
           deployment.apps/ingress-nginx-controller   1/1     1            1           7d3h

           NAME                                                  DESIRED   CURRENT   READY   AGE
           replicaset.apps/ingress-nginx-controller-756f546d89   1         1         1       7d3h

           NAME                                       COMPLETIONS   DURATION   AGE
           job.batch/ingress-nginx-admission-create   1/1           3s         7d3h
           job.batch/ingress-nginx-admission-patch    1/1           4s         7d3h

 
  
  Una vez creados todos los manifiestos , los deplegaremos:
  
        kubectl apply -f k8s
       
       configmap/db-config unchanged
        deployment.apps/flask-dpl configured
        deployment.apps/redis-dpl unchanged
        horizontalpodautoscaler.autoscaling/flask-hpa unchanged
        ingress.networking.k8s.io/flask-ingress created
        persistentvolumeclaim/pvc-redis unchanged
        secret/db-secret unchanged
        service/flask-svc unchanged
        service/redis-svc unchanged
 
 Si quisieramos deplegarlos individualemnte:
 
       kubectl apply -f k8s/<nombre del objeto.yaml>
       
       
 Si quisieramos ver todos los recursos desplegados y que se actualicen automaticamente

      watch " kubectl get all" ---------> los datos se actualizaran automaticamente 
      
      kubectl get all
      
      NAME                             READY   STATUS    RESTARTS   AGE
      pod/flask-dpl-69879bf64f-g7lvk   1/1     Running   0          28m
      pod/redis-dpl-6b5f444665-l6vnq   1/1     Running   0          28m

      NAME                 TYPE        CLUSTER-IP   EXTERNAL-IP   PORT(S)    AGE
      service/flask-svc    ClusterIP   10.8.6.243   <none>        5000/TCP   28m
      service/kubernetes   ClusterIP   10.8.0.1     <none>        443/TCP    7d3h
      service/redis-svc    ClusterIP   10.8.5.70    <none>        6379/TCP   28m

      NAME                        READY   UP-TO-DATE   AVAILABLE   AGE
      deployment.apps/flask-dpl   1/1     1            1           28m
      deployment.apps/redis-dpl   1/1     1            1           28m

      NAME                                   DESIRED   CURRENT   READY   AGE
      replicaset.apps/flask-dpl-69879bf64f   1         1         1       28m
      replicaset.apps/redis-dpl-6b5f444665   1         1         1       28m

      NAME                                            REFERENCE                     TARGETS         MINPODS   MAXPODS   REPLICAS   AGE
      horizontalpodautoscaler.autoscaling/flask-hpa   Deployment/flask-deployment   <unknown>/70%   1         3         0          28m
      
Podemos obteneer el ingress mediante:

     kubectl get ingress
    
     NAME            CLASS    HOSTS                      ADDRESS       PORTS   AGE
     flask-ingress   <none>   flask.34-132-94-3.nip.io   34.132.94.3   80      30m
     
           
     kubectl describe ingress flask-ingress
     
     Name:             flask-ingress
     Labels:           <none>
     Namespace:        default
     Address:          34.132.94.3
     Default backend:  default-http-backend:80 (10.4.0.8:8080)
     Rules:
       Host                      Path  Backends
       ----                      ----  --------
       flask.34-132-94-3.nip.io  
                                 /   flask-svc:5000 (10.4.3.31:5000)
     Annotations:                kubernetes.io/ingress.class: nginx
     Events:
       Type    Reason  Age                From                      Message
       ----    ------  ----               ----                      -------
       Normal  Sync    37m (x2 over 38m)  nginx-ingress-controller  Scheduled for sync
       
  
  Para poder ver nuestra aplicacion introduciendo en el navegador -------> flask.34-132-94-3.nip.io 
  
  Podemos borrar los recursos desplegados con el siguiente comando:
  
       kubectl delete -f k8s


# Helm

Helm es un administrador de paquetes de recursos para aplicaciones en Kubernetes. Permite definir, instalar, actualizar y hacer rollback de las aplicaciones desplegadas a través de este gestor. Este administra los recursos que necesita a través de los llamados Charts.

Instalación de Helm 3:

        $ wget
        https://github.com/helm/helm/releases/download/v3.7.2/helm-v3.7.2-darwin-amd64.tar.gz.asc
        $ tar xzvf helm-v3.7.2-darwin-amd64.tar.gz
        $ sudo mv darwin-amd64/helm /usr/local/bin/
        $ helm version
        version.BuildInfo{Version:"v3.7.2", GitCommit:"663a896f4a815053445eec4153677ddc24a0a361",
        GitTreeState:"clean", GoVersion:"go1.16.10"}


Proporcionaamos dos opciones :
  - charts1-------> keep-conter 
  - charts2------> counter

* Charts1:
  
  Nos situaremos en el directorio charts1 ( mkdir charts1 && cd charts1) y ejecutamos el siguiente comando:
  
         helm create keep-counter
  
 Chart1 contendra:
 
         └── keep-counter
             ├── charts
             ├── templates
             │   ├── _helpers.tpl
             |   ├── configmap
             │   ├── flask_deploymen.yaml
             │   ├── flask_service.yaml
             │   ├── hpa.yaml
             │   ├── ingress.yaml
             |   ├── NOTES.txt
             │   ├── redis_deployment.yaml
             │   ├── redis_pvc.yaml
             │   ├── redis_service.yaml.yaml
             │   ├── secret.yaml
             |
             ├──.helmignore   
             ├── Chart.yaml
             └── values.yaml



 Para instalar nuestro chart le tendremos que indicar una release, lo quecutaremos  con el siguiente comando, situados en el directorio raiz:
 
         helm install  prueba1 charts1/kee-counter
         
         
         
 obtendremos:
 
        NAME: prueba1
        LAST DEPLOYED: Fri Apr 23 15:59:58 2022
        NAMESPACE: default
        STATUS: deployed
        REVISION: 1
        TEST SUITE: None
        NOTES:
        GRACIAS POR INSTALAR keep-counter

        Nombre de la release utilizada prueba1

        Para mas detalles puede ejecutar:
           $ helm status prueba1
           $ helm get all prueba1

        Puede desinstalar su release ejecutando:
           $ helm uninstall prueba1

        Get the application URL by running these commands:
          http://flask.34-132-94-3.nip.io/

Para desinstalar nuestra release ejecutamos:

        helm uninstall prueba1
        
        
        
* Charts2:
  
  Nos situaremos en el directorio charts2 ( mkdir charts2 && cd charts2 ) y ejecutamos el siguiente comando:
  
         helm create keep-counter
  
 Chart2 contendra:
 
         └── counter
             ├── charts
             ├── templates
             │   ├── _helpers.tpl
             │   ├── deploymen.yaml
             │   ├── hpa.yaml
             │   ├── ingress.yaml
             |   ├── NOTES.txt
             │   ├── service.yaml.yaml
             │   ├── secret.yaml
             |
             ├──.helmignore
             ├── Chart.lock
             ├── Chart.yaml
             └── values.yaml
             
  Al utilizar dependencias de terceros debemos añadir lo siguien al archivo Chart.yaml
  
        dependencies:
        - name : redis                                                       
         version: 16.0.0                                 
         repository: https://charts.bitnami.com/bitnami
         condition: redis.enabled  

 Añadir el repositorio de helm de bitnami para poder desplegar el chart de redis:
 
       helm repo add bitnami https://charts.bitnami.com/bitnami
       helm repo update
 
 Descargar las dependencias necesarias:
 
       helm dep up charts2/counter

 Para instalar nuestro chart le tendremos que indicar una release, lo quecutaremos  con el siguiente comando, situados en el directorio raiz:
 
         helm install  prueba2 charts2/counter 
         
         
 Obtendremos:
 
      NAME: prueba2
      LAST DEPLOYED: Fri Apr 29 16:26:46 2022
      NAMESPACE: default
      STATUS: deployed
      REVISION: 1
      TEST SUITE: None
      NOTES:
      GRACIAS POR INSTALAR counter

      Nombre de la release utilizada prueba2

      Para mas detalles puede ejecutar:
        $ helm status prueba2
        $ helm get all prueba2

      Puede desinstalar su release ejecutando:
        $ helm uninstall prueba2

      Get the application URL by running these commands:
       http://flask.34-132-94-3.nip.io/

         
        

# Monitoring

Añadir el repositorio de helm prometheus-community para poder desplegar el chart:

      helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
      helm repo update
      
 Posteriormente instalaremos prometheus , con la release prometheus:
 
      helm install prometheus prometheus-community/prometheus

 
 Añadimos el repositorion para desplegar Grafana:
       
       helm repo add grafana https://grafana.github.io/helm-charts
 
 
 Ahora intalaremos Grafana:
 
      helm install grafana grafana/grafana 
      
      
  Obtener contraseña de administrador:

        kubectl get secret --namespace default -o jsonpath="{.data.admin-password}" | base64 --  decode ; echo
        
  obtenemos lo siguiente:
  
          error: error executing jsonpath "{data.admin-password}": Error executing template: unrecognized identifier data. Printing more information for debugging the template:
	template was:
		{data.admin-password}
	object given to jsonpath engine was:
		map[string]interface {}{"apiVersion":"v1", "data":map[string]interface {}{"admin-password":"V3FmQzFMVTlXVXhTRDhIZ2RTa0dueUxPMmZucThRdXFNTkpNRkk0Tw==", "admin-user":"YWRtaW4=", "ldap-toml":""}, "kind":"Secret", "metadata":map[string]interface {}{"annotations":map[string]interface {}{"meta.helm.sh/release-name":"grafana", "meta.helm.sh/release-namespace":"default"}, "creationTimestamp":"2022-04-29T15:37:58Z", "labels":map[string]interface {}{"app.kubernetes.io/instance":"grafana", "app.kubernetes.io/managed-by":"Helm", "app.kubernetes.io/name":"grafana", "app.kubernetes.io/version":"8.5.0", "helm.sh/chart":"grafana-6.28.0"}, "managedFields":[]interface {}{map[string]interface {}{"apiVersion":"v1", "fieldsType":"FieldsV1", "fieldsV1":map[string]interface {}{"f:data":map[string]interface {}{".":map[string]interface {}{}, "f:admin-password":map[string]interface {}{}, "f:admin-user":map[string]interface {}{}, "f:ldap-toml":map[string]interface {}{}}, "f:metadata":map[string]interface {}{"f:annotations":map[string]interface {}{".":map[string]interface {}{}, "f:meta.helm.sh/release-name":map[string]interface {}{}, "f:meta.helm.sh/release-namespace":map[string]interface {}{}}, "f:labels":map[string]interface {}{".":map[string]interface {}{}, "f:app.kubernetes.io/instance":map[string]interface {}{}, "f:app.kubernetes.io/managed-by":map[string]interface {}{}, "f:app.kubernetes.io/name":map[string]interface {}{}, "f:app.kubernetes.io/version":map[string]interface {}{}, "f:helm.sh/chart":map[string]interface {}{}}}, "f:type":map[string]interface {}{}}, "manager":"helm", "operation":"Update", "time":"2022-04-29T15:37:58Z"}}, "name":"grafana", "namespace":"default", "resourceVersion":"4959532", "uid":"cbdc06a4-291a-42a2-9b0d-c10d784aeba9"}, "type":"Opaque"}


puesto que obtenia un error pasamos a decodiificar tanto el username como password manualmente:
     
     
      *password*     
      echo "V3FmQzFMVTlXVXhTRDhIZ2RTa0dueUxPMmZucThRdXFNTkpNRkk0Tw==" | base64 --decode
      
      WqfC1LU9WUxSD8HgdSkGnyLO2fnq8QuqMNJMFI4O
      
      
      *username*
      echo  "YWRtaW4=" | base64 --decode
      
      admin

Nos podemos conectar a Grafana con el siguiente comando:

     kubectl port-fordward svc/grafana 3000:80
     
Nos podemos conectar a Prometheus con el siguiente comando:

      kubectl port-forward svc/prometheus-server 9090:80
      
      
      
 para recoger las metricas en nuestra applicacion hemos utilizado   ---->   Prometheus Flask exporter( https://pypi.org/project/prometheus-flask-exporter/) , para ello hemos añadido a nuestro archivo requirements.txt------>prometheus-flask-exporter
 
 
 Por ultimos  daremos acceso completo al usuario/profesor eedugon.keepcoding@gmail.com con el rol de editor:
 
 	gcloud projects add-iam-policy-binding natural-chiller-347811 --member='user:eedugon.keepcoding@gmail.com' --role='roles/editor'
