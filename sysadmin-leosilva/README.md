# sysadmin-leosilva

**Practica sysadmin Leonardo Silva Nevado**

Para la realización de la práctica hemos creado un entorno de integración continua, para ello hemos creado dos maquinas virtuales a traves de Vagrant, un generador de maquinas virtuales, a partir de imagenes previamente construidas, la plataforma donde estarán nuestras maquinas virtuales sera Virtualbox y para configurar las maquinas e instalar los correspondientes softwares utilizaremos Ansible, que automatiza las tareas y despliega de forma sencilla, de modo que pueda replicarse en cualquier maquina remota.

# Pre-requisito
 - Ubuntu 20.04
 - Virtualbox
 - Vagrant
 - Ansible

# Instalación
  ## 1.Construccion de las maquinas virtuales.
        
        vagrant up
        
   Construiremos las maquinas virtuales correspondientes al hostname wordpress y hostname elasticsearch.
   
  ## 2. Aprovisionamiento de las maquinas virtuales:
   2.1 Hostname Wordpress:
        
        ansible-playbook wordpress-provision.yml
   
   Realizaremos la instalación y configuración de una forma automatizada de los componentes correspondientes al hostname wordpress correspondiente a la                vm1(Lvm,Nginx,MariaDB,Wordpress y el Filebeat necesario).
   Si todo se ha realizado correctamente , podremos accedre a la siguiente URL para empezar a configurar Wordpress :http://localhost:8081
   
   2.2 Hostname Elasticsearch:
  
      ansible-playbook elasticsearch-provision.yml
      
   Realizaremos la instalación y configuración de los componentes correspondientes al hostname elasticsearch (Lvm, JDK, Nginx, Logstash, Elasticsearch y Kibana)
   
   Si todo el proceso se ha realizado correctamente podremos acceder  ala interfaz http://localhost:8080  y nos pedira el usuario y el password(situado en .kibana que podra  encontrar en el repositorio correspondiente)     
   
   
   
Para la automatización  la instalación y configuración de las maquinas virtuales a traves de ansible , se han utilizados roles personalizados obtenidos de los repositorios de Github.
Las evidencias de Kibana repecto a los logs los puede encontrar en el repositorio corresppondiente.
         
 
