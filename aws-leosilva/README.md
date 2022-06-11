# Migración en la nube AWS

### Practica migración en la nube AWS
 - Leonardo Silva Nevado

### Detalles de  acceso al profesor:

- Nombre del rol: kc-revision
- Arn: arn:aws:iam::354962422015:role/kc-revision 

# Pre-requisito
 - Ubuntu 20.04 / Windows10 / MACS OS
 - Disponer de una cuenta en AWS
 - Terraform
 - Requisitos previos de la Practica: OK


# Descripción del Proyecto

* 1 VPC con 4 subnets:
  - 2 privadas para la base de datos
  - 2 públicas para el load balancer y la webapp

* 1 base de datos  MySQL en RDS
* 1 instancia EC2 para servir la webapp
* 1 load balancer para asegurar la distribución de las peticiones en la webapp


# Procedimiento:

## Tipologia de red:

Crearemos una VPC para aislar los recursos que iremos añadiendo más adelante.

Amazon Virtual Private Cloud, nos permite aprovisionar una seccion lógicamente aislada de la nube de AWS donde podemos lanzar recursos de AWS en una red virtual que definiremos, tendremos control total sobre nuestro entorno de red virtual, incluida la selección de nuestro propio rango de direcciones IP, la creación de subredes( en nuestro caso  2 subnets publicas y 2 subnets privadas) y la configuración de tablas de rutas ( 1 tabla de ruta corespondientes a las 2 subnets publicas y 1 tabla de rutas corespondiente a las 2 subnets privadas) y una puerta de enlace de red.

Esta seccción correspondiente a la tipologia de red consta de tres partes , primeramente crearemos una vpc , posteriormente crearemos las 4 subnets y finalmente  las asociaremos a sus correspondientes tablas de rutas, que se diferenciaran en que para que las dos subnets  sean publicas deben tener salida a internet, para ello necesitaremos un internet Gateway .

* Primera parte: Creación de una VPC (importante hemos habilitado las opciones DNS hostnames y DNS resolutio, ya que Amazon RDS lo requiere para disponer la base de datos)

Detalles VPC:

    Name: practik-vpc   /    ID de VPC: vpc-00cb7de36572e0d3    /    CIDR IPv4: 10.0.0.0/16

* Segunda parte: Creación de la subnets

Una subnet es un rango de direcciones IP en nuestra VPC. Podemos lanzar recursos de AWS en una subnets especificas. 

Detalles Subnets publicas:

    Name: pk-public-subnet-1   /    ID de subnet: subnet-0284ffd89c0f490f9     /      CIDR IPv4 10.0.1.0/24     /     Zona de disponibilidad: eu-west-1a

    Name: pk-public-subnet-2    /    ID de subnet: subnet-044cedbac0e23eb41     /      CIDR IPv4 10.0.2.0/24     /     Zona de disponibilidad: eu-west-1b

Detalles Subnets privadas:

    Name: pk-private-subnet-1   /    ID de subnet: subnet-05920a5a7b05c01a4      /     CIDR IPv4 10.0.11.0/24    /      Zona de disponibilidad: eu-west-1a

    Name: pk-private-subnet-2   /    ID de subnet: subnet-01153f660f0220866      /     CIDR IPv4 10.0.12.0/24    /      Zona de disponibilidad: eu-west-1b

* Tercera parte : Ceación de internet Gateway y  de las correspondientes tablas de rutas

 Internet Gateway: Es un componente de VPC de escala  horizontal,redundante y de alta disponibilidad que permite la comunicación entre instancias de una VPC e internet.
 
    Name: practica-igw         /   ID de gateway de Internet: igw-0136de7bc03ef4604
    
 Tablas de rutas: Estas contienen un conjunto de reglas , llamadas rutas, que determinaran hacia donde se dirige el tráfico de red. Cada subnet en una VPC debe estar asociada con una tabla de rutas, que controla el enrutamiento de la subnet. Una subnet solo se puede asociar con una tabla de rutas a la vez, aunque  se puede asociar varias subnets con una misma tabla de rutas , en nuestro caso utilizaremos dos tablas de rutas , una correspondiente a las dos subnets publicas que utilizaremos para el load balancer y la appweb y otra corespondientes para las dos subnets privadas utilizadas para la base de datos.
 
 Detalles tabla de rutas publica ( incluye el correspondiente internet gateway)
 
    Name: pk-public-tr        /    ID de tabla de enrutamiento:  rtb-0eba0200a49c19b16  
 
 Detalles tabla de rutas privada:
    
    Name: pk-private-tr       /   ID de tabla de enrutamiento:   rtb-08a6d2a23faf46980
    
    
