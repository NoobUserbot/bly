from utilities import MHdocker as dckr
import asyncio


async def rollback(recepient: str | int) -> bool:
    """
    Executes switching branches to master and pulling the latest changes for recepient's container.
    :param recepient: Recepient's ID.
    :return: True if the operation was successful, False otherwise.
    """
    try:
        r = dckr.execute(str(recepient), 'git checkout master')
        rr = dckr.execute(str(recepient), 'git pull')
        dckr.stop(str(recepient))
        await asyncio.sleep(1.5)
        dckr.start(str(recepient))
        await asyncio.sleep(0.5)
        dckr.stop(str(recepient))
        await asyncio.sleep(1.5)
        dckr.start(str(recepient))
        await asyncio.sleep(0.5)
        dckr.stop(str(recepient))
        await asyncio.sleep(1.5)
        dckr.start(str(recepient))
        await asyncio.sleep(0.5)
        dckr.start(str(recepient))
        #if r['exit_code'] == 0 and rr['exit_code'] == 0:
        if r[0] == 0 and rr[0] == 0:
            return True
        else:
            return r, rr
    except Exception as e:
        return e
