# Migración en la nube GPC - Leonardo Silva Nevado

**Practica migración en la nube GPC**
 - Leonardo Silva Nevado
 - ID PROYECTO : mod2-gpc

Para la creación de las infraestructuras solicitadas en la practica correspondiente al modulo 2 ( migración-nube-gcp ) se ha utilizado la consola de Google cloud platform  y Google Cloud SDK



# Pre-requisito
 - Ubuntu 20.04 / Windows10 / MACS OS
 - Disponer de una cuenta en Google Cloud Platform
 - terraform

# Descripción del Proyecto
## Parte 1
 Crearemos un proyecto en GPC:
   
    gcloud projects create mod2-gcp
  
  
 Daremos acceso completo al usuario/profesor javioreto@gmail.com con el rol de editor:
   
    gcloud projects add-iam-policy-binding  mod2-gcp --member user:javioreto@gmail.com --role roles/editor
    
 Se ha creado un presupuesto por un importe de 50€ con unos avisos de facturación según distintos porcentajes de gastos :
    
    25% 50% 75% 100%
   
## Parte 2
 Creación de una base de datos MySQL mediante CloudSQL, con la siguiente informacion a destacar:
     
     ID de instancia: mysql-mod2db
     Contraseña: HvPlj97xwBFgJcEf
     Tipo de maquina: Estándar 2 CPU virtual , 7.5 GB (posteriormente se desescalara al minimo establecido)
     Tipo de almacenamiento: SSD / 10 GB
     Copias de seguridad: 12:00-16:00
     
 Para la creación del usuario llamado "alumno" y contraseña "googlecloud", y la creación de las dos bases de datos llamadas "google" y "cloud" , se ejecutará los siguientes  comandos en Mysql (otra forma de crearlos seria mediante la consola de google cloud ) con el sieguiente orden de prioridad:
   
  - Nos conectamos a la base de datos:
       
         gcloud sql connect mysql-mod2db --user=root
    
  - Crearemos las dos correspondientes bases de datos "google " y "cloud":
   
        CREATE DATABASE google;
        CREATE DATABASE cloud;
    
  - Creamos el usuario "alumno y su correspondiente contraseña "googlecloud", y procedemos a darle todos los privilegios en las dos bases de datos creadas anteriormente:
   
        CREATE USER 'alumno'@'%' IDENTIFIED BY 'googlecloud';
        GRANT ALL PRIVILEGES ON google.* TO 'alumno'@'%';
        GRANT ALL PRIVILEGES ON cloud.* TO 'alumno'@'%';
        FLUSH PRIVILEGES;
        exit
   
  Crearemos un segmento de Cloud Storage, para realizar la exportación de la dos bases de datos "google" y "cloud" y posteriormente importación desde dicho segmento:
   
        gsutil mb -c standard -l europe-west3 gs://mideposito-db
    
 Una vez finalizada la exportación, y posterior importación desde dicho fichero, hemos realizado la comprobación de  los logs de auditación para corroborar que la importación se ha realizado satisfactoriamente ( es recomendable antes de realizar una exportación realizar una copia de seguridad ).
 Por último, se ha realizado la  desescalada de la máquina de base de datos a la configuración minima de CPU y RAM ==> Núcleo compartido, 1 CPU virtual y 614,4 MB de RAM.
   
## Parte 3
 Crearemos una imágen personalizada con un servidor Apache instalado,
  
     gcloud compute instances create img-custom --project=mod2-gcp --zone=europe-west3-c --machine-type=f1-micro --network-interface=network-tier=PREMIUM,subnet=default --metadata=startup-script=apt-get\ update\ $'\n'apt-get\ install\ -y\ apache2 --maintenance-policy=MIGRATE --no-service-account --no-scopes --tags=http-server,https-server --create-disk=boot=yes,device-name=img-custom,image=projects/ubuntu-os-cloud/global/images/ubuntu-1804-bionic-v20220118,mode=rw,size=10,type=projects/mod2-gcp/zones/europe-west3-c/diskTypes/pd-standard --no-shielded-secure-boot --shielded-vtpm --shielded-integrity-monitoring --reservation-affinity=any
     
