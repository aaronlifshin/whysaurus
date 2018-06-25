import React from 'react'

export const CloseLinkX  = () => <span>&#xd7;</span>

export const timeAgoFormatter = (value, unit, suffix, date) => {
  let unitMap = {"second": "s", "minute": "m", "hour": "h", "day": "d", "week": "w", "month": "mo", "year": "y"}
  return <span><span className="number">{value}</span>{unitMap[unit]}</span>
}

export const timeAgoTitle = (date) => {
  let i = date.indexOf("T")
  if (i != -1)
    return date.slice(0, i)
  else
    return date
}
