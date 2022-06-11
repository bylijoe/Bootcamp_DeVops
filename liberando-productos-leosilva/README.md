# Liberando Productos.

### Práctica liberando productos
  - Leonardo Silva Nevado

# Pre-requisitos
 - Ubuntu 20.04 /windows10 / MACS SO
 - Docker
 - minikube
 - kubectl
 - Helm


## Objetivo

El objetivo es mejorar un proyecto inicial creado previamente para ponerlo en producción, a través de la adicción de una serie de mejoras.

Para la descripción del proyecto nos hemos basado en los laboratorios realizados en clase :

## Descripción del Proyecto 

El proyecto mejorado es un servidor que realiza lo siguiente:

* Utiliza FastAPI para levantar un servidor en el puerto 8081 e implementa inicialmente dos endpoints:

 - http://0.0.0.0:8081: Devuelve en formato JSON como respuesta {"message":"Hello World"} y un status code 200.
 - http://0.0.0.0:8081/health: Devuelve en formato JSON como respuesta {"health": "ok"} y un status code 200.
 - http://0.0.0.0:8081/bye: Devuelve en formato JSON como respuesta {"message": "bye bye goodbye"} y un status code 200.

* Se han implementado tests unitarios para el servidor FastAPI

* Utiliza prometheus-client para arrancar un servidor de métricas en el puerto 8000 y poder registrar métricas, siendo inicialmente las siguientes:

  - Counter('server_requests_total', 'Total number of requests to this webserver'): Contador que se incrementará cada vez que se haga una llamada a alguno de los endpoints implementados por el servidor ( / y /health y /goodbye )
  
  - Counter('healthcheck_requests_total', 'Total number of requests to healthcheck'): Contador que se incrementará cada vez que se haga una llamada al endpoint /health.
  
  - Counter('main_requests_total', 'Total number of requests to main endpoint'): Contador que se incrementará cada vez que se haga una llamada al endpoint /.

  - Counter('bye_requests_total', 'Total number of requests to goodbye endpoint'): Contador que se incrementará cada vez que se haga una llamada al endpoint /bye.


## Software necesario

Es necesario disponer del siguiente software:

- Python en versión 3.8.5 o superior, disponible para los diferentes sistemas operativos en la página oficial de descargas

- virtualenv para poder instalar las librerías necesarias de Python, se puede instalar a través del siguiente comando:
		
		pip3 install virtualenv

- Docker para poder arrancar el servidor implementado a través de un contenedor Docker, es posible descargarlo a través de su página oficial.

# Ejecución de servidor

## Ejecución directa con Python
 
 1.Instalación de un virtualenv, realizarlo sólo en caso de no haberlo realizado previamente:
 		
		pip3 install virtualenv

   I. Obtener la versión actual de Python instalada para crear posteriormente un virtualenv:

		python3 --version

   El comando anterior en mi caso muestra lo siguiente:

		Python 3.8.10
	
  II. Crear el virtualenv en la raíz del directorio para poder instalar las librerías necesarias:
		
		python3.8 -m venv venv
 

2.Activar el virtualenv creado en el directorio venv en el paso anterior:

		source venv/bin/activate


3.Instalar las librerías necesarias de Python, recogidas en el fichero requirements.txt, sólo en caso de no haber realizado este paso previamente. Es posible instalarlas a través del siguiente comando:

		pip3 install -r requirements.txt

4.Ejecución del código para arrancar el servidor:

		python3 src/app.py

5.La ejecución del comando anterior debería mostrar algo como lo siguiente:

	[2022-04-16 09:44:22 +0000] [1] [INFO] Running on http://0.0.0.0:8081 (CTRL + C to quit)

## Ejecución a través de un contenedor Docker

1.Crearemos una imagen Docker con el código necesario para arrancar el servidor la renombraremos y le añadiremos tag:0.0.2:

		docker build -t leosn/fast-api:0.0.2 .

2.Posteriormente la subiremos  a nuestro repositorio  DockerHub

		docker push leosn/fast-api:0.0.2