Posteriormente eliminaremos esa imagen  y conservaremos el disco de arranque puesto que en las reglas de eliminación se indico la opción conservar disco de arranque.
Nos desplazamos al apartado de Almacenamiento/imagen y creamos una imagen  con las siguientes caracteristicas a destacar:
 
    Nombre: img-custom-apache
    Origen: Disco
    Dico de origen: img-custom
    
    gcloud compute images create img-custom-apache --project=mod2-gcp --source-disk=img-custom --source-disk-zone=europe-west3-c --storage-location=europe-west3
    
    
 Con la imagen creada anteriormente procedemos a crear la plantilla de instancias con la configuración minima de CPU y RAM:
 
    gcloud compute instance-templates create template-mod2 --project=mod2-gcp --machine-type=f1-micro --network-interface=network=default,network-tier=PREMIUM --metadata=startup-script-url=gs://mideposito-db/startup.sh --maintenance-policy=MIGRATE --no-service-account --no-scopes --tags=http-server --create-disk=auto-delete=yes,boot=yes,device-name=template-mod2,image=projects/mod2-gcp/global/images/img-custom-apache,mode=rw,size=10,type=pd-standard --no-shielded-secure-boot --shielded-vtpm --shielded-integrity-monitoring --reservation-affinity=any
    
    
Crearemos un grupo de instancias de autoescalado basado en consumos de CPU muy bajo para forzar un escalado rapido, configurando el tiempo de enfriamiento oportuno para nuestra imagen y que cuente el grupo con un minimo de 1 instancia y un máximo de 4:

    gcloud beta compute health-checks create tcp verificacion-estado --project=mod2-gcp --port=80 --proxy-header=NONE --no-enable-logging --check-interval=10 --timeout=5 --unhealthy-threshold=2 --healthy-threshold=2
    
    gcloud beta compute instance-groups managed create group-mod2 --project=mod2-gcp --base-instance-name=group-mod2 --size=1 --template=template-mod2 --zones=europe-west3-c,europe-west3-a,europe-west3-b --target-distribution-shape=EVEN --health-check=verificacion-estado --initial-delay=300
    
    gcloud beta compute instance-groups managed set-autoscaling group-mod2 --project=mod2-gcp --region=europe-west3 --cool-down-period=45 --max-num-replicas=4 --min-num-replicas=1 --mode=on --target-cpu-utilization=0.1

Crearemos una máquina virtual independiente en Compute Engine , que en su directorio local tenga un sencillo script para comprobar si funciona el autoescaldado:

    gcloud compute instances create test-autoescalado --project=mod2-gcp --zone=europe-west3-b --machine-type=f1-micro --network-interface=network-tier=PREMIUM,subnet=default --metadata=startup-script=apt-get\ \ update$'\n'apt-get\ install\ -y\ siege$'\n'systemctl\ enable\ siege.service --maintenance-policy=MIGRATE --service-account=567208585448-compute@developer.gserviceaccount.com --scopes=https://www.googleapis.com/auth/devstorage.read_only,https://www.googleapis.com/auth/logging.write,https://www.googleapis.com/auth/monitoring.write,https://www.googleapis.com/auth/servicecontrol,https://www.googleapis.com/auth/service.management.readonly,https://www.googleapis.com/auth/trace.append --tags=http-server,https-server --create-disk=auto-delete=yes,boot=yes,device-name=test-autoescalado,image=projects/ubuntu-os-cloud/global/images/ubuntu-1804-bionic-v20220126,mode=rw,size=10,type=projects/mod2-gcp/zones/europe-west3-b/diskTypes/pd-standard --no-shielded-secure-boot --shielded-vtpm --shielded-integrity-monitoring --reservation-affinity=any
  
En test-autoescalado,hacemos clic en SSh para conectarnos al terminal, una vez dentro para atacar a la ip propia del grupo de instancias ejecutamos el siguiente comando:
 
    siege -c 250 http://35.234.68.35
    
Hemos supervisado dentro del grupo de instancias para obserabar el autoescalado durante la prueba. Posteriormente ejecutaremos  "Ctrl+c" para detener la prueba de carga y saldremos del terminal, posteriormente detendremos la maquina corespondiente.
Volveremos  a supervisar el grupo de instancias para ver el autoescalado y observaremos el proceso de estabilizacion.
Se puede encontrar las imagenes de la supervisón en el apartado infraestructuras y registros del correspondiente repositorio.


## Parte 4

