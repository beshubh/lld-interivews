# ═══════════════════════════════════════════════════════════════════════════
# REQUIREMENTS
#
# Example (Tic Tac Toe):
#   1. Two players alternate placing X and O on a 3x3 grid.
#   2. A player wins by completing a row, column, or diagonal.
#   Out of Scope: UI, AI opponent, networking
# ═══════════════════════════════════════════════════════════════════════════

# REQUIREMENTS
- Inventory management system to track inventory across multiple warehouses.
- Add inventory to the warehouses.
- Remove inventory from warehouses.
- System needs to support transferring inventory b/w warehouses.
- System needs to alert when inventory runs low in some warehouse.
- The system needs to support concurrency.
    - Transfers b/w warehouses needs to be atomic.
    - Opperations like adding, removing also needs to be atomic and support concurrent access.
- Error handling:
    - Inventory of any product cannot go negative.
    - operations like removing inventory and transferring inventory if they result in negative inventory, should be rejected.

Out of scope: UI, Actually sending the alert.


# ═══════════════════════════════════════════════════════════════════════════
# ENTITIES & RELATIONSHIPS
#
# Example (Tic Tac Toe):
#   Game, Board, Player
# ═══════════════════════════════════════════════════════════════════════════
# - InventoryManager, WareHouse, Inventory, AlertStrategy, EmailAlert impl AlertStrategy, SlackAlert impl AlertStrategy


# ═══════════════════════════════════════════════════════════════════════════
# CLASS DESIGN
#
# Example (Tic Tac Toe):
#   class Game:
#     - board: Board
#     - currentPlayer: Player
#     + makeMove(row, col) -> bool
# ═══════════════════════════════════════════════════════════════════════════


class InventoryManager:
    warehouses: dict[str, WareHouse]

    def __init__(self, alert_configs: dict[str, dict]) -> None:
        pass

    def add(self, warehouse_id: str, product_id: str, quantity: int) -> None
        pass
    
    def remove(self, warehouse_id: str, product_id: str, quantity: int) -> None:
        pass
    
    def transfer(
        self, 
        from_warehouse_id: str, 
        to_warehouse_id: str,
        product_id: str,
        quantity: int
    ) -> None:
        pass
    

class WareHouse:
    inventory: dict[str, int]
    alert_configs: dict[str, list[AlertConfig]]

    def __init__(self, alert_configs: dict[str, list[AlertConfig]]) -> None:
        # use alert_configs to create alerts strategies per product
        pass

    def add(self, product_id: str, quantity: int) -> None:
        pass
    
    def remove(self, product_id: str, quantity: int) -> None:
        pass
    
    def set_low_stock_alert(self, product_id: str, threshold: int, listener: AlertListener) -> None:
        pass
    
    def _get_alerts_to_fire(
        self,
        product_id: str,
        old_inventory: int,
        new_inventory: int
    ) -> list[AlertListener]:
        res = []
        for config in self._alert_configs.get(product_id):
            if old_inventory >= config.threshold and new_inventory < config.threshold:
                res.append(config.listener)
        return res


class AlertConfig:
    threshold: int
    listener: AlertListener

    def __init__(self, threshold: int, listener: AlertListener) -> None:
        self._threshold = threshold
        self._listener = listener


class AlertListener(ABC):

    def __init__(self, min_threshold: int) -> None:
        self._min_threshold = min_threshold

    @abstractmethod
    def on_low_stock(self, warehouse_id: str, product_id: str, current_inventory: int) -> None:
        pass


class EmailAlert(IAlertStrategy):

    def on_low_stock(self, warehouse_id: str, product_id: str, current_inventory: int) -> None:
        print('Email: Inventory low')


# ═══════════════════════════════════════════════════════════════════════════
# IMPLEMENTATION
# ═══════════════════════════════════════════════════════════════════════════
import threading
import collections


class InventoryManager:
    warehouses: dict[str, WareHouse]

    def __init__(self, warehouses: dict[str, WareHouse]) -> None:
        self._warehouses = warehouses
        self._warehouse_locks = collections.defaultdict(threading.RLock)

    def add(self, warehouse_id: str, product_id: str, quantity: int) -> None
        pass
    
    def remove(self, warehouse_id: str, product_id: str, quantity: int) -> None:
        warehouse = self._warehouses.get(warehouse_id)
        if not warehouse:
            raise ValueError(f'No such warehouse: {warehouse_id}')
        with self._warehouse_locks[warehouse_id]:
            warehouse.remove(product_id, quantity)
    
    def transfer(
        self, 
        from_warehouse_id: str, 
        to_warehouse_id: str,
        product_id: str,
        quantity: int
    ) -> None:
        assert quantity > 0
        from_warehouse = self._warehouses.get(from_warehouse_id)
        if not from_warehouse:
            raise ValueError(f'From Warehouse not found')
        to_warehouse = self._warehouses.get(to_warehouse_id)
        if not to_warehouse:
            raise ValueError(f'To warehouse not found')
        
        first, second = sorted([from_warehouse_id, to_warehouse_id])
        if first == second:
            raise ValueError('cannot transfer b/w same warehouses')
        with self._warehouse_locks[first]:
            with self._warehouse_locks[second]:
                from_warehouse.remove(product_id, quantity)
                to_warehouse.add(product_id, quantity)

        

