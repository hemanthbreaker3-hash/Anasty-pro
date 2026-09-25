from asyncio import Event

from ... import (
    queued_dl,
    queued_up,
    non_queued_up,
    non_queued_dl,
    queue_dict_lock,
    task_dict,
    task_dict_lock,
    LOGGER,
)
from ...core.config_manager import Config
from ..mirror_leech_utils.gdrive_utils.search import GoogleDriveSearch
from .bot_utils import sync_to_async, get_telegraph_list
from .files_utils import get_base_name
from .links_utils import is_gdrive_id


async def user_has_active_task(user_id, current_mid):
    async with task_dict_lock:
        for mid, task in task_dict.items():
            if mid != current_mid and hasattr(task, "listener") and task.listener.user_id == user_id:
                if task.status() not in ["Queued in download queue", "Queued in upload queue"]:
                    return True
    return False


async def can_start_queued_task(mid):
    async with task_dict_lock:
        task = task_dict.get(mid)
        if task and hasattr(task, "listener") and task.listener.user_dict.get("SEQUENCE", False):
            user_id = task.listener.user_id
            for active_mid, active_task in task_dict.items():
                if active_mid != mid and hasattr(active_task, "listener") and active_task.listener.user_id == user_id:
                    if active_task.status() not in ["Queued in download queue", "Queued in upload queue"]:
                        return False
    return True


async def stop_duplicate_check(listener):
    if (
        listener.is_leech
        or not listener.stop_duplicate
        or listener.same_dir
        or listener.select
        or not is_gdrive_id(listener.up_dest)
    ):
        return False, None

    name = listener.name
    LOGGER.info(f"Checking File/Folder if already in Drive: {name}")

    if listener.compress:
        name = f"{name}.zip"
    elif listener.extract:
        try:
            name = get_base_name(name)
        except:
            name = None

    if name is not None:
        telegraph_content, contents_no = await sync_to_async(
            GoogleDriveSearch(stop_dup=True, no_multi=listener.is_clone).drive_list,
            name,
            listener.up_dest,
            listener.user_id,
        )
        if telegraph_content:
            msg = f"File/Folder is already available in Drive.\nHere are {contents_no} list results:"
            button = await get_telegraph_list(telegraph_content)
            return msg, button

    return False, None


async def check_running_tasks(listener, state="dl"):
    all_limit = Config.QUEUE_ALL
    state_limit = Config.QUEUE_DOWNLOAD if state == "dl" else Config.QUEUE_UPLOAD
    event = None
    is_over_limit = False

    is_sequence = listener.user_dict.get("SEQUENCE", False)
    if is_sequence and await user_has_active_task(listener.user_id, listener.mid):
        is_over_limit = True

    async with queue_dict_lock:
        if state == "up" and listener.mid in non_queued_dl:
            non_queued_dl.remove(listener.mid)
        if (
            not is_over_limit
            and (all_limit or state_limit)
            and not listener.force_run
            and not (listener.force_upload and state == "up")
            and not (listener.force_download and state == "dl")
        ):
            dl_count = len(non_queued_dl)
            up_count = len(non_queued_up)
            t_count = dl_count if state == "dl" else up_count
            is_over_limit = (
                all_limit
                and dl_count + up_count >= all_limit
                and (not state_limit or t_count >= state_limit)
            ) or (state_limit and t_count >= state_limit)

        if is_over_limit:
            event = Event()
            if state == "dl":
                queued_dl[listener.mid] = event
            else:
                queued_up[listener.mid] = event
        else:
            if state == "up":
                non_queued_up.add(listener.mid)
            else:
                non_queued_dl.add(listener.mid)

    return is_over_limit, event


async def start_dl_from_queued(mid: int):
    queued_dl[mid].set()
    del queued_dl[mid]
    non_queued_dl.add(mid)


async def start_up_from_queued(mid: int):
    queued_up[mid].set()
    del queued_up[mid]
    non_queued_up.add(mid)


async def start_from_queued():
    if all_limit := Config.QUEUE_ALL:
        dl_limit = Config.QUEUE_DOWNLOAD
        up_limit = Config.QUEUE_UPLOAD
        async with queue_dict_lock:
            dl = len(non_queued_dl)
            up = len(non_queued_up)
            all_ = dl + up
            if all_ < all_limit:
                f_tasks = all_limit - all_
                if queued_up and (not up_limit or up < up_limit):
                    started = 0
                    for mid in list(queued_up.keys()):
                        if not await can_start_queued_task(mid):
                            continue
                        await start_up_from_queued(mid)
                        f_tasks -= 1
                        started += 1
                        if f_tasks == 0 or (up_limit and started >= up_limit - up):
                            break
                if queued_dl and (not dl_limit or dl < dl_limit) and f_tasks != 0:
                    started = 0
                    for mid in list(queued_dl.keys()):
                        if not await can_start_queued_task(mid):
                            continue
                        await start_dl_from_queued(mid)
                        started += 1
                        if (dl_limit and started >= dl_limit - dl) or started == f_tasks:
                            break
        return

    if up_limit := Config.QUEUE_UPLOAD:
        async with queue_dict_lock:
            up = len(non_queued_up)
            if queued_up and up < up_limit:
                f_tasks = up_limit - up
                started = 0
                for mid in list(queued_up.keys()):
                    if not await can_start_queued_task(mid):
                        continue
                    await start_up_from_queued(mid)
                    started += 1
                    if started == f_tasks:
                        break
    else:
        async with queue_dict_lock:
            if queued_up:
                for mid in list(queued_up.keys()):
                    if not await can_start_queued_task(mid):
                        continue
                    await start_up_from_queued(mid)

    if dl_limit := Config.QUEUE_DOWNLOAD:
        async with queue_dict_lock:
            dl = len(non_queued_dl)
            if queued_dl and dl < dl_limit:
                f_tasks = dl_limit - dl
                started = 0
                for mid in list(queued_dl.keys()):
                    if not await can_start_queued_task(mid):
                        continue
                    await start_dl_from_queued(mid)
                    started += 1
                    if started == f_tasks:
                        break
    else:
        async with queue_dict_lock:
            if queued_dl:
                for mid in list(queued_dl.keys()):
                    if not await can_start_queued_task(mid):
                        continue
                    await start_dl_from_queued(mid)