3.Una vez creada nuestra imagen y subida a nuestro repositorio ,  inicializaremos dicha imagen y la nombraremos como simle-server  mapeando los puertos utilizados por el servidor de FastAPI y el cliente de prometheus:

		docker run --rm -d -p 8000:8000 -p 8081:8081 --name simple-server fast-api:0.0.2 

4.Obtendremos  los logs del contenedor creado en el paso anterior con el siguiente comando:

		docker logs -f simple-server

5La ejecución del comando anterior debería mostrar algo como lo siguiente:

		[2022-04-16 09:44:22 +0000] [1] [INFO] Running on http://0.0.0.0:8081 (CTRL + C to quit)


## Comprobación de endpoints de servidor y métricas

Una vez arrancado el servidor, utilizando cualquier de las formas expuestas en los apartados anteriores, es posible probar las funcionalidades implementadas por el servidor:

* Comprobación de servidor FastAPI, a través de llamadas a los diferentes endpoints, para realizar las peticiones introduciremos en el navegador ----> http://0.0.0.0:8081/docs :

  
 - Realizar una petición al endpoint /

		curl -X 'GET' \
		'http://0.0.0.0:8081/' \
		-H 'accept: application/json'

      Debería devolver la siguiente respuesta:

		{"message":"Hello World"}

 - Realizar una petición al endpoint /health

		curl -X 'GET' \
	        'http://0.0.0.0:8081/health' \
	        -H 'accept: application/json'

      Debería devolver la siguiente respuesta.

		{"health": "ok"}
 
 - Realizar una petición al endpoint /bye

		curl -X 'GET' \
  	       'http://0.0.0.0:8081/goodbye' \
               -H 'accept: application/json'
	
      Debería devolver la siguiente respuesta.

		{"msg":"Bye Bye Goodbye"}

* Comprobación de registro de métricas, si se accede a la URL http://0.0.0.0:8000 se podrán ver todas las métricas con los valores actuales en ese momento :

  - Realizar varias llamadas al endpoint / y ver como el contador utilizado para registrar las llamadas a ese endpoint, main_requests_total ha aumentado, se debería ver algo como lo mostrado a continuación:

		# TYPE main_requests_total counter
		main_requests_total 6.0
  
  - Realizar varias llamadas al endpoint /health y ver como el contador utilizado para registrar las llamadas a ese endpoint, healthcheck_requests_total ha aumentado, se debería ver algo como lo mostrado a continuación:

		# TYPE healthcheck_requests_total counter
		healthcheck_requests_total 31.0    
  
  - Realizar varias llamadas al endpoint /goodbye y ver como el contador utilizado para registrar las llamadas a ese endpoint, goodbye_requests_total ha aumentado, se debería ver algo como lo mostrado a continuación:

		# TYPE bye_requests_total counter
		bye_requests_total 5.0

  - También se ha credo un contador para el número total de llamadas al servidor server_requests_total, por lo que este valor debería ser la suma de los dos anteriores, tal y como se puede ver a continuación:

		# TYPE server_requests_total counter
		server_requests_total 42.0 

  - Una vez comprobada nuestras metricas de los diferentes endpoints procederemos a parar nuestro servidor a traves del siguiente comando:
  		
		 docker stop simple-server
  		
## Tests

Se ha implementado tests unitarios para probar el servidor FastAPI, estos están disponibles en el archivo src/tests/app_test.py.

Es posible ejecutar los tests manualmente de diferentes formas:

  - Ejecución de todos los tests:

		 pytest

  - Ejecución de todos los tests y mostrar cobertura:

	 	 pytest --cov

  - Ejecución de todos los tests y generación de report de cobertura:

		pytest --cov --cov-report=html
  
  - Se puede ya apagar el contenedor de docker con nuestro simple-server ya que en los siguientes pasos seguiremos con Kubernetes utilizando minikube

	        docker stop simple-server
		
   - Una vez terminadas las pruebas correspondientes desactivaremos  virtualenv mediante:
   
   		deactivate
   		

