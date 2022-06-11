# Ciclo de vida de un desarrollo-CICD

### Practica ciclo de vida de un desarrollo CICD
 - Leonardo Silva Nevado

# Pre-requisito
 - Ubuntu 20.04 / Windows10 / MACS OS
 - Docker
 - make
 - Jenkins
 - Una cuenta AWS
 
# Descripción del Proyecto
La empresa Acme, solicita la creacioon totalmente automatizada de unidades de almacenamiento en la nube(en nuestro caso utilizaremos AWS),la cual quiere concretamente dos unidades de almacenamiento, pues tienen dos entornos : dev y prod, por lo que llamaremos  a las unidades respectivamente acme-storage-dev y acme-storage-prod.
Para la realización de dicho proyecto hemos creado un usuario terraform en AWS con su ACCES KEY y SECRET ACCES KEY.

# Procedimiento:

Describiremos el proyecto segun los requerimientos y entregables solicitados.


## Makefile
Los makefile son  ficheros de texto que utiliza **make** para llevar la gestion de la compilacion de programas, define una secuencia de pasos entre las diferentes partes de un proyecto, el cual se ejecuta , con la herramienta de gestion de dependencia Make, cuya funcion consiste en determinar automáticamente que partes de un programa requieren ser recompilada y ejecuta los comandos necesarios para hacerlo.

hemos creado un makefile el cual permite levantar la estructura de los buckets s3 , el cual describe 3 estrategias, aunq esta pensado principalmente para los desarrolladores ya que se ejecuta desde local.