## Base de datos ( Amazon RDS )

Lo primero que haremos es crear un Security Group para la base de datos , estos actuan como un firewall virtual para instancias, controlando el trafico entrante y saliente, puestro que para la creacion del grupo de seguridad sera necesario el security group de la instancia EC2 procederemos a la creacion de los tres grupos de seguridad correspondientes a la practica.

### Security Groups

Detalles SG para RDS:

Este security group permitira las peticiones entrantes al puerto  TCP 3306 procedentes de EC2
   
    Name: RDS-sg              /    ID del grupo de seguridad: sg-05dea3e5656ecdf3c 
    
    
Detalles  SG para EC2:

En dicho security group debemos permitir las peticiones entrantes al puerto TCP 8080 procedentes del load balancer , y las salientes al puerto TCP 3306 hacia la base de satos, y el resto del tráfico saliente a internet. esto ultimo es muy importante ya que, de no hacerlo , las instancias no podran descargar la paqueteria de sistemas necesaria ni la webapp.

    Name: EC2-sg           /     ID del grupo de seguridad: sg-03a50b464f4ac0570   
    
Destalles SG para Load Balancer: 

En este security group  permitiremos las peticiones entrantes al puerto TCP 80 procedentes de insternet y las peticiones salientes al puerto TCP 8080 hacia la instancias EC2 que sirven la webapp:

    Nmae: LB-sg           /     ID del grupo de seguridad: sg-55a6c6c0e8be290 
    
  
### Subnet Group 

El Subnet group es necesario para que el RDS se implemente dentro de las subnets que desemos en nuestro caso las dos subnets privadas

### Creación de la Base de datos

Detalles:
 
    Identificador de base de datos: db-mysql  / Punto de enlace: db-mysql.cvt7beystfx1.eu-west-1.rds.amazonaws.com   /  Puerto: 3306
    
    
Creada la instancia, procederemos a guardar los datos de conexion de forma segura en Secret Manager, el cual es un servicio que facilita la rotación ,administración y recuperación de credenciales de bases de datos , claves de API y otros secretos a lo largo de su ciclo de vida.

Detalles :

    Name: rtb-db-secret    /  ARN: arn:aws:secretsmanager:eu-west-1:354962422015:secret:rtb-db-secret-oKsgAE   / Clave de cifrado: DefaultEncryptionKey
    
 Nota: hemos renombrado el secret key dbname por db ,para que concuerde con el codigo de la appweb.
 
 
## Roles

La instancia de EC2 debe acceder a **Secret Manager** para lo cual delegaremos a la isntancia **Rol** con la **Politica de seguridad** correspondiente asociada.

* Crearemos primeramente la politica:

 Policy_Secret_Manager
 
     {
      "Version": "2012-10-17",
      "Statement": [
          {
             "Effect": "Allow",
             "Action": "secretsmanager:GetSecretValue",
             "Resource": "*"
          }
       ]
     }
      
    
* Posteriormente creamos el rol al cual asociaremos con dicha politica
 
      Name: rol-ec2-getsecret 
    
    
## Servidor web

Configuraremos las instancias de EC2 que servirán la webapp.Recursos necesarios para dicha configuracion:

* **key pair** para las instancias- la cual utilizaremos para conectarnos  a la instancia

      Name : Kc-ec2-key.pem
      
  
* **Security Groups**- definidos en los apartados anteriores.

* **Target Group**:

 Detalles:
  
    Name: tg-LB-pk    /   Target type- Instance   /   Protocol : Port   HTTP: 8080  /  Protocol version- HTTP1  /   IP address type- IPv4    /  Load balancer-  pratk-LB 
    
    Health checks
    
    Protocol- HTTP    /   Path- /api/utils/healthcheck  /  Success codes- 200
    
    
