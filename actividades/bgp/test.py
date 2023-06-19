import router

new_router = router.Router()

route = "127.0.0.1 8882 8881 127.0.0.1 8882 100"

new_bgp = router.BGP(new_router)

print("<-------TEST CREACION MENSAJE BGP INICIO Y RUTAS (Item 1)------->")
start_bgp_packet = new_bgp.create_init_BGP_message("127.0.0.1", 8885, 10, 120)
routes_bgp_packet = new_bgp.create_BGP_message(
    'rutas_R1_BGP.txt', "127.0.0.1", 8885, 10, 120)
print(f"----> Mensaje de inicio BGP (START_BGP): {start_bgp_packet}")
print(f"----> Mensaje con rutas BGP (BGP_ROUTES): {routes_bgp_packet}")
print("<--------------------------------------------------------------->")
