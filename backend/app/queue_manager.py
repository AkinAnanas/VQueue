import uuid
import json
from redis import Redis
from app.queues import PartyInfo, BlockInfo, QueueInfo

def add_party_to_block(rdb: Redis, code: str, party: PartyInfo):
    blocks_key = f"blocks:{code}"
    blocks = rdb.lrange(blocks_key, 0, -1)

    # Try to find an existing block with enough capacity
    for i, block_json in enumerate(blocks):
        try:
            block = json.loads(block_json)
        except (TypeError, json.JSONDecodeError):
            continue  # Skip bad block data
        capacity = block.get("capacity", 10)
        current_size = sum(p["party_size"] for p in block.get("parties", []))

        if current_size + party.party_size <= capacity:
            block["parties"].append(party.to_dict())
            # Update block in Redis
            rdb.lset(blocks_key, i, json.dumps(block))
            return {"phone": party.phone, "block_id": block["block_id"]}

    # No available block found, so create a new one
    block_counter_key = f"queue:{code}:block_counter"
    next_block_id = rdb.incr(block_counter_key)
    new_block_id = f"{code}-{next_block_id}"
    new_block_capacity_key = f"queue:{code}:block_capacity"
    block_capacity = int(rdb.get(new_block_capacity_key) or 10)
    new_block = BlockInfo(block_id=new_block_id, parties=[party.to_dict()], capacity=block_capacity)
    rdb.rpush(blocks_key, json.dumps(new_block))
    return {"party_id": party.party_id, "block_id": new_block_id}

def initialize_queue(rdb: Redis, queue_info: QueueInfo):
    # Start fresh by deleting any possible existing data
    blocks_key = f"blocks:{queue_info.code}"
    rdb.delete(blocks_key)

    # Set the queue variables
    block_counter_key = f"queue:{queue_info.code}:block_counter"
    rdb.set(block_counter_key, 0)
    block_capacity_key = f"queue:{queue_info.code}:block_capacity"
    rdb.set(block_capacity_key, queue_info.block_capacity)
    return {"status": "initialized"}