Realizaremos un deploy de la siguiente aplicación en GAE Estándar: 
       
       https://github.com/GoogleCloudPlatform/python-docs-samples/tree/main/appengine/standard/cloudsql
       
Para ello realizaremos el siguiente procedimiento:

Clonaremos el repositorio :
   
      git clone https://github.com/GoogleCloudPlatform/python-docs-samples.git

Nos desplazaremos al directorio de la aplicación:

      cd ./python-docs-samples/appengine/standard/cloudsql/
      
Configuraremos el archivo app.yaml con la configuración generada en la segunda parte, para ello utilizaremos el editor vim:

      vim app.yaml
      
      runtime: python27
      api_version: 1
      threadsafe: yes
      
      handlers:
      - url: /
        script: main.pp
        
      libraries:
      - name: MySQLdb
        version: "latest"
      
      env_variables:
          CLOUDSQL_CONNECTION_NAME: mod2-gcp:europe-west3:mysql-mod2db
          CLOUDSQL_USER: root
          CLOUDSQL_PASSWORD: HvPlj97xwBFgJcEf
          
Procedemos a desplegar a la aplicacion mediante el siguiente comando:

    gcloud app deploy

Una vez subida la app, se comprobara el correcto funcionamiento accediendo a la url de la app,para ello se obtendra la direccion de la aplicacion desplegada anteriormen:

    gcloud app browse

    Did not detect your browser. Go to this link to view your app:
    https://mod2-gcp.ey.r.appspot.com
     
Se volvera a hacer el deploy de la aplicación , pero esta vez no sobre el servicio  "default", sino un servicio nuevo llamado "practica" y personalizada a la "version-1-0-0". para ello modificaremos el archivo app , escribiendo service:practica:

    vim app.yaml
    
    runtime:python27
    api_version: 1
    threadsafe: yes
    service: practica
      
    handlers:
    - url: /
      script: main.pp
        
    libraries:
    - name: MySQLdb
      version: "latest"
      
    env_variables:
        CLOUDSQL_CONNECTION_NAME: mod2-gcp:europe-west3:mysql-mod2db
        CLOUDSQL_USER: root
        CLOUDSQL_PASSWORD: HvPlj97xwBFgJcEf
    
    
  Modificado el archivo desplegaremos la aplicacion  a la versión  "version-1-0-0":
  
     gcloud app deploy -v version-1-0-0
     
  Repetirmos el paso anterior, obteniendo la dirección de la aplicación desplegada y accederemos a la url:
  
    gcloud app browse -s practica
      
    Did not detect your browser. Go to this link to view your app:
    https://practica-dot-mod2-gcp.ey.r.appspot.com
    
      
 Posteriormente, desplegaremos la aplicación a la versión "version-2-0-0":
 
    gcloud app deploy -v version-2-0-0
    
 Una vez subida la segunda versión, se cambiara la distribución del trafico de forma aleatoria al "50%" entre la dos versiones, para ello nos desplazamos a "APP ENGINE" y al directorio de "versiones" y marcamos el servicio  "practica", e indicamos las dos versiones del servicio y hacemos clic en "DISTRIBUIR EL TRAFICO", posteriormente estableceremos la distribución  del trafico de forma "Aleatoria" al "50%" entre las dos versiones, y guardaremos los cambios.
 
 
 
## BONUS

- Se creara una configuaración de Terraform en un unico fichero main.tf.
- Añadiremos a la configuración las instrucciones para que utilice la libreria de Google Cloud.
- Crearemos  una cuenta de servicio y descargaremos el fichero JSON con las credenciales.
- Añadiremos a la configuración  el proyecto, región, zona y credenciales.
- Crearemos los siguientes recursos:
         
       - Nueva red virtual
       - Bucket de almacenamiento en Cloud Storage.
       - Aprovisionar una máquina virtual enlazada con la red virtual creada anteriormente.
       - Reglas de firewalls.
       - Parte dos de la practica "MySQL".

## INSTRUCCIONES:


-  Inicializados el directorio de trabajo  e instalamos las dependencias:
  
       terraform init
       
- Comprobamos que la sintaxis de la configuración es correcta:
 
       terraform validate
       
- Creamos un plan de ejecución para alcanzar el estado deseado de la infraestructura:

       terraform plan

- Ejecutamos toda la configuración y creamos la infraestructrura:

       terraform apply
       
- Finalmente eliminaremos los recursos :

       terraform destroy

