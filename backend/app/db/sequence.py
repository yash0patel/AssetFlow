from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.shared import EntityCodeSequence

async def get_next_sequence_value(db: AsyncSession, prefix: str) -> str:
    """
    Fetch and increment the next sequence value for a given prefix.
    Uses SELECT ... FOR UPDATE to prevent race conditions.
    """
    stmt = (
        select(EntityCodeSequence)
        .where(EntityCodeSequence.entity_prefix == prefix)
        .with_for_update()
    )
    res = await db.execute(stmt)
    seq = res.scalar_one_or_none()
    
    if not seq:
        seq = EntityCodeSequence(entity_prefix=prefix, current_value=1, padding_length=4)
        db.add(seq)
        await db.flush()
        val = 1
        padding = 4
    else:
        seq.current_value += 1
        await db.flush()
        val = seq.current_value
        padding = seq.padding_length
        
    return f"{prefix}-{str(val).zfill(padding)}"
