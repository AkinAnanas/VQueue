import uuid
import json
from redis import Redis
from app.queue_models import PartyInfo, BlockInfo

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
            return {"party_id": party.party_id, "block_id": block["block_id"]}

    # No available block found, so create a new one
    block_counter_key = f"queue:{code}:block_counter"
    next_block_id = rdb.incr(block_counter_key)
    new_block_id = f"{code}-{next_block_id}"
    new_block = BlockInfo(block_id=new_block_id, parties=[party.to_dict()], capacity=10)
    rdb.rpush(blocks_key, json.dumps(new_block))
    return {"party_id": party.party_id, "block_id": new_block_id}