# Monitoring-Autoscaling

##Objetivo
 
 El objetivo de este apartado es la monitorización mediante el stack de Prometheus, utilizando el chart kube-prometheus-stack.


## Software necesario

* minikube
* kubectl
* helm

1.Crearemos un cluster dutilizando minikube:

		minikube start 
	   
	    
2.Añadiremos el repositorio de helm prometheus-community para poder desplegar el chart kube-prometheus-stack:

		helm repo add prometheus-community https://prometheus-community.github.io/helm-charts 
		helm repo update
	

3.Desplegaremos el chart kube-prometheus-stack del repositorio de helm añadido en el paso anterior con los valores configurados en el archivo custom_values_prometheus.yaml en el namespace monitoring:

		helm -n monitoring upgrade --install prometheus prometheus-community/kube-prometheus-stack \
		-f custom_values_prometheus.yaml \
		--create-namespace --wait --version 34.1.1

 * podemos ver lo que esta  creando con el siguiente comando(esta ventana la mantendremos abierta durante los siguientes pasos):
 
		k -n monitoring get po -w
		NAME                                                   READY   STATUS              RESTARTS   AGE
		prometheus-grafana-75898f6f7b-krgn5                    0/3     ContainerCreating   0          9s
		prometheus-kube-prometheus-operator-667548975f-shhfv   0/1     ContainerCreating   0          9s
		prometheus-kube-state-metrics-77698656df-vsqpn         0/1     ContainerCreating   0          9s
		prometheus-prometheus-node-exporter-w54cp              0/1     ContainerCreating   0          9s
		prometheus-prometheus-node-exporter-w54cp              0/1     Running             0          15s
		prometheus-prometheus-node-exporter-w54cp              1/1     Running             0          15s
		prometheus-kube-prometheus-operator-667548975f-shhfv   1/1     Running             0          21s
		alertmanager-prometheus-kube-prometheus-alertmanager-0   0/2     Pending             0          0s
		alertmanager-prometheus-kube-prometheus-alertmanager-0   0/2     Pending             0          0s
		alertmanager-prometheus-kube-prometheus-alertmanager-0   0/2     ContainerCreating   0          1s
		prometheus-prometheus-kube-prometheus-prometheus-0       0/2     Pending             0          0s
		prometheus-prometheus-kube-prometheus-prometheus-0       0/2     Pending             0          0s
		prometheus-prometheus-kube-prometheus-prometheus-0       0/2     Init:0/1            0          0s
		prometheus-kube-state-metrics-77698656df-vsqpn           0/1     Running             0          36s
		prometheus-kube-state-metrics-77698656df-vsqpn           1/1     Running             0          50s


		
4.Añadiremos el repositorio de helm de bitnami para poder desplegar el chart de mongodb empaquetado por esta compañía:

			helm repo add bitnami https://charts.bitnami.com/bitnami 
			helm repo update

Nota: Siempre que realicemos un add ,hay que realizar un update , esto permite que los charts sean recogidos en los indices de los listados

5.Instalaremos metrics-server(que nos permitirá autoescalar) en minikube a través de la activación del addon necesario:

			minikube addons enable metrics-server 


## Despliegue de aplicación fast-api

 Se ha creado un helm chart en la carpeta fastapi para la aplicación fastapi:0.0.2 desarrollada en los anteriores apartados, en la cual se han realizado modificaciones respecto a las versiones anteriores para disponer de métricas mediante prometheus. Para desplegarla es necesario realizar los siguientes pasos:
		

 1. desplegar el helm chart:

			helm install my-app charts/fastapi


2.Abrir una nueva pestaña en la terminal y realizar un port-forward del servicio de Grafana al puerto 3000 de la máquina:

	    		kubectl -n monitoring port-forward svc/prometheus-grafana 3000:80
  

3.Abrir otra pestaña en la terminal y realizar un port-forward del servicio de Prometheus al puerto 9090 de la máquina:

	   		 kubectl -n monitoring port-forward svc/prometheus-kube-prometheus-prometheus 9090:9090