class WareHouse:
    id: str
    inventory: dict[str, int]
    alert_configs: dict[str, list[AlertConfig]]

    def __init__(self, inventory: dict[str, int], alert_configs: dict[str, list[AlertConfig]]) -> None:
        # use alert_configs to create alerts strategies per product
        self._product_locks = collections.defaultdict(threading.RLock)
        self._inventory = inventory

    def add(self, product_id: str, quantity: int) -> None:
        pass
    
    def remove(self, product_id: str, quantity: int) -> None:
        with self._product_locks[product_id]:
            if self._inventory.get(product_id, 0) >= quantity:
                old_inventory = self._inventory[product_id]
                self._inventory[product_id] -= quantity
                new_inventory = self._inventory[product_id]
                alerts_to_fire = self._get_alerts_to_fire(product_id, old_inventory, new_inventory)
            else:
                raise ValueError('not enough inventory')
        for listener in alerts_to_fire:
            listener.on_low_stock(self.id, product_id, new_inventory)
    
    def set_low_stock_alert(self, product_id: str, threshold: int, listener: AlertListener) -> None:
        pass
    
    def _get_alerts_to_fire(
        self,
        product_id: str,
        old_inventory: int,
        new_inventory: int
    ) -> list[AlertListener]:
        res = []
        for config in self._alert_configs.get(product_id):
            if old_inventory >= config.threshold and new_inventory < config.threshold:
                res.append(config.listener)
        return res


# ═══════════════════════════════════════════════════════════════════════════
# EXTENSIBILITY
# ═══════════════════════════════════════════════════════════════════════════

   

class WareHouse:
    id: str
    inventory: dict[str, int]
    alert_configs: dict[str, list[AlertConfig]]
    reserved: dict[str, int]
    reservations: dict[str, Reservation]

    def __init__(self, inventory: dict[str, int], alert_configs: dict[str, list[AlertConfig]]) -> None:
        # use alert_configs to create alerts strategies per product
        self._product_locks = collections.defaultdict(threading.RLock)
        self._inventory = inventory

    def add(self, product_id: str, quantity: int) -> None:
        pass

    def reserve(self, reservation_id: str, product_id: str, quantity: int) -> int:
        with self._product_locks[product_id]:
            if self._inventory.get(product_id, 0) < quantity:
                raise ValueError('not enough inventory to reserve')

            old_inventory = self._inventory[product_id]
            self._inventory[product_id] -= quantity
            new_inventory = self._inventory[product_id]
            # whether we want to send alert on reservation depends
            self._reservations[reservation_id] = Reservation(id=reservation_id, product_id=product_id, quantity=quantity)
            self._reserved[product_id] += quantity

    
    def remove(self, product_id: str, quantity: int) -> None:
        with self._product_locks[product_id]:
            if self._inventory.get(product_id, 0) >= quantity:
                old_inventory = self._inventory[product_id]
                self._inventory[product_id] -= quantity
                new_inventory = self._inventory[product_id]
                alerts_to_fire = self._get_alerts_to_fire(product_id, old_inventory, new_inventory)
            else:
                raise ValueError('not enough inventory')
        for listener in alerts_to_fire:
            listener.on_low_stock(self.id, product_id, new_inventory)
    
    def set_low_stock_alert(self, product_id: str, threshold: int, listener: AlertListener) -> None:
        pass
    
    def _get_alerts_to_fire(
        self,
        product_id: str,
        old_inventory: int,
        new_inventory: int
    ) -> list[AlertListener]:
        res = []
        for config in self._alert_configs.get(product_id):
            if old_inventory >= config.threshold and new_inventory < config.threshold:
                res.append(config.listener)
        return res
    
    def cleanup_reservations(self) -> None:
        # background worker to cleanup the expired reservations



class Reservation:
    def __init__(id: str, product_id: str, quantity: int, ttl: int) -> None:
        self._id = id,
        self._product_id = product_id
        self._quantity = quantity
        self._ttl = time.time() + ttl

    