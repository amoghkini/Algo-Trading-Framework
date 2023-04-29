class OrderModifyParams:
    def __init__(self):
        self.new_price = 0
        self.new_trigger_price = 0 # Applicable in case of SL order
        self.new_qty = 0
        self.new_order_type = None # Ex: Can change LIMIT order to SL order or vice versa. Not supported by all brokers

    def __str__(self):
        return "new_price=" + str(self.new_price) + ", new_trigger_price=" + str(self.new_trigger_price) \
            + ", new_qty=" + str(self.new_qty) + \
            ", new_order_type=" + str(self.new_order_type)
        