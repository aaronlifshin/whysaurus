import React from 'react'

export const CloseLinkX  = () => <span>&#xd7;</span>

export const timeAgoFormatter = (value, unit, suffix, date) => {
  let unitMap = {"second": "s", "minute": "m", "hour": "h", "day": "d", "week": "w", "month": "mo", "year": "y"}
  return `${value}${unitMap[unit]}`
}

export const timeAgoTitle = (date) => {
  let i = date.indexOf("T")
  if (i != -1)
    return date.slice(0, i)
  else
    return date
}