4.Accedemos a nuestra aplicaccion a través de http://localhost:8081/doscs y realizaremos varias peticiones, podemos accer a ella puesto que en el paso 2.II realizamos el port-fordward.

	      		 kubectl  port-forward svc/my-app-fastapi 8081:8081
	 
   * Si hacemos un port-forwardd al puerto 8000, para divisar que hay otro puerto levantado donde se recogen las metricas, ejecutaremos el siguiente comando:
  	
	   	 	kubectl  port-forward  svc/my-app-fastapi  8000:8000	
		 
			# HELP python_gc_objects_collected_total Objects collected during gc
			# TYPE python_gc_objects_collected_total counter
			python_gc_objects_collected_total{generation="0"} 56445.0
			python_gc_objects_collected_total{generation="1"} 10289.0
			python_gc_objects_collected_total{generation="2"} 823.0
			# HELP python_gc_objects_uncollectable_total Uncollectable object found during GC
			# TYPE python_gc_objects_uncollectable_total counter
			python_gc_objects_uncollectable_total{generation="0"} 0.0
			python_gc_objects_uncollectable_total{generation="1"} 0.0
			python_gc_objects_uncollectable_total{generation="2"} 0.0
			# HELP python_gc_collections_total Number of times this generation was collected
			# TYPE python_gc_collections_total counter
			python_gc_collections_total{generation="0"} 190.0
			python_gc_collections_total{generation="1"} 17.0
			python_gc_collections_total{generation="2"} 1.0
			# HELP python_info Python platform information
			# TYPE python_info gauge
			python_info{implementation="CPython",major="3",minor="8",patchlevel="11",version="3.8.11"} 1.0
			# HELP process_virtual_memory_bytes Virtual memory size in bytes.
			# TYPE process_virtual_memory_bytes gauge
			process_virtual_memory_bytes 4.4310528e+07
			# HELP process_resident_memory_bytes Resident memory size in bytes.
			# TYPE process_resident_memory_bytes gauge
			process_resident_memory_bytes 3.8084608e+07
			# HELP process_start_time_seconds Start time of the process since unix epoch in seconds.
			# TYPE process_start_time_seconds gauge
			process_start_time_seconds 1.65140521548e+09
			# HELP process_cpu_seconds_total Total user and system CPU time spent in seconds.
			# TYPE process_cpu_seconds_total counter
			process_cpu_seconds_total 7.82
			# HELP process_open_fds Number of open file descriptors.
			# TYPE process_open_fds gauge
			process_open_fds 10.0
			# HELP process_max_fds Maximum number of open file descriptors.
			# TYPE process_max_fds gauge
			process_max_fds 1.048576e+06
			# HELP server_requests_total Total number of requests to this webserver
			# TYPE server_requests_total counter
			server_requests_total 1233.0
			# HELP server_requests_created Total number of requests to this webserver
			# TYPE server_requests_created gauge
			server_requests_created 1.6514052185333464e+09
			# HELP healthcheck_requests_total Total number of requests to healthcheck
			# TYPE healthcheck_requests_total counter
			healthcheck_requests_total 540.0
			# HELP healthcheck_requests_created Total number of requests to healthcheck
			# TYPE healthcheck_requests_created gauge
			healthcheck_requests_created 1.6514052185333693e+09
			# HELP main_requests_total Total number of requests to main endpoint
			# TYPE main_requests_total counter
			main_requests_total 691.0
			# HELP main_requests_created Total number of requests to main endpoint
			# TYPE main_requests_created gauge
			main_requests_created 1.651405218533383e+09
			# HELP bye_requests_total Total number of requests to bye endpoint
			# TYPE bye_requests_total counter
			bye_requests_total 2.0
			# HELP bye_requests_created Total number of requests to bye endpoint
			# TYPE bye_requests_created gauge
			bye_requests_created 1.6514052185333931e+09

	     

