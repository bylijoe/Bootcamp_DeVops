## Observaciones a destacar del Proyecto 2


## Makefile

En esta estrategia usaremos espacios de trabajo, que como diferencia tienen los valores de las variables y el archivo de estado.

hemos creado un makefile el cual permite levantar la estructura de los buckets s3 , el cual describe 3 estrategias, aunq esta pensado principalmente para los desarrolladores ya que se ejecuta desde local.

* Los desarrolladores mediante el siguiente comando podran desplegar automaticamente la construccion del recurso aws s3:

       make all-dev
 
 
* Para levantar el recurso acme-storage-prod introduzca el siguiente comando:
       
       make all-prod
       
* para levantar ambos recursos a la vez introduzca el siguiente comando:

       make all
       

## Jenkins

* He creado otro proyecto de estilo libre el cual he denominado  0.seed1,se que podria haber utilizado el anterior proyecto para que me generara este job pero he decidido hacerlo de manera independiente ya que esta es otra propuesta y no queria introducir el job que realiza la revision de los buckets , el job se genera mediante el siguiente **DSL script**:
 
        pipelineJob('Jobs/Deploy ') {
        definition {
          cpsScm {
            scm {
              git {
                remote {
                  url("https://github.com/KeepCodingCloudDevops5/cicd-leosilva.git")
                }
                branches("main")
                scriptPath('proyecto-2/extra.Jenkinsfile')
              }
            }
          }
        }
      }
