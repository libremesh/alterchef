=====
Notas
=====

TODO
====

# Sacar sugested packages
# [done] Armar una lista de devices con checkboxes y sacar el campo de texto
# [done] Pollear el Profile Detail y mostrar siempre el ultimo success
# Quitar del perfil simple las llaves SSH
# Bug: si desselccionas llaves al editar un perfil guarda mal y pone otra llave (se soluciona con el anterior)
# No preseleccionar las llaves y quitarlas del perfil avanzado
# [done] Enviar email 

Vistas generales
================

* Listado de redes
* Listado de ultimos FWs
* Listado de FW por red
* FW con listado de archivos para descargar (imágenes y paquetes)
* Listado de trabajos en cola

"Modelos"
=========

Usuario
-------

Los usuarios pueden crear redes y perfiles de firmware.

No, se usas passwords directamente.

Red
---

Datos generales de la red, se asocia con un usuario "admin" de la misma.
Podría no ser necesario este modelo y estar "todo junto" en el perfil.

FW profile
----------

Son los datos con los que se construye un tipo de FW.
La idea es que cada red puede tener uno o más perfiles además de haber
perfiles "genericos" para generar firmwares o inicializar un perfil.

* include_packages (lista de paquetes a incluir dentro de la imagen)
* include_files (archivos a incluir dentro de la imágen)
* llaves ssh (un hook para crear el include_file de la llave)
* tienen un README con la descripción del perfil/red

Funcionalidades:

* se generan desde un perfil base que ya tiene include_packages e include_files
* se pueden agregar y/o modificar archivos de include_files
* "previsualizar" el resultado del perfil
* se puede comparar con otro perfil (diff)

Los include_files son templates, esto permite "llenarlos" con datos que uno carga
en el formulario, ej:

#/etc/config/batmesh

config autoconf 'batmesh'
        option force_autoconf '1'

config autoconf 'radio0'
        option public_essid '{{ PUBLIC_ESSID }}'
        option mesh0_essid '{{ MESH0_ESSID }}'
        option mesh0_bssid 'ca:fe:ca:fe:24:01'
        option mesh0_channel '{{ MESH0_CHANNEL|default:1 }}'

##

* read_profile, lee del disco o DB un perfil y lo "carga en memoria" para trabajarlo en formularios web
* write_profile, escribe un perfil de "memoria" a disco

FW
--

Imágen y archivos de paquetes disponibles para un firmware ya compilado. También incluye
la configuración (el perfil) usado para compilarlo.


FW Job
------

Es un FW a realizar.

Básicamente la implementación puede ser crear un archivo .job, con los datos necesarios para el comando make_snapshots,
en un directorio y poner un cron para irlos procesando.
