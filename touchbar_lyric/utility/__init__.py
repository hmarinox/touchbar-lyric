#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2021-03-01 19:51:54
# @Author  : Chenghao Mou (mouchenghao@gmail.com)

import bisect
from collections import namedtuple
from typing import Optional, List, Tuple

import applescript
from loguru import logger

MediaInformation = namedtuple("MediaInformation", ["name", "artists", "position", "state", "durantion"])

def get_info(app: str) -> Optional[MediaInformation]:
    """Get media information with apple script.

    Parameters
    ----------
    app : str
        The name of the application

    Returns
    -------
    Optional[MediaInformation]
        MediaInformation object

    Examples
    --------
    >>> ans = get_info("Spotify")
    >>> assert ans is None or isinstance(ans, MediaInformation)
    """    

    script: str = """
    on run
        if application "{app}" is running then
            tell application "{app}"
                set currentInfo to {{name of current track, "|", artist of current track, "|", player position, "|", player state, "|", duration of current track}}
            end tell
        else
            set currentInfo to "Empty"
        end if
        return currentInfo
    end run
    """

    r = applescript.run(script)

    logger.debug(r.out)
    
    ans: Optional[MediaInformation] = None
    if r.code == 0 and r.out != "Empty":
        segments = r.out.split(", ")
        ans = MediaInformation(
            segments[0], 
            segments[2], 
            float(segments[4]),
            {"playing": 2, "paused": 1, "stopped": 0}.get(segments[6], 0), 
            float(segments[8]) // 1000 if "." not in segments[8] else float(segments[8])
        )

    logger.debug(ans)

    return ans

def search_intervals(intervals: List[Tuple[float, float]], position: float) -> int: # pragma: no cover
    """Search a timestamp in a list of intervals.

    Parameters
    ----------
    intervals : List[Tuple[float, float]]
        List of intervals
    position : float
        Current timestamp

    Returns
    -------
    int
        Index of the interval

    Examples
    --------
    >>> search_intervals([(0, 12), (12, 15)], 13)
    1
    >>> search_intervals([(0, 12), (12, 15)], 7)
    0
    """
    _, maximums = zip(*intervals)
    idx = bisect.bisect_left(maximums, position)
    if len(intervals) > idx >= 0 and intervals[idx][0] <= position <= intervals[idx][1]:
        return idx
    
    return -1