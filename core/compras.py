class Carrito:
    def __init__(self, request):
        self.request = request
        self.session = request.session
        carrito = self.session.get("carrito")
        if not carrito:
            carrito = self.session["carrito"] = {}
        self.carrito = carrito 
    
    def agregar(self, planta):
        if planta.stock > 0:
            if planta.idPlanta not in self.carrito.keys():
                self.carrito[planta.idPlanta] = {
                    "planta_id": planta.idPlanta,
                    "nombre": planta.nombre,
                    "precio": planta.precio,
                    "cantidad": 1,
                    "total": planta.precio,
                }
            else:
                for key, value in self.carrito.items():
                    if key == planta.idPlanta:
                        if value["cantidad"] < planta.stock:
                            value["cantidad"] += 1
                            value["total"] = value["cantidad"] * planta.precio
                        else:
                            return "No hay suficiente stock para agregar más unidades."
                        break
            self.guardar_carrito()
        else:
            return "Stock insuficiente para el producto."


    def guardar_carrito(self):
        self.session["carrito"] = self.carrito
        self.session.modified = True

    def eliminar(self, planta):
        id = planta.idPlanta
        if id in self.carrito: 
            del self.carrito[id]
            self.guardar_carrito()

    def restar(self, planta):
        for key, value in self.carrito.items():
            if key == planta.idPlanta:
                if value["cantidad"] > 1:  
                    value["cantidad"] -= 1
                    value["total"] = value["cantidad"] * planta.precio
                else:
                    self.eliminar(planta) 
                break
        self.guardar_carrito()
    
    def limpiar(self):
        self.session["carrito"] = {}
        self.session.modified = True

    def total(self):
        return sum(item["total"] for item in self.carrito.values())

    def items(self):
        return self.carrito.values()
