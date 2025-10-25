def get_order_status(order_id: str):
    orders = {"A123": "Delivered", "B456": "In Transit", "C789": "Cancelled"}
    return {"order_id": order_id, "status": orders.get(order_id, "Not Found")}
print(get_order_status("B456"))
