# Capa de enlace de datos

- [Capa de enlace de datos](#capa-de-enlace-de-datos)
  - [Capa de enlace de Datos o Data Link Layer](#capa-de-enlace-de-datos-o-data-link-layer)
  - [Colisiones](#colisiones)
  - [Enlaces](#enlaces)

## Capa de enlace de Datos o Data Link Layer

En la unidad de capa de red vimos que la informacion no va de forma directa de host a host, si no que esta debe pasar por varios routers y enlaces durante su camino. En la capa de red asumimos que la informacion simplemente logra viajar a traves de estos enlaces sin mayores problemas. Sin embargo, estos enlaces son **componentes fisicos** reales como **fibras opticas, ondas electromagneticas, cables de cobre, etc.** *Los componentes fisicos tienen limitaciones* y en el caso de enlaces fisicos, algo tan simple como enviar informacion de forma simultanea puede resultar en perdida de datos por colisision de las ondas enviadas a traves del medio fisico. La capa de enlace de datos es la encargada de manejar el envio de datos a traves de estos enlaces.

**La capa de enlace de datos (o capa de datos) tiene como objetivo manejar el envio de datos a traves de enlaces fisicos, considerando que los datos pueden dañarse o destruirse durante el envio debido a colisiones o problemas del medio de envio.**

## Colisiones

Decimos que ocurre **colision** cuando dos o mas entidades en la capa de datos intentan enviar informacion por un mismo enlace al mismo tiempo.

Al enviar informacion por un enlace fisico, tipicamente lo que se hace es enviar la informacion codificada como ondas (electricas o electromagneticas). Luego, si dos entidades envian informacion de forma simultanea a traves de un enlace, efectivamente tenemos ondas emitidas desde distintos origines viajando a traves del mismo medio, al mismo tiempo. Si estas ondas chocan (ocurre colision), la informacion codificada por estas ondas puede dañarse o destruirse, generando perdidas.

## Enlaces