* Los desarrolladores mediante el siguiente comando podran desplegar automaticamente la construccion del recurso aws s3:

       make all-dev
 
 Al ejecutar dicho comando se generara un fichero denominado dev.tfstate, el cual guarda los datos  del recurso que hemos creado con el codigo terraform, al cual se podra dirigir el desarrollador y podra encontrar todos los atributos del recurso generado , a modo de ejemplo lo exponemos a continuacion:
    
        "attributes": {
            "acceleration_status": "",
            "acl": "private",
            "arn": "arn:aws:s3:::acme-storage-dev-leo-4184",
            "bucket": "acme-storage-dev-leo-4184",
            "bucket_domain_name": "acme-storage-dev-kc-4184.s3.amazonaws.com",
            "bucket_prefix": null,
            "bucket_regional_domain_name": "acme-storage-dev-kc-4184.s3.eu-west-1.amazonaws.com",
            "cors_rule": [],
            "force_destroy": false,
            "grant": [],
            "hosted_zone_id": "Z1BKCTXD74EZPE",
            "id": "acme-storage-dev-kc-4184",
            "lifecycle_rule": [],
            "logging": [],
            "object_lock_configuration": [],
            "object_lock_enabled": false,
            "policy": "",
            "region": "eu-west-1",
            "replication_configuration": [],
            "request_payer": "BucketOwner",
            "server_side_encryption_configuration": [],
            "tags": {
              "Name": "storage_s3"
 
En el mismo makefile hemos proporcionado dos estrategias más para levantar ambos recursos a la vez o individualmente, hemos introducido un paso Clean ya que es una buena practica ,para que nos borre la carpeta .terraform entre otras ,proporciono un paso destroy tanto para dev como para prod de forma individual para que en cualquier caso dichos recursos se puedan borrar desde local.
 
 
* Para levantar el recurso acme-storage-prod introduzca el siguiente comando:
       
       make all-prod
       
* para levantar ambos recursos a la vez introduzca el siguiente comando:

       make all
       

## Jenkins
Es un servidor open source para la integracion continua, utilizado para compilar y probar proyectos de forma continua, lo que facilita a los desarrrolladore integrar cambios en un proyecto y entragar nuevas versiones a los usuarios.Escrito en Java, es multiplataforma y es accesible mediante interfaz web (war), enfocada a tareas administrativas.

Mediante el plugin job DSl, el cual es un lenguaje especial para los jobs de jenkins, que nos permitirá estructurar de una forma automatica la estructura de nuestros jobs , en nuestro caso crearemos dos jos , uno que utilizaremos para el despliegue  tanto de acme-storage-dev como acme-storage-prod y el correspondiente job que mediante un tiggers de 10 minutos revisara cada dicho periodo  los bucket evitando que su capacidad de almacenamiento sea igual o superior a 20MiB, en dicho caso los vaciara.

* Primeramente crearemos un proyecto de estilo libre que denominaremos 0.seed mediante el cual generaremos  los dos jobs requeridos  a traves del siguiente **DSL script**:
 
          
        folder('Jobs') {
        description('Deploy and check buckets s3')
             }

         pipelineJob('Jobs/Deploy infrastructure') {
            definition {
                cpsScm {
                    scm {
                        git {
                            remote {
                                url("https://github.com/KeepCodingCloudDevops5/cicd-leosilva.git")
                            }
                            branches("main")
                            scriptPath('Jenkinsfile')
                        }
                    }
                }
            }
         }
         pipelineJob('Jobs/Check buckets s3') {
            definition {
                cpsScm {
                    scm {
                        git {
                            remote {
                                url("https://github.com/KeepCodingCloudDevops5/cicd-leosilva.git")
                            }
                            branches("main")
                            scriptPath('storagecheck.Jenkinsfile')
                        }
                    }
                }
            }
         }
 
 
## Dockerfile

Mediante el correspondiente Dockerfile ,el cual hereda de la imagen base , crearemos el agente Terraform , estos agentes(slaves) permiten distribuir la carga de Jenkins, antes de configurar el agente Terraform en el interface de Jenkins crearemos la imagen que necesitaremos posteriormente  , para la creación de la imagen introduciremos los siguientes comandos:

    docker build -t leosn/terraform-jenkins-agent .
     
    docker push leosn/terraform-jenkins-agent
    
Una vez subida la imagen a Docker hub pasaremos a configurar nuestro agente terrafom , nos iremos a administrar Jenkins ----> Administrar nodos ----> configure cloud ----> Docker agent template, el agente tendra las siguientes caracteristicas:

    Labels: terraform

    Name: terraform
    
    Docker image: leosn/terraform-jenkisn-agent
    
    Remote File System Root: /home/jenkins
    
    usar: Dejar este nodo para ejecutar sólamente tareas vinculadas a él
    
    idle timeout: 10
    
    Metodo de conexion : Connect with SSH  / SSH Key: Use configured SSH credentials  / SSH Credentials: jenkins/Jenkins
    Host Key verification strategy: en nuestro casoNon verifying Verification Strategy
    
    Pull Strategy: Pull all images every time
    
    Pull timeout: 300
    
    
    
## Credenciales

Uno de  los requerimientos solicitados es que las credenciales no se encuentren el el codigo , para lo cual utilizaremos AWS credentials plugin, para la configuración de las credenciales nos dirigimos a Aministrar Jenkins ---> Manage Credentials---->Store scope to Jenkins -----> Add Credentials , detalles :

      Kind : AWS credentials
      Scope: Global(Jenkins,nodes,items,etc)
      Acces Key ID: **************
      Secret Access Key: *****************
      
      
Para que Jenkins pueda interactuar con nuestro repositorio privado tendremos que generar un token personal en github una vez generado lo configuraremos en Jenkins hay varias formas de realizar este paso aunq aqui expondremos una de ellas:    

     *  Vaya a credentials> System> Global credentials> Add credentialsse abrirá una página.
        En el menú desplegable Tipo , seleccione Nombre de usuario y contraseña .

    *   En Usuario,coloque su nomebre de usuario de Github.
     
    *   Agregar Personal Access Tokenen el campo de contraseña.
    
Otra forma es hacerlo de forma individual por cada jobs , a través de su configuracion en la seccion  Pipelines y agregamos la credenciales ,usuario y token.    
    
    
    
## Jenkinsfiles

 ### Jenkinsfile del job de despliegue.
   Se encuentra en el repositorio el cual desplegara en dev y en prod
   
 ### Jenkkinfile  del job de chequeo de almacenamiento (storagecheck.Jenkinsfile)
   Se encuentra en el repositorio, para cumplir este requerimiento se me  han creado ciertas dudas, he generado unos scripts a partir de los comando de aws que se expondran posteriormente , las dudas que se me crean son las siguientes, los nombres de los buckets deben ser unicos , para ello en un principio pensaba en el recurso random que se encuentra en el archivo main.tf , de esta forma podemos crear ilimitados buckets que contengan acme-storage-$$$,  aunque con este recurso no podria cumplir dicho requerimiento , por lo que he decidido fijar los nombres de los buckets en acme-storage-dev-kc y acme-storage-prod-kc(probablemente exista otra forma mas eficiente de hacer esto). Los detalles de los scripts son los siguientes:
   
   
     aws s3 ls s3://<bucket name>  --recursive --human-readable --summarize ---> nos proporciona el contenido del objeto contenido en el bucket
     
     aws s3 rm s3://<bucket name>  --recursive  ---> vacia las unidades de almacenamiento
     
     
     ------------------------------------------ script-----------------------------------------------------------------------------
     
     #!/bin/sh

     size=$(aws s3 ls s3://<bucket name> --recursive --human-readable --summarize | grep "Total Size" | awk '{print $3}')
     # El tamaño obtenido es en MiB

     # Converter string to int
     sizenum= expr $size

     if [ $sizenum => 20 ]; then  # If Result >= 20MiB Clean Bucket
       aws s3 rm s3://<bucket name> --recursive
     fi
     
     
     
## Github action

Es una herramienta que permite reducir la cadena de acciones necesaria para la ejecución de código, mediante la creación de un de flujo de trabajo encargado del Pipeline. Siendo configurable para que GitHub reaccione a ciertos eventos de forma automática según nuestras preferencias.
     
     
### Credentials
En este caso las credenciales las debemos de guardar como secretos dentro de nuestro repositorio particulas de la siguiente manera:

Settings ----> Secrets -----> Actions ----> New repository secrets :

    AWS_ACCESS_KEY_ID    : ******************
    
    AWS_SECRET_ACCES_KEY : ******************
    
    AWS_DEFAULT_REGION   : eu-west-1

    
### Conclusion:
- Con esta propuesta  de proyecto se cumplen todos los requerimientos pero unicamente podriamos desplegar una vez sin borrar los recursos , para poder comprobar los bucket y segun el requerimiento vaciarlos,auneque  no le encuentro mucho sentido ya que cada vez que se realice un push se realizara un despliegue a través de Github action y dará erro si no borramos los recursos.Dicho conflicto se soluciona volviendo a utilizar el recurso random que se encuentra en el archivo main.tf


**Nota**: En la carpeta proyecto-2 puedes encontrar otra porpuesta de Deploy.
