import json


async def key_generate(*args, **kwargs) -> str:
    return f'{args}:{json.dumps({"kwargs": kwargs}, sort_keys=True)}'