* **Application Load Balancer**- El cual distribuira automaticamente el trafico de aplicaciones entrantes en varias instancias de Amazon EC2. Nos permite lograr mayores niveles de tolerancia a fallas en nuestras aplicaciones, proporcionandonos sin problemas la cantidad requerida de capacidad de balanceo de carga necesaria para disitribuir el trafico de aplicaciones. 

Crearemos un  balanceador expuesto a internet y que atienda peticiones IPv4 en el puerto HTTP 80, al que sociaremos tanto el segurity group ( LB-sg ) y el target group anteriormente creado (  tg-LB-pk )

 Detalles:

    Name: practik-LB   /  Nombre de DNS- pratk-LB-41910701.eu-west-1.elb.amazonaws.com   /   VPC- vpc-00cb7de36572e0d39 
    
    
    Zonas de disponibilidad- subnet-0284ffd89c0f490f9 - eu-west-1a  |   subnet-044cedbac0e23eb41 - eu-west-1b 
    
* **Launch Template**-

 Detalles:
 
    Name- app-template
 
    ID de AMI- ami-0db188056a6ff81ae  /  Tipo de instancia- t2.micro con Amazon Linux 2     /   Subnet- pk-public-subnet-1  /  Security Group- EC2-sg 
    
    key pair- kc-ec2-key.pem       / Autoasignaccion de la IP Publica- Enable    /   IAM role- rol-ec2-getsecret 
    
    
    **User Data**
    
    #!/bin/bash
    sudo yum update -y
    sudo yum install -y docker
    sudo service docker start
    sudo docker run -d --name rtb -p 8080:8080 vermicida/rtb
    
    
* **Auto Scaling Group**- Un grupo de Auto Scaling contiene una colección de instancias de Amazon EC2 que se tratan como una agrupación lógica a efectos de escalado automático y administración. El cual hemos asociado al Load balancer creado anteriormente  y  hemos configurado una capacidad de 1 instancia como tamaño máximo,minimo y deseado; lo cual nos garantizara una disponibilidad de 1 instancia de la webapp en todo momento.


Configurado los recursos nos conectaremos a la instancia EC2 para corroborar que el container este corriendo y que la instancia EC2 obtiene el secreto:

* Nos conectamos a la instancia EC2 a través del cliente SSH de la siguiente manera:
 
      1. Abra un cliente SSH.
      2.Localice el archivo de clave privada. La clave utilizada para lanzar esta instancia es kc-ec2-keys.pem
      3.Ejecute este comando, si es necesario, para garantizar que la clave no se pueda ver públicamente.
          chmod 400 kc-ec2-keys.pem
      4.Conéctese a la instancia mediante su DNS público:
          ec2-34-248-102-5.eu-west-1.compute.amazonaws.com
      Ejemplo:
          ssh -i "kc-ec2-keys.pem" ec2-user@ec2-34-248-102-5.eu-west-1.compute.amazonaws.com

* Comprobamos que el container esta corriendo y que el servicio esta escuchando en el puerto 8080:
      
      [ec2-user@ip-10-0-1-187 ~]$ sudo docker ps
      CONTAINER ID   IMAGE           COMMAND                  CREATED       STATUS       PORTS                                       NAMES
      7ac8a7d45173   vermicida/rtb   "/bin/sh -c 'gunicor…"   4 hours ago   Up 4 hours   0.0.0.0:8080->8080/tcp, :::8080->8080/tcp   rtb
      
* Comprobamos la obtención del secreto:

      [ec2-user@ip-10-0-1-187 ~]$ aws secretsmanager --output text get-secret-value --secret-id arn:aws:secretsmanager:eu-west-1:354962422015:secret:rtb-db-secret-x1JXSd --query       SecretString --region eu-west-1  
      {
        "username": "admin",
        "password": "practica",
        "engine": "mysql",
        "host": "db-mysql.cvt7beystfx1.eu-west-1.rds.amazonaws.com",
        "port": 3306,
        "db": "Remember",
        "dbInstanceIdentifier": "db-mysql"
      }


Finalmente hemos verificado que el DNS del load balancer corresponde con la webapp- Remember The Bread, puede encontrar la imagen del correcto funcionamiento de la webapp en el correspondiente repositorio.

     DNS- pratk-LB-41910701.eu-west-1.elb.amazonaws.com
     



# BONUS

Despliegue de los componentes como IaaC, con Terraform:


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