5.Acceder a la dirección http://localhost:3000 del navegador para acceder a Grafana, las credenciales por defecto son admin para el usuario y prom-operator para la contraseña.

6.Acceder a la dirección http://localhost:9090 para acceder al Prometheus, por defecto no se necesita autenticación.

7.Empezar a realizar diferentes peticiones al servidor de fastapi, es posible a través de la URL http://localhost:8081/docs utilizando swagger

8.Acceder al dashboard creado para observar las peticiones al servidor a través de la URL http://localhost:3000/dashboards, seleccionando una vez en ella la opción Import y en el siguiente paso seleccionar Upload JSON File y seleccionar el archivo presente en esta carpeta llamado custom_dashboard.json.

9.Obtener el pod creado en el paso 1 para poder lanzar posteriormente un comando de prueba de extres:

		   export POD_NAME=$(kubectl get pods -l "app.kubernetes.io/name=fastapi,app.kubernetes.io/instance=my-app" -o jsonpath="{.items[0].metadata.name}")     

10.Acceder mediante una shell interactiva al pod obtenido en el paso anterior:

		kubectl exec --stdin --tty $POD_NAME -- /bin/sh

11.Dentro de la shell en la que se ha accedido en el paso anterior instalar y utilizar los siguientes comandos para descargar un proyecto de github que realizará pruebas de extress:

a. Instalar los binarios necesarios en el pod

		apk update && apk add git go

b. Descargar el repositorio de github y acceder a la carpeta de este, donde se realizará la compilación:

		git clone https://github.com/jaeg/NodeWrecker.git 
		cd NodeWrecker 
		go build -o extress main.go
c. Ejecución del binario obtenido de la compilación del paso anterior que realizará una prueba de extress dentro del pod:

		./extress -abuse-memory -escalate -max-duration 10000000
		
12.Se debería recibir una notificación como la siguiente en el canal de Slack configurado:
		
		[FIRING:2] Monitoring Event Notification
		Alert: fastApiConsumingMoreThanRequest - critical
		 Description: Pod my-app-fastapi-f5dcbc944-t8jxl is consuming more than requested
		 Graph: :gráfico_con_tendencia_ascendente: Runbook: <|:cuaderno_de_espiral:>
		 Details:
		  • alertname: fastApiConsumingMoreThanRequest
		  • pod: my-app-fastapi-f5dcbc944-t8jxl
		  • prometheus: monitoring/prometheus-kube-prometheus-prometheus
		  • severity: critical

		 Alert: KubeAggregatedAPIDown - warning
		 Description:
		 Graph: :gráfico_con_tendencia_ascendente: Runbook: :cuaderno_de_espiral:
		 Details:
		  • alertname: KubeAggregatedAPIDown
		  • name: v1beta1.metrics.k8s.io
		  • namespace: default
		  • prometheus: monitoring/prometheus-kube-prometheus-prometheus
		  • severity: warning

	
## GITHUB ACTION

				  └── .github
					 ├── workflows
					 │   ├── cd.yaml
					 |   ├── ci.yaml
					 │   ├── minikube-test.yaml
					 │
					 └── release-drafter.yaml
					 
					 

###  **CI**-**TEST**:
Se ralizaran  los test unitarios , cuando el evento desencadenante se una pull_request abierta reabierta u sincronizada

###  **CD**-**RELEASE**: 
Aqui hemos optado por una pull_request cerrada ,  si se realiza la correspondiente merge,este evento desencadenara la publicacion de la correspondiente release , publiacion del package, ademas  se reportaran los Artifacts tanto de flake8-coverage y paytest-coverage .

###  **Minikube-test**:
Se ha automatizado el despliegue de nuestro charts fastapi en minikube con la instalacion del stack de prometheus.

* Se han creado tres ramas con los nombres **feat/test** , **fix/test** y **fix/permission** ,para hacer las correspondientes pruebas.

* **Documentacion de interes** para la realizacion de  CI & CD:

	https://github.com/release-drafter/release-drafter
	
	https://github.com/actions-ecosystem/action-get-latest-tag
